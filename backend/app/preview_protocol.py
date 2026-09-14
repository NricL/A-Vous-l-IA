"""Server-authoritative qualification v1, isolated from the legacy chat protocol."""

import copy
import hashlib
import json
import re
import threading
import time
import uuid
from dataclasses import dataclass, field

from app.preview_repository import CatalogueRepository, DOMAINS, Filters, canonical_id, normalize

PROTOCOL_VERSION = 1
PROMPTS = {
    "domain": "Dans quel domaine souhaitez-vous avancer ?",
    "sector": "Dans quel secteur exercez-vous ?",
    "objective": "Quel est votre objectif ?",
    "problem": "Quel problème concret souhaitez-vous résoudre ?",
    "results": "Voici les cas trouvés dans votre sélection.",
    "orientation": "Une autre orientation pourrait convenir. Souhaitez-vous la choisir ?",
    "terminal": "Voici la fiche du cas choisi.",
}
DOMAIN_ALIASES = {"marketing": "marketing_visibilite", "rh": "ressources_humaines",
                  "production": "production"}


def option_text(value: str) -> str:
    return " ".join(normalize(value).split())


class ProtocolError(Exception):
    def __init__(self, code: str, message: str, status: int = 409):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


@dataclass
class Session:
    session_id: str
    catalogue_revision: str
    initial_need: str = ""
    problem: str = ""
    revision: int = 0
    phase: str = "domain"
    domain: str | None = None
    sector: str | None = None
    objective: str | None = None
    results: list[str] = field(default_factory=list)
    offers: list[str] = field(default_factory=list)
    selected_case: str | None = None
    main_retrieval: dict | None = None
    orientation_retrieval: dict | None = None
    issued: dict = field(default_factory=dict)
    receipts: dict = field(default_factory=dict)
    updated_at: float = field(default_factory=time.monotonic)


class QualificationService:
    def __init__(self, repository: CatalogueRepository, prompts: dict | None = None,
                 max_sessions: int = 128, ttl_seconds: int = 3600):
        self.repository = repository
        self.prompts = {**PROMPTS, **(prompts or {})}
        self.sessions: dict[str, Session] = {}
        self.lock = threading.RLock()
        self.max_sessions, self.ttl_seconds = max_sessions, ttl_seconds

    @property
    def domains(self):
        return getattr(self.repository, "domains", DOMAINS)

    def _parcours_policy(self):
        return {"PUBLIC_PAGES": "public-neutral-v1", "PUBLIC_API": "published-original",
                "SYNTHETIC": "synthetic-source-mode"}.get(self.repository.provenance["source_mode"], "unavailable")

    def _provenance(self):
        source = copy.deepcopy(self.repository.provenance)
        if source["source_mode"] == "PUBLIC_PAGES":
            source["parcours_mode"] = "Nouveau gabarit local neutre ; textes déjà publiés v4.6.1 inchangés."
        return source

    def create(self, initial_need: str = "") -> dict:
        if not isinstance(initial_need, str) or len(initial_need) > 8000:
            raise ProtocolError("invalid_problem", "Besoin trop long.", 422)
        with self.lock:
            if hasattr(self.repository, "ensure_ready"):
                self.repository.ensure_ready()
            now = time.monotonic()
            self.sessions = {key: value for key, value in self.sessions.items()
                             if now - value.updated_at < self.ttl_seconds}
            if len(self.sessions) >= self.max_sessions:
                raise ProtocolError("capacity", "Trop de sessions locales actives.", 503)
            session = Session(uuid.uuid4().hex, self.repository.revision,
                              initial_need=initial_need, problem=initial_need)
            session.issued = self._snapshot(session)
            self.sessions[session.session_id] = session
            return copy.deepcopy(session.issued)

    def _session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if session is None or time.monotonic() - session.updated_at >= self.ttl_seconds:
            self.sessions.pop(session_id, None)
            raise ProtocolError("expired_session", "Session expirée ; recommencez.", 404)
        return session

    def read(self, session_id: str) -> dict:
        with self.lock:
            return copy.deepcopy(self._session(session_id).issued)

    @staticmethod
    def _useful_problem(problem: str) -> bool:
        stripped = problem.strip().lower().strip(".!?")
        return bool(stripped) and not stripped.isdigit() and stripped not in {
            "oui", "non", "peut-être", "je ne sais pas", "ok", "autre",
        }

    def _filters(self, session: Session) -> Filters:
        if not session.domain or not session.objective:
            raise ProtocolError("incomplete_context", "Confirmez d'abord vos choix.", 422)
        sectors = self.repository.sectors(session.domain)
        if (sectors and session.sector not in sectors) or (not sectors and session.sector is not None):
            raise ProtocolError("invalid_sector", "Le secteur doit être revalidé.")
        if session.objective not in dict(self.repository.objectives(session.domain, session.sector)):
            raise ProtocolError("invalid_objective", "L'objectif doit être revalidé.")
        return Filters(session.domain, session.sector, session.objective)

    def _retrieve(self, session: Session, allow_orientation: bool = True) -> None:
        filters = self._filters(session)
        result = self.repository.search(session.problem, filters)
        if result.filters != filters.as_dict():
            raise ProtocolError("retrieval_contract", "Les filtres de recherche ne correspondent pas.", 502)
        for key in (*result.candidates, *result.results):
            case = self.repository.get(key)
            if not case or not self.repository.eligible(case, filters):
                raise ProtocolError("retrieval_contract", "Un cas sort du périmètre confirmé.", 502)
        if not set(result.results).issubset(result.candidates):
            raise ProtocolError("retrieval_contract", "Résultats absents des candidats.", 502)
        session.main_retrieval = {
            "filters_applied": result.filters, "candidate_ids": list(result.candidates),
            "result_ids": list(result.results), "engine": result.mode,
            "details": copy.deepcopy(result.details),
        }
        session.results = list(dict.fromkeys(result.results))
        session.phase, session.offers, session.selected_case = "results", [], None
        session.orientation_retrieval = None
        if not session.results and allow_orientation:
            self._orient(session)

    def _orient(self, session: Session) -> None:
        filters = self._filters(session)
        result = self.repository.orient(session.problem, filters)
        if not set(result.results).issubset(result.candidates):
            raise ProtocolError("retrieval_contract", "Piste absente des candidats.", 502)
        offers = []
        for key in result.results:
            case = self.repository.get(key)
            if not case or case.domain not in self.domains:
                raise ProtocolError("retrieval_contract", "Piste non issue du catalogue.", 502)
            if case.domain == session.domain and case.objective_id == session.objective:
                continue
            sectors = self.repository.sectors(case.domain)
            # Abstain rather than clear/change a sector to manufacture an offer.
            if session.sector is not None and session.sector not in sectors:
                continue
            if not self.repository.eligible(
                    case, Filters(case.domain, session.sector, case.objective_id)):
                continue
            if case.objective_id not in dict(self.repository.objectives(case.domain, session.sector)):
                continue
            offers.append(key)
        session.offers = list(dict.fromkeys(offers))[:3]
        session.orientation_retrieval = {
            "filters_applied": result.filters, "candidate_ids": list(result.candidates),
            "result_ids": session.offers[:], "engine": result.mode,
            "details": copy.deepcopy(result.details),
        }
        session.phase = "orientation" if session.offers else "results"

    def _clear_results(self, session: Session) -> None:
        session.results, session.offers, session.selected_case = [], [], None
        session.main_retrieval, session.orientation_retrieval = None, None

    def _back_targets(self, session: Session) -> list[str]:
        targets = []
        if session.phase != "domain":
            targets.append("domain")
        if session.domain and self.repository.sectors(session.domain) and session.phase != "sector":
            targets.append("sector")
        if session.domain and (not self.repository.sectors(session.domain) or session.sector):
            if session.phase not in ("domain", "sector", "objective"):
                targets.append("objective")
        if session.objective and session.phase not in ("domain", "sector", "objective", "problem"):
            targets.append("problem")
        if session.phase == "terminal":
            targets.append("results")
        return targets

    def _back(self, session: Session, target: str) -> None:
        if target not in self._back_targets(session):
            raise ProtocolError("invalid_back", "Retour impossible depuis cette étape.", 422)
        if target == "results":
            session.selected_case = None
            session.phase = "results"
            return
        self._clear_results(session)
        if target == "domain":
            session.domain, session.sector, session.objective = None, None, None
        elif target == "sector":
            session.sector, session.objective = None, None
        elif target == "objective":
            session.objective = None
        if target != "problem":
            # A problem entered under discarded choices must not reappear.
            session.problem = session.initial_need
        session.phase = target

    def _resolve_choice(self, session: Session, action: dict) -> str | None:
        if "choice_text" not in action:
            return action.get("choice_id")
        text = action["choice_text"]
        if not isinstance(text, str) or not text.strip() or len(text) > 500:
            raise ProtocolError("unknown_choice", "Saisissez un numéro ou un libellé proposé.", 422)
        text = option_text(text)
        offered = session.issued["question"]["options"]
        number = re.fullmatch(r"([1-9]\d*)(?:\s*[.)\-:]\s*(.+))?", text)
        numbered = None
        if number:
            numbered = next((item["id"] for item in offered
                             if item["number"] == int(number[1])), None)
            if numbered is None:
                raise ProtocolError("unknown_choice", "Ce numéro n'est pas proposé.", 422)
            text = number[2] or ""
        matches = {item["id"] for item in offered if option_text(item["label"]) == text}
        if session.phase == "domain" and text in DOMAIN_ALIASES:
            matches.update(item["id"] for item in offered
                           if item["id"] == DOMAIN_ALIASES[text]
                           or item["label"] == DOMAINS[DOMAIN_ALIASES[text]])
        if text and len(matches) != 1:
            raise ProtocolError("unknown_choice", "Saisissez un seul libellé proposé, sans interprétation.", 422)
        labelled = next(iter(matches), None)
        choice = numbered or labelled
        if (numbered and labelled and numbered != labelled
                or "choice_id" in action and action["choice_id"] != choice):
            raise ProtocolError("conflicting_choice", "Le numéro et le libellé ne désignent pas le même choix.", 422)
        if choice is None:
            raise ProtocolError("unknown_choice", "Choisissez une proposition affichée.", 422)
        return choice

    def _apply(self, session: Session, action: dict) -> None:
        kind = action["action"]
        if kind == "reset":
            session.catalogue_revision = self.repository.revision
            session.initial_need, session.problem = "", ""
            session.domain, session.sector, session.objective = None, None, None
            session.phase = "domain"
            self._clear_results(session)
            return
        if kind == "back":
            self._back(session, action.get("target", ""))
            return
        if kind == "describe" and session.phase == "problem":
            problem = action.get("text", "")
            if not isinstance(problem, str) or len(problem) > 8000 or not self._useful_problem(problem):
                raise ProtocolError("clarify_problem", "Décrivez le problème en quelques mots.", 422)
            session.problem = problem
            self._retrieve(session)
            return
        if kind == "reject" and session.phase == "results" and session.results:
            self._orient(session)
            return
        if kind == "refuse" and session.phase == "orientation":
            session.offers, session.phase = [], "results"
            return
        choice = self._resolve_choice(session, action)
        options = {item["id"]: item for item in session.issued["question"]["options"]}
        if kind not in ("choose", "accept") or choice not in options:
            raise ProtocolError("unknown_choice", "Choisissez une proposition affichée ; aucun choix n'a changé.", 422)
        if kind == "accept" and session.phase == "orientation":
            case = self.repository.get(options[choice]["case_id"])
            if not case or case.case_id not in session.offers:
                raise ProtocolError("stale_offer", "Cette piste n'est plus disponible.")
            session.domain = case.domain
            self._clear_results(session)
            if self.repository.sectors(case.domain) and session.sector is None:
                session.objective, session.phase = None, "sector"
            else:
                session.objective = case.objective_id
                self._retrieve(session, allow_orientation=False)
            return
        if kind != "choose":
            raise ProtocolError("invalid_action", "Action non proposée à cette étape.", 422)
        if session.phase == "domain":
            supplied_need = action.get("initial_need")
            if supplied_need is not None:
                if (not isinstance(supplied_need, str) or len(supplied_need) > 8000
                        or (session.initial_need and supplied_need != session.initial_need)):
                    raise ProtocolError("invalid_initial_need", "Modifiez le besoin à l'étape problème.", 422)
                session.initial_need = session.problem = supplied_need
            session.domain = choice
            session.phase = "sector" if self.repository.sectors(choice) else "objective"
        elif session.phase == "sector":
            session.sector = options[choice]["source_value"]
            session.phase = "objective"
        elif session.phase == "objective":
            session.objective = choice
            if self._useful_problem(session.problem):
                self._retrieve(session)
            else:
                session.phase = "problem"
        elif session.phase == "results":
            case = self.repository.get(choice)
            if not case or choice not in session.results or not self.repository.eligible(case, self._filters(session)):
                raise ProtocolError("invalid_case", "Ce cas ne correspond plus aux choix.")
            session.selected_case, session.phase = choice, "terminal"
        else:
            raise ProtocolError("invalid_action", "Action non proposée à cette étape.", 422)

    def act(self, session_id: str, action: dict) -> dict:
        with self.lock:
            current = self._session(session_id)
            if action.get("protocol_version") != PROTOCOL_VERSION:
                raise ProtocolError("protocol_version", "Version de protocole incompatible.")
            request_id = action.get("request_id")
            if not isinstance(request_id, str) or not 8 <= len(request_id) <= 128:
                raise ProtocolError("request_id", "Identité de requête requise.", 422)
            fingerprint = hashlib.sha256(json.dumps(action, sort_keys=True).encode()).hexdigest()
            receipt = current.receipts.get(request_id)
            if receipt:
                if receipt["fingerprint"] == fingerprint and receipt["revision"] == current.revision:
                    return copy.deepcopy(current.issued)
                raise ProtocolError("duplicate_request", "Cette réponse a déjà été traitée.")
            if (action.get("revision") != current.revision
                    or action.get("question_id") != current.issued["question"]["id"]
                    or action.get("catalogue_revision") != current.catalogue_revision):
                raise ProtocolError("stale_question", "Question périmée ; rechargez l'état courant.")
            if self.repository.revision != current.catalogue_revision and action.get("action") != "reset":
                raise ProtocolError("catalogue_changed", "Le catalogue a changé ; recommencez.")
            if action.get("action") not in current.issued["allowed_actions"]:
                raise ProtocolError("invalid_action", "Action non proposée à cette étape.", 422)
            updated = copy.deepcopy(current)
            self._apply(updated, action)
            updated.revision += 1
            updated.updated_at = time.monotonic()
            updated.issued = self._snapshot(updated)
            updated.receipts[request_id] = {"fingerprint": fingerprint, "revision": updated.revision}
            while len(updated.receipts) > 64:
                del updated.receipts[next(iter(updated.receipts))]
            self.sessions[session_id] = updated
            return copy.deepcopy(updated.issued)

    def _snapshot(self, session: Session) -> dict:
        options, actions = [], ["reset"]
        phase = session.phase
        if phase == "domain":
            options = [{"id": code, "label": label} for code, label in self.domains.items()]
        elif phase == "sector":
            options = [{"id": canonical_id("sector", value), "label": value, "source_value": value}
                       for value in self.repository.sectors(session.domain)]
        elif phase == "objective":
            options = [{"id": code, "label": value} for code, value
                       in self.repository.objectives(session.domain, session.sector)]
        elif phase == "results":
            options = [{"id": key, "label": self.repository.get(key).title} for key in session.results]
            if session.results:
                actions.append("reject")
        elif phase == "orientation":
            options = []
            for key in session.offers:
                case = self.repository.get(key)
                options.append({
                    "id": canonical_id("orientation", case.case_id, case.domain, case.objective_id),
                    "case_id": key, "label": case.title, "domain": case.domain,
                    "domain_label": self.domains[case.domain], "objective_id": case.objective_id,
                    "objective_label": case.objective, "sector": session.sector,
                    "source_sectors": list(case.sectors),
                    "sector_revalidation_required": session.sector is None and bool(self.repository.sectors(case.domain)),
                })
            actions += ["accept", "refuse"]
        if options and phase != "orientation":
            actions.append("choose")
        for number, option in enumerate(options, start=1):
            option["number"] = number
        if phase == "problem":
            actions.append("describe")
        targets = self._back_targets(session)
        if targets:
            actions.append("back")
        prompt = self.prompts[phase]
        if phase == "results" and not session.results:
            prompt = "Aucun cas adapté trouvé dans cette sélection. Vous pouvez corriger vos choix."
        elif phase == "objective" and not options:
            prompt = "Aucun objectif disponible dans cette source pour ces choix."
        objective_label = dict(self.repository.objectives(session.domain, session.sector)).get(session.objective) if session.domain else None
        card = None
        if session.selected_case:
            case = self.repository.get(session.selected_case)
            card = {
                "case_id": case.case_id, "title": case.title, "description": case.description,
                "source_hash": case.source_hash, "case_hash": case.case_hash, "source_url": case.source_url,
                "parcours_url": case.parcours_url,
                "parcours_render_policy": self._parcours_policy(),
                "preview_parcours_url": f"/preview/parcours/{session.session_id}?revision={session.revision}",
                "handoff_url": f"/api/preview/v1/sessions/{session.session_id}/handoff?revision={session.revision}",
            }
        context = {"domain": session.domain, "sector": session.sector, "objective": session.objective}
        question_id = canonical_id("question", session.session_id, str(session.revision),
                                   session.catalogue_revision, phase,
                                   json.dumps(context, sort_keys=True),
                                   json.dumps([item["id"] for item in options]))
        return {
            "protocol_version": PROTOCOL_VERSION, "session_id": session.session_id,
            "revision": session.revision, "catalogue_revision": session.catalogue_revision,
            "phase": phase, "question": {"id": question_id, "phase": phase, "prompt": prompt, "options": options},
            "confirmed": {**context, "domain_label": self.domains.get(session.domain), "objective_label": objective_label},
            "initial_need": session.initial_need, "problem_original": session.problem,
            "allowed_actions": actions, "back_targets": targets, "card": card,
            "diagnostics": {"main": session.main_retrieval, "orientation": session.orientation_retrieval,
                            "source": self._provenance()},
            "warning": ("PRÉVERSION LOCALE — API PUBLIQUE EXTERNE — RAG DÉPLOYÉ EXISTANT"
                        if self.repository.provenance["source_mode"] == "PUBLIC_API"
                        else "PUBLIC_PAGES — RAG LOCAL — MODÈLE AZURE EXISTANT — NON DÉPLOYÉ"
                        if self.repository.provenance["source_mode"] == "PUBLIC_PAGES"
                        else "PRÉVERSION LOCALE — DONNÉES SYNTHÉTIQUES — NON PRODUCTION"),
        }

    def handoff(self, session_id: str, expected_revision: int | None = None) -> dict:
        with self.lock:
            session = self._session(session_id)
            if expected_revision is not None and expected_revision != session.revision:
                raise ProtocolError("stale_handoff", "Ce lien correspond à un ancien choix ; ouvrez le parcours depuis la fiche actuelle.")
            if session.phase != "terminal":
                raise ProtocolError("no_selected_case", "Choisissez d'abord un cas.", 422)
            if session.catalogue_revision != self.repository.revision:
                raise ProtocolError("catalogue_changed", "Le catalogue a changé ; recommencez.")
            case = self.repository.get(session.selected_case)
            selected = session.issued["card"]
            if (case is None or any(getattr(case, key) != selected[key]
                                   for key in ("case_id", "source_hash", "case_hash", "source_url", "parcours_url"))
                    or hashlib.sha256(json.dumps(case.source_fields, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
                    != selected["source_hash"]):
                raise ProtocolError("selected_source_changed",
                                    "La source du cas sélectionné a changé ; recommencez depuis la fiche.", 409)
            return {
                "protocol_version": PROTOCOL_VERSION, "session_id": session_id, "revision": session.revision,
                "catalogue_revision": session.catalogue_revision,
                "case_id": case.case_id, "source_hash": case.source_hash,
                "parcours_render_policy": self._parcours_policy(),
                "case_hash": case.case_hash, "parcours_url": case.parcours_url, "source_url": case.source_url,
                "source_fields": copy.deepcopy(case.source_fields),
                "metadata": {"domain": case.domain, "objective": case.objective, "sectors": list(case.sectors)},
                "source": self._provenance(),
                "local_context": {"initial_need": session.initial_need, "problem_original": session.problem,
                                  "confirmed": session.issued["confirmed"]},
                "context_policy": (
                    "Besoin et choix transmis avec accord à l'API AVIA publique. Ce transfert reste local ; "
                    "aucun contexte dans le lien ni envoyé au parcours."
                    if self.repository.provenance["source_mode"] == "PUBLIC_API"
                    else "Accord limité aux appels RAG : besoin original et champs publiés vers Azure existant. "
                         "Le parcours de test reçoit le contexte localement, distinct des textes source et modifiable "
                         "dans la page ; aucun contexte dans l'URL ni nouvel envoi externe automatique. "
                         "La copie manuelle ajoute le contexte et les règles uniquement sur clic."
                    if self.repository.provenance["source_mode"] == "PUBLIC_PAGES"
                    else "Complément utilisateur local, distinct du contenu source ; aucun envoi externe."),
            }
