"""Explicit live, bounded normal-public-API replay with fictitious needs only.

Run from backend: python -B scripts\\smoke_preview_public.py --live
Does not write source fields, queries, HTML, or a catalogue index to disk.
"""

import argparse
import json
from pathlib import Path
import sys
import uuid
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.preview_protocol import QualificationService
from app.preview_public_api import NoRedirect, PublicAPIRepository, public_parcours_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Allow normal API calls containing fictitious needs.")
    args = parser.parse_args()
    if not args.live:
        parser.error("An explicit --live is required; no external requests were made.")
    repository = PublicAPIRepository()
    service = QualificationService(repository)

    def choose(state, index, **fields):
        return service.act(state["session_id"], {
            "protocol_version": 1, "request_id": uuid.uuid4().hex,
            "revision": state["revision"], "question_id": state["question"]["id"],
            "catalogue_revision": state["catalogue_revision"], "action": "choose",
            "choice_id": state["question"]["options"][index]["id"], **fields,
        })

    first = service.create()
    domains = first["question"]["options"]
    assert len(domains) == 14
    report = {"source": repository.provenance, "domains": [], "replays": []}
    for index, domain in enumerate(domains):
        state = choose(service.create(), index)
        assert state["phase"] in {"sector", "objective"}
        report["domains"].append({"id": domain["id"], "label": domain["label"],
                                  "next_phase": state["phase"], "choices": len(state["question"]["options"])})
    for query in [
        "Rédiger une newsletter mensuelle avec nos actualités, sans inventer des offres.",
        "améliorer la pertinence des description produit pour l'adapter à la GenZ",
    ]:
        state = service.create()
        marketing = next(i for i, item in enumerate(state["question"]["options"])
                         if item["label"] == "Marketing & visibilité")
        state = choose(state, marketing, initial_need=query)
        other = next(i for i, item in enumerate(state["question"]["options"])
                     if item["label"] == "Autre / Non spécifique")
        state = choose(state, other)
        objective = next(i for i, item in enumerate(state["question"]["options"])
                         if item["label"] == "Créer des contenus marketing")
        state = choose(state, objective)
        assert state["problem_original"] == state["initial_need"] == query
        replay = {"query": query, "phase": state["phase"], "main": state["diagnostics"]["main"],
                  "orientation": state["diagnostics"]["orientation"], "cases": []}
        for option in state["question"]["options"]:
            case = repository.get(option["id"])
            replay["cases"].append({"id": case.case_id, "title": case.title, "description": case.description,
                                    "parcours_url": case.parcours_url})
        if state["question"]["options"]:
            state = choose(state, 0)
            assert state["phase"] == "terminal" and state["question"]["options"] == []
            transfer = service.handoff(state["session_id"], state["revision"])
            url = public_parcours_url(transfer["parcours_url"], transfer["case_hash"])
            with urllib.request.build_opener(NoRedirect()).open(url, timeout=30) as response:
                assert response.status == 200 and response.headers.get_content_type() == "text/html"
                replay["published_parcours_http_status"] = response.status
        report["replays"].append(replay)
    report["source"] = repository.provenance
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
