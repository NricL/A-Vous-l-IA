#!/usr/bin/env python3
"""
Ajoute un lien "Retour à Avoulia" dans les pages parcours statiques (Axe 3.4).

Contexte : chaque page parcours s'ouvre dans un nouvel onglet servi par le backend. Sans lien
de retour, l'utilisateur est dans un cul-de-sac une fois son quick win en main. Ce script injecte,
de façon IDEMPOTENTE, deux affordances de relance pointant vers l'app Avoulia (le chat) :
  - un lien en haut de page (juste sous l'ouverture de `.page`) ;
  - un rappel en pied de page (avant `</footer>`).

Pourquoi un post-traitement plutôt qu'une régénération : les 1026 pages servies utilisent un
template abouti dont le générateur canonique n'est pas `generate_parcours_pages.py` (celui-ci
produit un template plus ancien). Post-traiter les fichiers SERVIS évite toute régression visuelle.

URL de l'app : variable d'env `AVOULIA_APP_URL` (défaut = front Container App), cohérent avec
l'Axe 4.5 (URL = source de config unique). Réexécuter ce script si les pages sont régénérées.

Usage : `python scripts/add_backlink_parcours.py` (depuis `backend/`).
"""

import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PARCOURS_DIR = BACKEND_DIR / "app" / "static" / "parcours"
DEFAULT_APP_URL = "https://avoulia-frontend.purpleocean-980317d1.francecentral.azurecontainerapps.io"

# Marqueur d'idempotence : présent dès qu'une page a déjà été traitée.
MARKER = 'id="avoulia-back"'


def _top_link(app_url: str) -> str:
    return (
        f'<a {MARKER} href="{app_url}" '
        'style="display:inline-block;margin-bottom:16px;color:#2B59C3;'
        'text-decoration:none;font-weight:600;font-size:14px">&larr; Retour à Avoulia</a>\n'
    )


def _footer_cta(app_url: str) -> str:
    return (
        '<p class="avoulia-relance" style="margin-top:10px">'
        f'<a href="{app_url}" style="color:#2B59C3;text-decoration:none;font-weight:700">'
        "&larr; Revenir à Avoulia pour explorer d'autres cas d'usage</a></p>\n"
    )


def process_file(path: Path, app_url: str) -> bool:
    """Injecte les liens si absents. Retourne True si le fichier a été modifié."""
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return False  # déjà traité

    changed = False
    # 1) Lien haut de page : juste après l'ouverture de `.page`.
    needle = '<div class="page">'
    if needle in html:
        html = html.replace(needle, needle + "\n  " + _top_link(app_url), 1)
        changed = True

    # 2) Rappel en pied : juste avant la fermeture du footer.
    if "</footer>" in html:
        html = html.replace("</footer>", "  " + _footer_cta(app_url) + "</footer>", 1)
        changed = True

    if changed:
        path.write_text(html, encoding="utf-8")
    return changed


def main() -> None:
    app_url = (os.getenv("AVOULIA_APP_URL") or DEFAULT_APP_URL).strip().rstrip("/")
    pages = sorted(PARCOURS_DIR.glob("action-*.html"))
    updated = skipped = 0
    for p in pages:
        if process_file(p, app_url):
            updated += 1
        else:
            skipped += 1
    print(f"Pages parcours : {len(pages)} | mises à jour : {updated} | déjà à jour : {skipped}")
    print(f"URL app utilisée : {app_url}")


if __name__ == "__main__":
    main()
