"""Opt-in gateway to the already-published AVIA chat, never a workbook loader.

Only normal chat requests are made. Public menus and returned case fields stay
in bounded process memory. This is not a rebuilt retrieval engine or index.
"""

import hashlib
import json
import re
import threading
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from app.preview_protocol import ProtocolError
from app.preview_repository import Case, Filters, MULTI_SECTOR, Retrieval, canonical_id

PUBLIC_ORIGIN = "https://avoulia-backend.purpleocean-980317d1.francecentral.azurecontainerapps.io"
PUBLIC_CHAT = PUBLIC_ORIGIN + "/api/v1/chat"
OBSERVED_DEPLOYMENT = "ux-20260913-d02ffad"
SECTOR_PROMPT = "Pour mieux cibler mes recommandations, pouvez-vous me dire dans quel secteur"
OBJECTIVE_PROMPT = "Quel est votre objectif principal dans ce domaine ?"
PROBLEM_PROMPT = "Pouvez-vous décrire le problème concret que vous rencontrez actuellement ?"
NO_RESULTS = "Je n'ai pas de cas suffisamment pertinent à vous proposer avec les choix actuels."
PUBLIC_FIELDS = (
    "cas_utilisation", "description_cas_utilisation", "secteur", "effort",
    "prerequis_donnees", "guardrails", "questions_qualification",
    "sensibilite_donnees", "premiere_action_48h", "mode_execution", "declencheurs_typiques",
)


def fail(code="public_contract", message="Réponse publique incompatible ; aucun remplacement par des fixtures."):
    raise ProtocolError(code, message, 502)


def public_parcours_url(value: str, case_hash: str) -> str:
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc != urlsplit(PUBLIC_ORIGIN).netloc
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not re.fullmatch(r"[a-z0-9]{6,64}", case_hash)
            or parsed.path != f"/action-{case_hash}.html"):
        fail("public_parcours", "Lien de parcours publié absent ou non autorisé.")
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PublicChatTransport:
    def __init__(self):
        self.opener = urllib.request.build_opener(NoRedirect())

    def __call__(self, payload):
        request = urllib.request.Request(
            PUBLIC_CHAT, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with self.opener.open(request, timeout=90) as response:
                if response.status != 200 or response.headers.get_content_type() != "application/json":
                    fail()
                data = response.read(1_048_577)
                if len(data) > 1_048_576:
                    fail()
                result = json.loads(data)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            fail("public_unavailable", "API AVIA publique indisponible. Aucun résultat de substitution ; réessayez explicitement.")
        if not isinstance(result, dict):
            fail()
        return result


def menu(response, prefix):
    answer = response.get("answer")
    if (not isinstance(answer, str) or not answer.startswith(prefix)
            or response.get("suggested_case_ids") or response.get("suggested_cases")):
        fail()
    choices = re.findall(r"^([1-9]\d*)\. (.+)$", answer, re.MULTILINE)
    if (not choices or len(choices) > 100
            or [int(n) for n, _ in choices] != list(range(1, len(choices) + 1))
            or len({label for _, label in choices}) != len(choices)):
        fail()
    return [(number, label.rstrip()) for number, label in choices]


class PublicAPIRepository:
    def __init__(self, transport=None):
        self.transport = transport or PublicChatTransport()
        self.lock = threading.RLock()
        self.revision = "public-api-not-initialized"
        self.domains = {}
        self._domain_menu = None
        self._domain_choices = []
        self._domain_numbers = {}
        self._routes = {}
        self._menus = {}
        self._cases = {}
        self.provenance = {
            "source_mode": "PUBLIC_API", "external_consent_required": True,
            "catalogue_version": f"API publiée AVIA — révision observée déclarée {OBSERVED_DEPLOYMENT}",
            "observed_deployment": OBSERVED_DEPLOYMENT,
            "revision_attestation": "Révision déclarée de l'observation ; l'API ne fournit pas de verrou de version du catalogue.",
            "source_url": PUBLIC_CHAT, "case_count": 0, "domain_count": 0,
            "coverage": "Menus publics actuels ; uniquement les cas renvoyés par chaque recherche. Couverture des 1 021 cas non vérifiée.",
            "retrieval_engine": "Nouveau protocole local de qualification + RAG déjà déployé. Aucun correctif du cœur RAG.",
            "candidate_scope": "IDs visibles renvoyés seulement ; candidats internes du RAG non exposés.",
            "orientation_coverage": "Non disponible : aucun index public exhaustif chargé, aucune recherche transversale simulée.",
            "orientation_supported": False,
            "parcours_mode": "Parcours actuel publié, pas le nouveau template local.",
            "privacy": "Après accord, vos besoins et choix sont transmis à l'API AVIA publique et traités par son service existant (journalisation possible). Aucun envoi du contexte au parcours.",
            "metadata_calls": 0, "retrieval_calls": 0, "failed_calls": 0,
        }

    def _call(self, payload, *, retrieval=False):
        self.provenance["retrieval_calls" if retrieval else "metadata_calls"] += 1
        try:
            result = self.transport(payload)
        except ProtocolError:
            self.provenance["failed_calls"] += 1
            raise
        except Exception:
            self.provenance["failed_calls"] += 1
            fail("public_unavailable", "API AVIA publique indisponible ; aucun repli synthétique.")
        if not isinstance(result, dict):
            fail()
        return result

    def ensure_ready(self):
        with self.lock:
            if self._domain_menu is not None:
                return
            response = self._call({"message": "Bonjour", "history": []})
            choices = menu(response, "Dans quel domaine souhaitez-vous agir en priorité ?")
            if len(choices) != 14 or response.get("selected_domain_code") is not None:
                fail()
            self.domains = {canonical_id("domain", label): label for _, label in choices}
            self._domain_numbers = {canonical_id("domain", label): number for number, label in choices}
            self._domain_menu = response["answer"]
            self._domain_choices = choices
            self.revision = hashlib.sha256(json.dumps(
                {"adapter": 1, "observed": OBSERVED_DEPLOYMENT, "domain_menu": choices},
                ensure_ascii=False, sort_keys=True,
            ).encode()).hexdigest()
            self.provenance.update(catalogue_revision=self.revision, domain_count=len(choices))

    def _domain(self, domain, refresh=False):
        if domain not in self.domains:
            fail()
        if domain in self._routes and not refresh:
            return self._routes[domain]
        current_menu = self._call({"message": "Bonjour", "history": []})
        if (menu(current_menu, "Dans quel domaine souhaitez-vous agir en priorité ?") != self._domain_choices
                or current_menu.get("selected_domain_code") is not None):
            fail("public_source_changed", "Les domaines publics ont changé ; redémarrez la préversion.")
        response = self._call({
            "message": self._domain_numbers[domain],
            "history": [{"role": "assistant", "content": current_menu["answer"]}],
        })
        code = response.get("selected_domain_code")
        if (not isinstance(code, str) or not re.fullmatch(r"[a-z_]+", code)
                or response.get("selected_sector") is not None or response.get("selected_intention") is not None):
            fail()
        answer = response.get("answer", "")
        is_sector = answer.startswith(SECTOR_PROMPT)
        choices = menu(response, SECTOR_PROMPT if is_sector else OBJECTIVE_PROMPT)
        route = {"code": code, "sector_question": is_sector, "choices": choices, "answer": answer}
        if domain in self._routes and route != self._routes[domain]:
            fail("public_source_changed", "Le menu public a changé ; redémarrez la préversion pour une nouvelle observation.")
        if any(old["code"] == code for key, old in self._routes.items() if key != domain):
            fail()
        self._routes[domain] = route
        return route

    def sectors(self, domain):
        with self.lock:
            route = self._domain(domain)
            return [label for _, label in route["choices"]] if route["sector_question"] else []

    def _objective_menu(self, domain, sector, refresh=False):
        route = self._domain(domain, refresh)
        key = (domain, sector)
        if route["sector_question"] and sector is None:
            return None
        if key in self._menus and not refresh:
            return self._menus[key]
        if not route["sector_question"]:
            if sector is not None:
                fail()
            result = {"choices": route["choices"], "answer": route["answer"], "sector": None}
        else:
            number = next((n for n, label in route["choices"] if label == sector), None)
            if number is None:
                fail()
            response = self._call({
                "message": number, "history": [{"role": "assistant", "content": route["answer"]}],
                "selected_domain_code": route["code"],
            })
            if (response.get("selected_domain_code") != route["code"]
                    or response.get("selected_sector") != sector or response.get("selected_intention") is not None):
                fail()
            result = {"choices": menu(response, OBJECTIVE_PROMPT), "answer": response["answer"], "sector": sector}
        if key in self._menus and self._menus[key] != result:
            fail("public_source_changed", "Les objectifs publics ont changé ; redémarrez la préversion.")
        self._menus[key] = result
        return result

    def objectives(self, domain, sector):
        with self.lock:
            result = self._objective_menu(domain, sector)
            return [(canonical_id("objective", domain, label), label) for _, label in result["choices"]] if result else []

    def get(self, case_id):
        return self._cases.get(case_id)

    def eligible(self, case, filters):
        return (case.domain == filters.domain and case.objective_id == filters.objective
                and (filters.sector is None or filters.sector in case.sectors or MULTI_SECTOR in case.sectors))

    def search(self, problem: str, filters: Filters):
        with self.lock:
            # Refresh the public route before binding a positional legacy token.
            # If a menu changed, do not reinterpret an already-confirmed choice.
            objective_menu = self._objective_menu(filters.domain, filters.sector, refresh=True)
            if objective_menu is None:
                fail()
            choice = next(((n, label) for n, label in objective_menu["choices"]
                           if canonical_id("objective", filters.domain, label) == filters.objective), None)
            if choice is None:
                fail()
            number, objective = choice
            upstream = {"selected_domain_code": self._routes[filters.domain]["code"],
                        "selected_sector": filters.sector}
            binding = self._call({
                "message": number, "history": [{"role": "assistant", "content": objective_menu["answer"]}],
                **upstream,
            })
            if (any(binding.get(k) != v for k, v in upstream.items())
                    or not isinstance(binding.get("selected_intention"), str)
                    or not binding["selected_intention"]
                    or not binding.get("answer", "").startswith(PROBLEM_PROMPT)
                    or binding.get("suggested_case_ids") or binding.get("suggested_cases")):
                fail()
            upstream["selected_intention"] = binding["selected_intention"]
            response = self._call({"message": problem, "history": [], **upstream}, retrieval=True)
            if any(response.get(k) != v for k, v in upstream.items()):
                fail("public_filter_changed", "Le service public n'a pas conservé les choix confirmés.")
            ids = response.get("suggested_case_ids")
            rows = response.get("suggested_cases") or []
            if (not isinstance(ids, list) or not all(isinstance(key, str) for key in ids)
                    or len(ids) != len(set(ids)) or not isinstance(rows, list) or len(rows) > 20
                    or any(not isinstance(row, dict) for row in rows)
                    or ids != [row.get("id") for row in rows]):
                fail()
            if not ids and not response.get("answer", "").startswith(NO_RESULTS):
                fail("public_non_result", "L'API n'a pas renvoyé une réponse de recherche reconnue ; aucun faux résultat vide.")
            staged = {}
            for row in rows:
                key = row["id"]
                if not re.fullmatch(r"UC-\d{3,5}", key):
                    fail()
                header = row.get("content", "").split(" | ", 6)
                title, description, sector = (row.get(k) for k in (
                    "cas_utilisation", "description_cas_utilisation", "secteur"))
                if (not all(isinstance(v, str) and v.strip() for v in (title, description, sector))
                        or len(header) != 7
                        or header[:3] != [key, upstream["selected_domain_code"], objective]
                        or header[4:6] != [sector, title]):
                    fail("public_case_scope", "Métadonnées publiques insuffisantes ou cas hors des choix confirmés.")
                case_hash, url = row.get("case_hash"), row.get("parcours_url")
                if not isinstance(case_hash, str) or not isinstance(url, str):
                    fail("public_parcours", "Ce cas n'a pas de parcours public vérifiable.")
                public_parcours_url(url, case_hash)
                source = {field: row.get(field) for field in PUBLIC_FIELDS}
                if any(value is not None and not isinstance(value, str) for value in source.values()):
                    fail()
                source.update(title=title, description=description, use_case_id=key,
                              public_domain_code=upstream["selected_domain_code"], intention=objective,
                              case_hash=case_hash, parcours_url=url)
                digest = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                case = Case(key, filters.domain, objective, (sector,), title, description, digest,
                            source, PUBLIC_CHAT, url, case_hash)
                if not self.eligible(case, filters):
                    fail("public_case_scope", "Cas public hors du secteur confirmé ; aucun élargissement silencieux.")
                if key in self._cases and self._cases[key] != case:
                    fail("public_source_changed", "Un cas public a changé ; redémarrez la préversion.")
                staged[key] = case
            if len(self._cases.keys() | staged.keys()) > 1024:
                fail("public_capacity", "Limite du cache public en mémoire atteinte ; redémarrez la préversion.")
            self._cases.update(staged)
            self.provenance["case_count"] = len(self._cases)
            return Retrieval(filters.as_dict(), tuple(ids), tuple(ids), "existing-deployed-rag-returned-cases-only",
                             {"upstream_confirmed": upstream, "query_forwarded_unchanged": True,
                              "candidate_scope": "returned_cases_only", "revision_attested_by_upstream": False})

    def orient(self, problem, filters):
        return Retrieval({"search": "orientation", "sector": filters.sector}, (), (),
                         "public-orientation-unavailable", {"supported": False, "external_calls": 0})
