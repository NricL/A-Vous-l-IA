"""
Statistiques d'usage simples et INTÉGRÉES au chatbot (Axe 3.1, version simple).

Objectif : suivre, sans produit externe ni dashboard séparé, les éléments les plus visités —
domaines (rôles), problématiques (Q3) et cas d'usage sélectionnés — plus les clics sur le
bouton parcours. Le tout est consultable sur une page `/stats` servie par le backend.

Stockage : un *append blob* Azure (concurrence-safe, dépendance `azure-storage-blob` déjà
présente) quand un compte de stockage est configuré (STORAGE_ACCOUNT_NAME/KEY) ; sinon repli
EN MÉMOIRE (suffisant pour démarrer, remis à zéro au redémarrage). Aucune nouvelle infra requise :
compatible avec le futur mono-conteneur.
"""

import html
import json
import logging
import threading
import time
from collections import Counter
from typing import Any

from app.config import get_settings

logger = logging.getLogger("app.stats")

_CONTAINER = "stats"
_BLOB_NAME = "events.jsonl"
_lock = threading.Lock()
_memory_events: list[dict] = []  # repli si pas de storage configuré

# Libellés lisibles pour les types d'événements affichés.
_TYPE_LABELS = {
    "domaine": "Domaines (rôles) les plus choisis",
    "cas": "Cas d'usage les plus consultés",
    "probleme": "Problématiques les plus fréquentes",
}


def _blob_client():
    s = get_settings()
    name = (getattr(s, "storage_account_name", "") or "").strip()
    key = (getattr(s, "storage_account_key", "") or "").strip()
    if not name or not key:
        return None
    try:
        from azure.storage.blob import BlobServiceClient

        svc = BlobServiceClient(account_url=f"https://{name}.blob.core.windows.net", credential=key)
        container = svc.get_container_client(_CONTAINER)
        try:
            container.create_container()
        except Exception:
            pass  # existe déjà
        return container.get_blob_client(_BLOB_NAME)
    except Exception:
        logger.warning("stats: blob indisponible, repli mémoire", exc_info=True)
        return None


def record(event_type: str, value: str) -> None:
    """Enregistre un événement (type + valeur). Jamais bloquant/critique : les erreurs sont avalées."""
    value = (value or "").strip()
    if not value or not event_type:
        return
    entry = {"ts": int(time.time()), "type": event_type, "value": value[:200]}
    bc = _blob_client()
    if bc is None:
        with _lock:
            _memory_events.append(entry)
        return
    try:
        line = (json.dumps(entry, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            bc.append_block(line)
        except Exception:
            # L'append blob n'existe pas encore : le créer puis réessayer.
            bc.create_append_blob()
            bc.append_block(line)
    except Exception:
        logger.warning("stats: échec append, repli mémoire", exc_info=True)
        with _lock:
            _memory_events.append(entry)


def _all_events() -> list[dict]:
    bc = _blob_client()
    if bc is None:
        with _lock:
            return list(_memory_events)
    try:
        data = bc.download_blob().readall().decode("utf-8")
    except Exception:
        return []
    out: list[dict] = []
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def aggregates(top_n: int = 15) -> dict[str, Any]:
    events = _all_events()
    counters: dict[str, Counter] = {}
    for e in events:
        t = e.get("type")
        v = e.get("value")
        if t and v:
            counters.setdefault(t, Counter())[v] += 1

    def top(t: str) -> list[tuple[str, int]]:
        return counters.get(t, Counter()).most_common(top_n)

    return {
        "total_events": len(events),
        "top_domaines": top("domaine"),
        "top_cas": top("cas"),
        "top_problemes": top("probleme"),
        "parcours_clicks": sum(counters.get("parcours_click", Counter()).values()),
    }


def _render_list(title: str, rows: list[tuple[str, int]]) -> str:
    if not rows:
        items = '<li class="empty">Aucune donnée pour le moment.</li>'
    else:
        maxc = max(c for _, c in rows) or 1
        items = "".join(
            f'<li><span class="bar" style="width:{max(6, int(100 * c / maxc))}%"></span>'
            f'<span class="val">{html.escape(v)}</span><span class="cnt">{c}</span></li>'
            for v, c in rows
        )
    return f'<section><h2>{html.escape(title)}</h2><ul class="rank">{items}</ul></section>'


def render_html() -> str:
    a = aggregates()
    sections = (
        _render_list(_TYPE_LABELS["domaine"], a["top_domaines"])
        + _render_list(_TYPE_LABELS["cas"], a["top_cas"])
        + _render_list(_TYPE_LABELS["probleme"], a["top_problemes"])
    )
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Avoulia — Statistiques d'usage</title>
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background:#0f1420; color:#e8ecf4; }}
  .wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 20px 64px; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color:#9aa6bd; font-size: 13px; margin-bottom: 24px; }}
  .kpis {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom: 28px; }}
  .kpi {{ background:#182135; border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:14px 18px; }}
  .kpi .n {{ font-size: 26px; font-weight:700; }}
  .kpi .l {{ font-size:12px; color:#9aa6bd; }}
  section {{ background:#182135; border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:16px 18px; margin-bottom:18px; }}
  h2 {{ font-size:15px; margin:0 0 12px; }}
  ul.rank {{ list-style:none; margin:0; padding:0; }}
  ul.rank li {{ position:relative; display:flex; align-items:center; gap:10px; padding:7px 8px; border-radius:8px; overflow:hidden; }}
  ul.rank li .bar {{ position:absolute; left:0; top:0; bottom:0; background:rgba(0,96,223,.22); z-index:0; }}
  ul.rank li .val {{ position:relative; z-index:1; flex:1; font-size:13px; }}
  ul.rank li .cnt {{ position:relative; z-index:1; font-weight:700; font-size:13px; }}
  ul.rank li.empty {{ color:#9aa6bd; font-size:13px; }}
</style></head>
<body><div class="wrap">
  <h1>Statistiques d'usage — Avoulia</h1>
  <div class="sub">Éléments les plus visités. Actualisez la page pour rafraîchir.</div>
  <div class="kpis">
    <div class="kpi"><div class="n">{a['parcours_clicks']}</div><div class="l">Clics sur le bouton parcours</div></div>
    <div class="kpi"><div class="n">{a['total_events']}</div><div class="l">Événements enregistrés</div></div>
  </div>
  {sections}
</div></body></html>"""
