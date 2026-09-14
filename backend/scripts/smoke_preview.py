"""Exercise a running isolated synthetic preview through real HTTP and SSE."""

import argparse
import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def run(port: int) -> dict:
    base = f"http://127.0.0.1:{port}"
    trace = []

    def request(path, payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        with urlopen(Request(base + path, body, {"Content-Type": "application/json"}), timeout=15) as response:
            text = response.read().decode()
            return text if "text/event-stream" in response.headers.get("Content-Type", "") else json.loads(text)

    health = request("/health")
    assert health["preview"] and health["source"]["source_mode"] == "SYNTHETIC"
    state = request("/api/preview/v1/sessions", {"protocol_version": 1})
    assert len(state["question"]["options"]) == 14
    session_path = f"/api/preview/v1/sessions/{state['session_id']}"

    def command(action="choose", *, stream=False, **kwargs):
        nonlocal state
        payload = {
            "protocol_version": 1, "request_id": uuid.uuid4().hex,
            "revision": state["revision"], "question_id": state["question"]["id"],
            "catalogue_revision": state["catalogue_revision"], "action": action, **kwargs,
        }
        result = request(session_path + "/actions" + ("/stream" if stream else ""), payload)
        state = json.loads(next(line[6:] for line in result.splitlines() if line.startswith("data: "))) if stream else result
        trace.append({"phase": state["phase"], "revision": state["revision"],
                      "confirmed": state["confirmed"], "main": state["diagnostics"]["main"]})
        return payload

    def choose(label):
        option = next(item for item in state["question"]["options"] if item["label"] == label)
        command(choice_id=option["id"])

    need = "améliorer la pertinence des description produit pour l'adapter à la GenZ"
    old_request = command(choice_id="marketing_visibilite", initial_need=need)
    choose("Autre / Non spécifique")
    choose("Créer des contenus marketing")
    assert state["phase"] == "orientation"
    assert state["diagnostics"]["main"]["result_ids"] == []
    assert [item["case_id"] for item in state["question"]["options"]] == ["SYN-PRODUCT"]
    assert state["confirmed"]["domain"] == "marketing_visibilite"
    command("refuse")
    assert state["phase"] == "results" and state["confirmed"]["domain"] == "marketing_visibilite"
    command("back", target="objective")
    choose("Créer des contenus marketing")
    command("accept", choice_id=state["question"]["options"][0]["id"])
    assert state["confirmed"]["domain"] == "ventes_developpement"
    assert state["confirmed"]["sector"] == "Autre / Non spécifique"
    assert state["diagnostics"]["main"]["result_ids"] == ["SYN-PRODUCT"]
    command(choice_id="SYN-PRODUCT", stream=True)
    assert state["phase"] == "terminal" and "describe" not in state["allowed_actions"]
    assert state["problem_original"] == need
    assert request(session_path) == state
    handoff = request(state["card"]["handoff_url"])
    assert handoff["source_fields"]["description"] == state["card"]["description"]
    assert handoff["local_context"]["problem_original"] == need
    try:
        request(session_path + "/actions/stream", old_request)
        raise AssertionError("Old action unexpectedly accepted")
    except HTTPError as error:
        assert error.code == 409
    return {
        "passed": True, "source_mode": "SYNTHETIC", "case_count": health["source"]["case_count"],
        "coverage": health["source"]["coverage"], "http_sse_and_stale_guard": "passed",
        "steps": trace, "selected_case": state["card"]["case_id"],
        "handoff": base + state["card"]["handoff_url"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Use a loopback port between 1024 and 65535")
    print(json.dumps(run(args.port), ensure_ascii=False, indent=2))
