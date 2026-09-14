"""Explicit, bounded live HTTP acceptance against the local PUBLIC_PAGES server.

No transcript/query persistence. Selection chunks and independent verification calls
are reported separately, paced under the existing quota. Explicit operator consent required.
"""
import json
import argparse
import time
import urllib.error
import urllib.request
import uuid

ORIGIN = "http://127.0.0.1:8767"
API = ORIGIN + "/api/preview/v1"
GENZ = "améliorer la pertinence des description produit pour l'adapter à la GenZ"
IN_PROCESS_CLIENT = None


def request(path, data=None):
    if IN_PROCESS_CLIENT is not None:
        local_path = path.removeprefix(ORIGIN)
        response = IN_PROCESS_CLIENT.request("POST" if data is not None else "GET", local_path, json=data)
        if response.is_error:
            raise urllib.error.HTTPError(path, response.status_code, response.text, response.headers, None)
        return response.json()
    req = urllib.request.Request(
        path if path.startswith(ORIGIN) else ORIGIN + path,
        data=json.dumps(data, ensure_ascii=False).encode() if data is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=900) as response:
        return json.load(response)


def act(state, action="choose", **fields):
    return request(f'{API}/sessions/{state["session_id"]}/actions', {
        "protocol_version": 1, "catalogue_revision": state["catalogue_revision"],
        "revision": state["revision"], "question_id": state["question"]["id"],
        "request_id": uuid.uuid4().hex, "action": action, **fields,
    })


def qualify(need, choices=("marketing", "Autre / Non spécifique", "Créer des contenus marketing")):
    state = request(API + "/sessions", {"protocol_version": 1, "external_consent": True,
                                       "source_mode": "PUBLIC_PAGES", "initial_need": need})
    for text in choices:
        state = act(state, choice_text=text)
    return state


def report(label, state):
    print(json.dumps({
        "test": label, "phase": state["phase"], "confirmed": state["confirmed"],
        "main": state["diagnostics"]["main"], "orientation": state["diagnostics"]["orientation"],
        "source": {key: state["diagnostics"]["source"].get(key) for key in (
            "source_mode", "case_count", "catalogue_revision", "inference_calls", "inference_tokens")},
    }, ensure_ascii=False), flush=True)


def test_genz():
    state = qualify(GENZ)
    report("GenZ", state)
    assert state["problem_original"] == state["initial_need"] == GENZ
    main = state["diagnostics"]["main"]
    assert "UC-0706" in main["candidate_ids"], "UC-0706 absent from real candidate pool"
    assert "UC-0706" in main["result_ids"], "Model did not select UC-0706; keep visible as acceptance failure"
    assert not {"UC-0437", "UC-0485"}.intersection(main["result_ids"]), "An unstated TikTok/WhatsApp activity was inferred"
    assert state["diagnostics"]["orientation"] is None
    state = act(state, choice_id="UC-0706")
    assert state["phase"] == "terminal"
    transfer = request(state["card"]["handoff_url"])
    assert transfer["source_fields"]["description"] == state["card"]["description"]
    assert transfer["source_fields"]["mode_execution"] is None
    assert GENZ not in state["card"]["preview_parcours_url"]
    print(json.dumps({"test": "terminal", "case": state["card"]["case_id"],
                      "title": state["card"]["title"], "source_hash": state["card"]["source_hash"],
                      "parcours": transfer["parcours_url"], "mode_execution": None}), flush=True)


def test_negative():
    state = qualify("Je veux une recette de gâteau au chocolat.")
    report("negative-chocolate", state)
    assert not state["diagnostics"]["main"]["result_ids"]
    assert not state["diagnostics"]["orientation"]["result_ids"]
    assert state["phase"] == "results"


def test_specialization():
    state = qualify("Je veux rédiger une offre d'emploi claire pour recruter un candidat.")
    report("generic-recruitment-no-specialization", state)
    assert state["phase"] == "orientation"
    assert not state["diagnostics"]["main"]["result_ids"]
    assert state["diagnostics"]["orientation"]["result_ids"]
    assert "UC-1024" not in state["diagnostics"]["orientation"]["result_ids"], "Unstated age specialization"


def test_video():
    state = qualify(
        "Je travaille dans une PME agroalimentaire. Je veux créer un script de vidéo recette "
        "de gâteau au chocolat de 30 secondes pour TikTok, avec les étapes filmables, "
        "une accroche et des hashtags pour mettre en valeur nos produits."
    )
    report("explicit-video-positive", state)
    assert "UC-0437" in state["diagnostics"]["main"]["result_ids"], "Explicit video activity lost"


def test_inclusive():
    state = qualify(
        "Je veux rédiger une offre d'emploi sans formulations âgistes, attractive aussi pour les candidats "
        "expérimentés de 50 ans et plus, et préparer leur recrutement et leur intégration dans l'équipe, "
        "sans exclure les autres âges.",
        ("RH & gestion des équipes", "Autre / Non spécifique", "Recruter et intégrer"),
    )
    report("explicit-inclusive-recruitment-positive", state)
    assert "UC-1024" in state["diagnostics"]["main"]["result_ids"], "Explicit inclusive recruitment lost"


def test_verifier_regressions():
    if IN_PROCESS_CLIENT is None:
        raise ValueError("Verifier challenge requires --in-process with real public sources")
    from app.preview_public_rag import verification_messages, reconcile_verification
    repository = IN_PROCESS_CLIENT.app.state.qualification.repository
    controls = (
        ("chocolate", "Je veux une recette de gâteau au chocolat.", "UC-0437"),
        ("generic-recruitment", "Je veux rédiger une offre d'emploi claire pour recruter un candidat.", "UC-1024"),
    )
    # Exercise the gate even when the first selector happens to abstain correctly.
    for label, need, key in (*controls, *reversed(controls)):
        case = repository.get(key)
        rows = [{"id": case.case_id, "titre": case.title, "description": case.description}]
        payload, usage = repository.azure.select(verification_messages(need, rows), purpose="verification")
        selected = reconcile_verification(payload, need, rows)
        print(json.dumps({"test": "forced-public-candidate-" + label, "case": key,
                          "verified_ids": selected, "judgments": payload["judgments"], "usage": usage},
                         ensure_ascii=False), flush=True)
        assert not selected, "Verifier accepted an unstated channel/activity/population"


def test_orientation():
    need = "Je veux rédiger une offre d'emploi claire pour recruter un candidat."
    state = qualify(need)
    report("separate-orientation", state)
    assert state["phase"] == "orientation", "No genuine orientation found"
    assert not state["diagnostics"]["main"]["result_ids"]
    assert "UC-1024" not in state["diagnostics"]["orientation"]["result_ids"], "Unstated age specialisation proposed"
    original = state["confirmed"].copy()
    session_id = state["session_id"]
    # Refuse, then explicitly re-submit the same need to test a new offer's acceptance.
    state = act(state, "refuse")
    assert state["confirmed"] == original and state["phase"] == "results"
    state = act(state, "back", target="problem")
    state = act(state, "describe", text=need)
    assert state["phase"] == "orientation"
    assert "UC-1024" not in state["diagnostics"]["orientation"]["result_ids"], "Unstated age specialisation proposed on repeat"
    offer = state["question"]["options"][0]
    state = act(state, "accept", choice_id=offer["id"])
    report("accepted-orientation", state)
    assert state["session_id"] == session_id
    assert state["confirmed"]["domain"] != original["domain"] or state["confirmed"]["objective"] != original["objective"]
    assert state["problem_original"] == need
    assert state["phase"] == "results" and state["diagnostics"]["main"]["result_ids"]
    assert "UC-1024" not in state["diagnostics"]["main"]["result_ids"], "Accepted route introduced unstated age specialisation"
    assert state["diagnostics"]["orientation"] is None


def run(stage="all"):
    health = request("/health")
    assert health["source"]["source_mode"] == "PUBLIC_PAGES", health
    try:
        request(API + "/sessions", {"protocol_version": 1, "source_mode": "PUBLIC_PAGES"})
        raise AssertionError("Consent was not required")
    except urllib.error.HTTPError as error:
        assert error.code == 403
    started = time.monotonic()
    if stage == "semantic":
        tests = (test_genz, test_negative, test_specialization, test_video, test_inclusive,
                 test_negative, test_genz)
    elif stage == "semantic-repeat":
        tests = (test_inclusive, test_negative, test_genz, test_verifier_regressions)
    else:
        tests = tuple(test for name, test in (
            ("genz", test_genz), ("negative", test_negative), ("orientation", test_orientation),
            ("specialization", test_specialization), ("video", test_video), ("inclusive", test_inclusive),
            ("verifier-regressions", test_verifier_regressions),
        ) if stage == name or stage == "all" and name in {"genz", "negative", "orientation"})
    for test in tests:
        before = time.monotonic()
        try:
            test()
        finally:
            source = request("/health")["source"]
            print(json.dumps({"attempted": test.__name__, "elapsed_seconds": round(time.monotonic() - before),
                              "calls": source.get("inference_calls"), "tokens": source.get("inference_tokens")}), flush=True)
    print(json.dumps({"live_acceptance": "passed", "stage": stage,
                      "elapsed_seconds": round(time.monotonic() - started)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("all", "semantic", "semantic-repeat", "genz", "negative", "orientation",
                                          "specialization", "video", "inclusive", "verifier-regressions"), default="all")
    parser.add_argument("--in-process", action="store_true",
                        help="Fresh real PUBLIC_PAGES app from current code; existing server is not restarted.")
    parser.add_argument("--raw-model-results", action="store_true",
                        help="Print public-source judgments in this console, including before contract validation.")
    args = parser.parse_args()
    if args.in_process:
        from fastapi.testclient import TestClient
        from app.preview import create_app
        app = create_app(mode="public_pages")
        if args.raw_model_results:
            original_select = app.state.qualification.repository.azure.select

            def observed_select(messages, *, purpose="selection"):
                payload, usage = original_select(messages, purpose=purpose)
                print(json.dumps({"raw_model_purpose": purpose, "payload": payload, "usage": usage},
                                 ensure_ascii=False), flush=True)
                return payload, usage

            app.state.qualification.repository.azure.select = observed_select
        with TestClient(app) as IN_PROCESS_CLIENT:
            run(args.stage)
    else:
        if args.raw_model_results:
            parser.error("--raw-model-results requires --in-process")
        run(args.stage)
