"""Explicitly configured in-memory bridge, never a workbook or public-file loader."""

import copy
import html
from html.parser import HTMLParser
import importlib.util
import os
from pathlib import Path
import re

from app.preview_protocol import ProtocolError
from app.preview_hosting import application_url, local_origin
from app.preview_public_api import public_parcours_url
from app.preview_publicsnapshot import SOURCE_FIELDS, digest
from app.preview_theme import PARCOURS_CSS, THEME_CSS, THEME_SCRIPT


# Presentation guidance only: these are not execution modes or catalogue fields.
PUBLIC_STEP_TEMPLATES = (
    """Ce gabarit local est neutre : le mode d'exécution n'est pas publié dans la source.

Avec les données et validations nécessaires, testez le livrable sur une situation réelle limitée,
en gardant votre méthode habituelle. Un exemple fictif permet seulement de vérifier la forme :
reportez la comparaison réelle si les données nécessaires manquent.

- [ ] Choisissez une tâche réelle limitée, autorisée et comparable à votre pratique actuelle
- [ ] Relisez puis testez le livrable de l'étape 4 manuellement, sans envoi, publication ni déclenchement automatique
- [ ] Comparez à qualité attendue équivalente : temps habituel et temps total de l'essai, préparation + production + vérification + corrections comprises
- [ ] Notez les erreurs, faits non vérifiés, retouches nécessaires et limites, sans supposer un gain ni un retour sur investissement
- [ ] Décidez : utilisable sur ce périmètre, à ajuster puis retester, ou à arrêter ; notez pourquoi

**C'est fait quand** : la comparaison réelle est documentée et vous avez choisi la suite.
Un test fictif, un essai incomplet ou une case cochée ne prouve pas l'efficacité.
""",
    """Ce gabarit local prépare une réutilisation manuelle ; il ne prescrit aucun mode d'exécution métier.

Si l'essai est utilisable, gardez une recette validée pour la prochaine tâche comparable.
S'il faut ajuster ou arrêter, consignez cette décision au lieu d'installer un usage non validé.

- [ ] Sauvegardez dans un espace autorisé le prompt validé, le format attendu, les sources autorisées, les vérifications et les limites ; aucun nouveau compte nécessaire
- [ ] Désignez une personne responsable de la relecture et, si utile, une suppléante
- [ ] Choisissez la prochaine tâche comparable et les conditions de réutilisation ; recontrôlez les données et le résultat à chaque essai
- [ ] Gardez le lien local de ce parcours tant que la session reste valide et prévoyez un point de décision : garder, ajuster ou arrêter
- [ ] Réutilisez uniquement après validation humaine, sans automatiser aucun envoi, publication ou processus

**C'est fait quand** : une recette validée, un responsable et une prochaine tâche sont définis,
ou l'arrêt est consigné. Cela prépare la réutilisation ; cela ne démontre pas une adoption durable.
""",
)


class PreviewPage(HTMLParser):
    """Adapt only page chrome and the identified textarea, leaving source text escaped."""

    def __init__(self, context: str, source_hash: str, source: dict | None = None):
        super().__init__(convert_charrefs=False)
        self.context, self.source_hash = context, source_hash
        self.source = source or {"source_mode": "SYNTHETIC"}
        self.parts = []
        self.in_context = False
        self.in_style = False
        self.context_count = self.head_count = self.body_count = self.style_count = 0
        self.steps = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link":
            return  # The shared template's fonts must not issue external requests.
        if tag == "style":
            self.in_style = True
            self.style_count += 1
            self.parts.append("<style>" + THEME_CSS + PARCOURS_CSS)
            return
        if tag == "textarea" and attributes.get("id") == "contexte-local":
            self.context_count += 1
            self.in_context = True
            attributes["maxlength"] = "8000"
            attrs_html = "".join(f' {name}="{html.escape(value or "", quote=True)}"'
                                 for name, value in attributes.items())
            # HTML strips the first textarea newline; reserve one so a user's
            # own leading newline is preserved by the browser parser.
            self.parts.append(f"<textarea{attrs_html}>\n" + html.escape(self.context))
            return
        self.parts.append(self.get_starttag_text())
        if tag == "head":
            self.head_count += 1
            self.parts.append("<script>" + THEME_SCRIPT + "</script>")
        if tag == "body":
            self.body_count += 1
            if self.source["source_mode"] == "PUBLIC_PAGES":
                count = f'{self.source["case_count"]:,}'.replace(",", " ")
                banner = (
                    '<strong>PUBLIC_PAGES · PARCOURS DE TEST LOCAL · NON PRODUCTION</strong>'
                    f'<p>{count} cas réels issus des pages déjà publiées v4.6.1. '
                    'Nouveau gabarit local, textes source v4.6.1 conservés sans reformulation.</p>'
                    '<p>Mode d’exécution et déclencheurs typiques : non publiés, donc inconnus. '
                    'Les étapes 5 et 6 sont un choix de présentation neutre, pas une métadonnée métier.</p>'
                    '<p>L’accord donné pour le RAG ne déclenche aucun appel depuis cette page. '
                    'Le contexte reste modifiable ici, sans envoi externe automatique. '
                    'Il rejoint le prompt et ses règles uniquement quand vous cliquez sur Copier ; '
                    'vous choisissez ensuite où le coller.</p>'
                )
            else:
                banner = (
                    '<strong>SYNTHÉTIQUE · NON PRODUCTION — PARCOURS DE TEST LOCAL</strong>'
                    '<p>16 cas fictifs, pas le RAG ni les 1 021 cas v461. '
                    'Les six étapes sont une démonstration, sans déploiement ni envoi automatique.</p>'
                )
            self.parts.append(
                '<aside class="preview-banner" role="note">' + banner +
                '<p>Votre besoin reste un complément modifiable, distinct du texte source.</p>'
                f'<p>Empreinte source SHA-256 : {html.escape(self.source_hash)}</p></aside>'
            )
        if "data-etape" in attributes:
            self.steps.append(attributes["data-etape"])

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "textarea":
            self.in_context = False
        self.parts.append(f"</{tag}>")

    def handle_startendtag(self, tag, attrs):
        if tag != "link":
            self.parts.append(self.get_starttag_text())

    def handle_data(self, data):
        if not self.in_context and not self.in_style:
            self.parts.append(data)

    def handle_entityref(self, name):
        if not self.in_context and not self.in_style:
            self.parts.append(f"&{name};")

    def handle_charref(self, name):
        if not self.in_context and not self.in_style:
            self.parts.append(f"&#{name};")

    def handle_decl(self, decl):
        self.parts.append(f"<!{decl}>")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")

    def result(self):
        if ((self.context_count, self.head_count, self.body_count, self.style_count) != (1, 1, 1, 1)
                or self.steps != ["1", "2", "3", "4", "5", "6"]):
            raise ValueError("The configured template lacks the six steps or unique local context field.")
        return "".join(self.parts)


class ParcoursRenderer:
    def __init__(self, root: str | None, frontend_origin: str, *, app_url: str | None = None,
                 allowed_origins: set[str] | None = None, cloud: bool = False):
        self.root = root or os.environ.get("AVIA_PREVIEW_PARCOURS_ROOT") or os.environ.get("PARCOURS_SOURCE_ROOT")
        self.frontend_origin = frontend_origin
        self.app_url = application_url(app_url or frontend_origin + "/preview",
                                       allowed_origins or {frontend_origin}, cloud=cloud)
        self.generator = None
        self.template = None
        self.step_templates = None

    def _load(self):
        if self.generator is not None:
            return self.generator
        if not self.root:
            raise ProtocolError("parcours_unavailable",
                                "Parcours indisponible : configurez explicitement AVIA_PREVIEW_PARCOURS_ROOT "
                                "ou PARCOURS_SOURCE_ROOT vers le dépôt local du parcours. Aucun remplacement générique.", 503)
        root = Path(self.root)
        if not root.is_absolute() or str(root).startswith("\\\\"):
            raise ProtocolError("parcours_unavailable", "Le parcours exige un chemin local absolu explicite.", 503)
        spec = importlib.util.spec_from_file_location("avia_preview_parcours_generator", root / "pipeline" / "genere.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.generator = module
        return module

    @staticmethod
    def _public_case(transfer: dict) -> dict:
        source, provenance = transfer["source_fields"], transfer["source"]
        invalid = []
        if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
            invalid.append("schéma des seuls champs publiés")
        else:
            lists = {"questions_qualification", "prerequis_donnees", "guardrails"}
            unavailable = {"mode_execution", "declencheurs_typiques"}
            invalid.extend(key for key in SOURCE_FIELDS - lists - unavailable
                           if not isinstance(source[key], str) or not source[key].strip())
            invalid.extend(key for key in lists
                           if not isinstance(source[key], list) or not source[key]
                           or any(not isinstance(item, str) or not item.strip() for item in source[key]))
            invalid.extend(key for key in unavailable if source[key] is not None)
        if (not re.fullmatch(r"UC-\d{3,5}", transfer.get("case_id", ""))
                or provenance.get("catalogue_version") not in {"v4.6.1", "Pages publiées Avoulia v4.6.1"}
                or not isinstance(provenance.get("case_count"), int) or provenance["case_count"] < 1
                or not re.fullmatch(r"[a-f0-9]{64}", provenance.get("catalogue_revision", ""))
                or transfer.get("catalogue_revision", provenance.get("catalogue_revision"))
                != provenance.get("catalogue_revision")):
            invalid.append("identité/version du snapshot public")
        try:
            url = public_parcours_url(transfer.get("source_url"), transfer.get("case_hash"))
            if url != transfer.get("parcours_url"):
                invalid.append("identité du lien source publié")
        except (TypeError, ValueError, ProtocolError):
            invalid.append("URL/hash de la page source publiée")
        if invalid:
            raise ProtocolError("public_parcours_source_invalid",
                                "Parcours local refusé : " + ", ".join(invalid) + ". Aucun champ déduit.", 422)
        # Alias only for the shared template; the transfer and its digest stay untouched.
        return {
            **copy.deepcopy(source), "use_case_id": transfer["case_id"],
            "cas_utilisation": source["title"], "description_cas_utilisation": source["description"],
            "questions": copy.deepcopy(source["questions_qualification"]),
            "prereqs": copy.deepcopy(source["prerequis_donnees"]),
            "guardrails_liste": copy.deepcopy(source["guardrails"]),
            "guardrails": "\n".join(source["guardrails"]),
        }

    def render(self, transfer: dict) -> str:
        mode = transfer.get("source", {}).get("source_mode")
        if mode not in {"SYNTHETIC", "PUBLIC_PAGES"}:
            raise ProtocolError("unsupported_parcours_source",
                                "Parcours local réservé aux sources SYNTHETIC ou PUBLIC_PAGES vérifiées.", 422)
        try:
            source = transfer["source_fields"]
            actual_hash = digest(source)
            if actual_hash != transfer["source_hash"]:
                raise ProtocolError("parcours_source_changed",
                                    "Empreinte source différente du snapshot sélectionné ; rouvrez la fiche actuelle.", 409)
            if mode == "PUBLIC_PAGES":
                case = self._public_case(transfer)
            else:
                case = source["parcours"]
                strings = ("use_case_id", "cas_utilisation", "description_cas_utilisation", "domaine_label",
                           "intention", "secteur", "mode_execution", "effort", "sensibilite_donnees",
                           "guardrails", "premiere_action_48h")
                lists = ("questions", "prereqs", "guardrails_liste")
                if (not transfer["case_id"].startswith("SYN-")
                        or any(not isinstance(case.get(key), str) or not case[key].strip() for key in strings)
                        or any(not isinstance(case.get(key), list)
                               or any(not isinstance(item, str) for item in case[key]) for key in lists)
                        or case["use_case_id"] != transfer["case_id"]
                        or case["cas_utilisation"] != source["title"]
                        or case["description_cas_utilisation"] != source["description"]
                        or case["mode_execution"] not in {"outil", "no_code"}):
                    raise ValueError("Incomplete or inconsistent synthetic parcours source")
            generator = self._load()
            if self.template is None:
                self.template = generator.load_template()
            options = {}
            if mode == "PUBLIC_PAGES":
                options["step_templates"] = PUBLIC_STEP_TEMPLATES
                templates = {}
            else:
                if self.step_templates is None:
                    self.step_templates = {path.stem: path.read_text(encoding="utf-8")
                                           for path in (Path(self.root) / "templates" / "etapes").glob("*.md")}
                templates = self.step_templates
            page = generator.render_page(
                copy.deepcopy(case), transfer["source_hash"], transfer["source"]["catalogue_version"],
                self.template, templates, app_url=self.app_url, **options,
            )
            adapter = PreviewPage(transfer["local_context"]["problem_original"], actual_hash, transfer["source"])
            adapter.feed(page)
            adapter.close()
            return adapter.result()
        except ProtocolError:
            raise
        except ModuleNotFoundError as error:
            raise ProtocolError("parcours_dependency_missing",
                                f"Parcours indisponible : dépendance de rendu manquante ({error.name}). "
                                "Installer les dépendances de validation existantes ; aucun remplacement générique.", 503) from error
        except Exception as error:
            raise ProtocolError("parcours_unavailable",
                                "Parcours indisponible : source incomplète, dépôt inaccessible ou "
                                "gabarit incompatible. Aucun remplacement générique.", 503) from error
