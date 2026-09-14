"""Bounded synthetic candidate-selection evaluation; offline unless --live is explicit.

Expectations are engineering hypotheses, not human-user labels or production accuracy.
This bypasses embedding retrieval, workbook ingestion, HTTP/SSE routing and the UI.
Live requests reproduce rag.stream_prompt's single user message and streamed Azure
chat-completions configuration, with a configurable total completion-token bound
(reasoning plus visible output, not independent budgets). No reasoning-effort override.
Live runs require explicit subscription, resource group and container app.
The defaults used by offline/programmatic runs describe the existing Avoulia dev app.
"""
from __future__ import annotations

import argparse
import copy
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import inspect
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import haystack_rag as rag
from app.config import _normalize_azure_endpoint


SUBSCRIPTION = ""
RESOURCE_GROUP = "rg-avoulia-fr-dev"
CONTAINER_APP = "avoulia-backend"
DOMAIN = "activites_terrain"
INTENTION = "Partager les informations terrain"
MAX_CALLS = 16
MAX_TOKENS = 1200
HYPOTHESIS = "Engineering hypotheses on synthetic fixtures; not human-user validated."
DIAGNOSTIC_VERSION = "2.0-numbered-clarifications"
SUITE_CONTEXTS = {
    "chantier": (DOMAIN, "BTP", INTENTION),
    "stock-assumptions": ("logistique_stocks", "Commerce & retail", "Réduire les stocks invendus"),
    "generic-intent": ("marketing_visibilite", "Autre", "Créer des contenus marketing"),
}

_NUMBERED_LINE = re.compile(r"(?m)^[ \t]*(?:#{1,6}[ \t]*)?(?:[-+*][ \t]+)?[*_`]*\d+")
_ZERO_MATCH = re.compile(
    r"(?:aucun(?:e)?\b.{0,100}\b(?:cas|proposition)|"
    r"(?:pas|sans)\s+(?:de\s+)?(?:cas|proposition)|"
    r"(?:cas|proposition).{0,100}(?:ne correspond|ne répond|n'est.{0,30}pertinent))",
    re.IGNORECASE | re.DOTALL,
)
_CLARIFICATION_QUESTION = re.compile(
    r"(?P<number>[12])[.)][ \t]+(?:Si non,[ \t]+)?"
    r"(?:(?:Voulez-vous|Souhaitez-vous)[ \t]+(?:plutôt[ \t]+)?explorer[ \t]+"
    r"(?:le|un autre)[ \t]+domaine\b|"
    r"(?:Pouvez-vous|Pourriez-vous)[ \t]+(?:préciser|décrire)[ \t]+"
    r"(?:votre|le)[ \t]+(?:besoin|problème|objectif)\b|"
    r"souhaitez-vous que j['’]essaie d['’]identifier des liens possibles entre\b)"
    r"[^?\r\n]{0,350}\?[ \t]*"
    r"(?:\(répondez[ \t]+[\"«]oui[\"»][ \t]+ou[ \t]+[\"«]non[\"»]\))?",
    re.IGNORECASE,
)


def _numbered_clarifications_only(raw, headings):
    """Accept only 1–2 complete, anchored questions after an explicit no-match."""
    if not 1 <= len(headings) <= 2 or not _ZERO_MATCH.search(raw[:headings[0].start()]):
        return False
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(raw)
        block = raw[heading.start():end].strip()
        match = _CLARIFICATION_QUESTION.fullmatch(block) if len(block) <= 600 else None
        if not match or int(match["number"]) != index + 1:
            return False
    return True


def synthetic_documents(suite="chantier"):
    if suite == "generic-intent":
        domain, sector, intention = SUITE_CONTEXTS[suite]
        rows = [
            ("product-rewrite", "Réécrire des fiches produit",
             "Reformuler les descriptions existantes pour clarifier les caractéristiques, les bénéfices "
             "et les arguments commerciaux. Fournir les fiches et faire relire les textes avant utilisation."),
            ("product-video", "Préparer des scripts vidéo de présentation produit",
             "Écrire des scripts TikTok de trente secondes : séquences à filmer et texte à prononcer "
             "pour présenter les produits."),
            ("website-analysis", "Analyser la conversion du site web",
             "Analyser les statistiques de navigation, identifier les pages où les visiteurs abandonnent "
             "et recommander des changements de structure et d'appels à l'action."),
            ("product-translation", "Traduire des fiches produit",
             "Traduire fidèlement les descriptions produit dans une autre langue en conservant "
             "les caractéristiques et le sens du texte source."),
        ]
        return [
            SimpleNamespace(id=f"synthetic-{key}", content=description, meta={
                "domaine": domain, "secteur": sector, "intention": intention,
                "cas_utilisation": title, "description_cas_utilisation": description,
            }) for key, title, description in rows
        ]
    if suite == "stock-assumptions":
        domain, sector, intention = SUITE_CONTEXTS[suite]
        rows = [
            ("slow-stock", "Analyser les articles invendus",
             "Repérer les articles à faible rotation dans les historiques de vente et préparer "
             "des actions ciblées pour les écouler. Si des données personnelles sont présentes, "
             "les anonymiser avant analyse."),
            ("seasonal-orders", "Prévoir les commandes saisonnières",
             "Prévoir la demande future liée aux saisons et adapter les quantités à commander "
             "avant chaque saison. Ce cas nécessite des variations saisonnières des ventes."),
            ("expiry", "Suivre les dates de péremption",
             "Repérer les produits périssables proches de leur date limite et prioriser leur écoulement."),
        ]
        return [
            SimpleNamespace(id=f"synthetic-{key}", content=description, meta={
                "domaine": domain, "secteur": sector, "intention": intention,
                "cas_utilisation": title, "description_cas_utilisation": description,
            }) for key, title, description in rows
        ]
    if suite != "chantier":
        raise EvaluationError("Unknown evaluation suite")
    rows = [
        ("summary", "Synthétiser les notes de réunion de chantier",
         "Transformer les notes de réunion en compte rendu clair. Restituer les échanges et les décisions."),
        ("safety", "Préparer un plan de prévention chantier",
         "Identifier les risques de sécurité et préparer les mesures de prévention avant une intervention."),
        ("reporting", "Consolider le reporting hebdomadaire du chantier",
         "Assembler les indicateurs d'avancement hebdomadaire et signaler les écarts de planning."),
        ("actions", "Suivre les actions de réunion chantier",
         "Extraire les tâches, responsables et échéances pour suivre leur réalisation."),
        ("translation", "Traduire les consignes de chantier",
         "Traduire fidèlement les consignes écrites dans la langue des équipes étrangères."),
    ]
    return [
        SimpleNamespace(id=f"synthetic-{key}", content=description, meta={
            "domaine": DOMAIN, "intention": INTENTION, "secteur": "BTP",
            "cas_utilisation": title, "description_cas_utilisation": description,
        }) for key, title, description in rows
    ]


def scenarios(suite="chantier"):
    if suite == "generic-intent":
        return [
            {"id": "product-genz", "query":
             "améliorer la pertinence des description produit pour l'adapter à la GenZ",
             "expected_ids": ["synthetic-product-rewrite"]},
            {"id": "product-new-clients", "query":
             "Je veux réécrire mes fiches produits pour cibler de nouveaux clients.",
             "expected_ids": ["synthetic-product-rewrite"]},
            {"id": "product-generic", "query":
             "Je veux améliorer mes descriptions produit.",
             "expected_ids": ["synthetic-product-rewrite"]},
            {"id": "product-no-video", "query":
             "Je veux réécrire mes fiches produit pour la GenZ, pas faire de vidéo ni analyser mon site.",
             "expected_ids": ["synthetic-product-rewrite"]},
            {"id": "product-manual-preparation", "query":
             "Je veux réécrire mes fiches produit pour mieux expliquer les bénéfices. "
             "Je rassemblerai les textes à retravailler plus tard.",
             "expected_ids": ["synthetic-product-rewrite"]},
            {"id": "product-explicit-video", "query":
             "Je veux préparer les scripts de vidéos TikTok pour présenter mes produits.",
             "expected_ids": ["synthetic-product-video"]},
            {"id": "product-translation-only", "query":
             "Je veux uniquement traduire mes fiches produit du français à l'allemand, "
             "sans reformuler les arguments commerciaux.",
             "expected_ids": ["synthetic-product-translation"]},
            {"id": "product-zero-match", "query":
             "Je veux une recette de gâteau au chocolat.",
             "expected_ids": []},
        ]
    if suite == "stock-assumptions":
        return [
            {"id": "stock-no-seasonality", "query":
             "Je tiens un magasin de décoration et je voudrais comprendre quels articles restent "
             "invendus, puis trouver des actions pour les écouler.",
             "expected_ids": ["synthetic-slow-stock"]},
            {"id": "stock-explicit-seasonality", "query":
             "Les ventes de mon magasin varient selon les saisons. Je veux uniquement prévoir la "
             "demande de la prochaine saison et adapter les quantités à commander, pas analyser "
             "les articles invendus aujourd'hui.",
             "expected_ids": ["synthetic-seasonal-orders"]},
            {"id": "stock-conditional-guardrail", "query":
             "Je souhaite analyser mes historiques de vente pour repérer les articles à faible "
             "rotation et préparer leur écoulement. Les fichiers contiennent des noms de clients "
             "qui devront être anonymisés.",
             "expected_ids": ["synthetic-slow-stock"]},
            {"id": "stock-zero-match", "query":
             "Je dois rédiger le compte rendu d'une réunion avec mon équipe.",
             "expected_ids": []},
        ]
    if suite != "chantier":
        raise EvaluationError("Unknown evaluation suite")
    return [
        {"id": "summary-not-safety", "query":
         "Je veux transformer mes notes de réunion de chantier en compte rendu des échanges, "
         "pas préparer un plan de prévention ni un tableau de suivi des tâches.",
         "expected_ids": ["synthetic-summary"]},
        {"id": "safety-not-summary", "query":
         "Avant une intervention sur le chantier, je dois identifier les risques de sécurité "
         "et définir les mesures de prévention, pas rédiger un compte rendu de réunion.",
         "expected_ids": ["synthetic-safety"]},
        {"id": "weekly-progress", "query":
         "Chaque semaine je dois rassembler les indicateurs d'avancement du chantier et "
         "repérer les écarts au planning. Je n'ai pas de notes de réunion à traiter.",
         "expected_ids": ["synthetic-reporting"]},
        {"id": "action-ownership", "query":
         "À partir de la réunion, je veux uniquement un suivi des tâches attribuées : "
         "qui doit faire quoi et pour quelle date, pas un résumé des échanges.",
         "expected_ids": ["synthetic-actions"]},
        {"id": "translation", "query":
         "Mes équipes parlent polonais et ne comprennent pas les consignes écrites en français. "
         "Je veux la même instruction dans leur langue, sans modifier son contenu.",
         "expected_ids": ["synthetic-translation"]},
        {"id": "synonyms-zero-keyword-overlap", "query":
         "Condensez nos palabres en mémo lisible.",
         "expected_ids": ["synthetic-summary"]},
        {"id": "zero-match", "query":
         "Je dois calculer la TVA et établir la déclaration fiscale annuelle de mon entreprise.",
         "expected_ids": []},
        {"id": "ambiguous-observation", "query":
         "Je souhaite améliorer mon chantier.",
         "expected_ids": None},
    ]


def build_prompt(query, documents, suite="chantier"):
    # Only document/metadata reads are substituted; prompt and parser remain real.
    domain, sector, intention = SUITE_CONTEXTS[suite]
    with ExitStack() as stack:
        stack.enter_context(patch.object(rag, "_fetch_documents_for_domaine", return_value=documents))
        stack.enter_context(patch.object(rag, "_get_q2_choices_list", return_value=[intention]))
        stack.enter_context(patch.object(
            rag, "get_document_store", side_effect=AssertionError("Real document reads forbidden")))
        return rag._build_rag_prompt_from_docs(
            query, "", "", documents, [{"role": "user", "content": query}],
            selected_domain_code=domain, selected_sector=sector, selected_intention="1",
        )


def assess_response(raw, documents, expected_ids, finish_reason="stop"):
    cases = [rag._doc_to_case_dict(doc, i) for i, doc in enumerate(documents)]
    answer, indices = rag._reconcile_generated_case_list(raw, cases)
    retained = [cases[i]["id"] for i in indices]
    # Independent diagnostic: an unrecognized numbered list must never count as
    # a successful semantic exclusion just because reconciliation returned [].
    headings = list(_NUMBERED_LINE.finditer(raw))
    numbered = bool(headings)
    explicit_zero_signal = bool(_ZERO_MATCH.search(raw))
    clarification_only = _numbered_clarifications_only(raw, headings)
    candidate_markup = bool(re.search(
        r"(?mi)^[ \t]*(?:[-+*][ \t]+|#{1,6}[ \t]+|\*\*|__)|"
        r"(?:Pourquoi c['’]est pertinent pour vous|Ce que cela permet concrètement)[ \t]*:",
        raw,
    ))
    explicit_zero = explicit_zero_signal and not candidate_markup and (not numbered or clarification_only)
    generation_failure = finish_reason != "stop" or not raw.strip()
    if retained:
        response_kind = "recognized_cases"
    elif explicit_zero:
        response_kind = "semantic_exclusion"
    elif numbered or candidate_markup:
        response_kind = "all_unrecognized_parse_failure"
    else:
        response_kind = "unstructured_or_clarification"
    parse_failure = not generation_failure and (response_kind == "all_unrecognized_parse_failure" or (
        response_kind == "unstructured_or_clarification" and expected_ids is not None
    ))
    expected = set(expected_ids or [])
    actual = set(retained)
    scored = expected_ids is not None
    missing = sorted(expected - actual) if scored else None
    peripheral = sorted(actual - expected) if scored else None
    inclusion = not missing if scored and expected else None
    exclusion = not peripheral if scored else None
    zero_correct = (
        not actual and response_kind == "semantic_exclusion" and not generation_failure
    ) if scored and not expected else None
    passed = (
        not missing and not peripheral and not parse_failure and not generation_failure
        and (bool(expected) or zero_correct)
    ) if scored else None
    return {
        "retained_ids": retained, "reconciled_response": answer,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "response_kind": response_kind, "parse_failure": parse_failure,
        "diagnostic_inconclusive": not generation_failure and response_kind in (
            "all_unrecognized_parse_failure", "unstructured_or_clarification"),
        "numbered_clarifications_only": clarification_only and not candidate_markup,
        "raw_explicit_zero_match_statement": explicit_zero_signal,
        "numbered_output_detected": numbered,
        "generation_failure": generation_failure,
        "expected_relevant_included": inclusion, "peripheral_excluded": exclusion,
        "missing_expected_ids": missing, "unexpected_peripheral_ids": peripheral,
        "correct_zero_match": zero_correct,
        "relevance_failure": bool(missing or peripheral)
        if scored and not generation_failure and not parse_failure else None,
        "hypothesis_pass": passed,
    }


class EvaluationError(RuntimeError):
    """Safe diagnostic without potentially secret CLI/SDK exception bodies."""


def az_json(arguments):
    executable = shutil.which("az")
    if not executable:
        raise EvaluationError("Azure CLI unavailable")
    try:
        result = subprocess.run(
            [executable, *arguments, "--only-show-errors", "-o", "json"],
            capture_output=True, text=True, timeout=300, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise EvaluationError(f"Azure CLI {arguments[0]} {arguments[1]} timed out after 300 seconds") from exc
    if result.returncode:
        # CLI stderr can contain identity/tenant information; never persist it.
        raise EvaluationError(f"Azure CLI {arguments[0]} {arguments[1]} failed (exit {result.returncode})")
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise EvaluationError("Azure CLI returned invalid JSON") from exc


def discover_config(subscription=SUBSCRIPTION, resource_group=RESOURCE_GROUP, container_app=CONTAINER_APP):
    allowed = [
        "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_CHAT_DEPLOYMENT",
        "AZURE_OPENAI_DEPLOYMENT_NAME", "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT_CHAT", "AZURE_OPENAI_API_VERSION_CHAT",
    ]
    predicate = " || ".join(f"name=='{name}'" for name in allowed)
    scope = ["--resource-group", resource_group, "--subscription", subscription]
    containers = az_json([
        "containerapp", "show", "--name", container_app, *scope, "--query",
        f"properties.template.containers[].env[?{predicate}].{{name:name,value:value}}",
    ])
    configurations = [
        {item["name"]: item.get("value") for item in envs} for envs in containers
    ]
    matching = [env for env in configurations if env.get("AZURE_OPENAI_ENDPOINT")]
    if len(matching) != 1:
        raise EvaluationError("Expected exactly one unambiguous app Azure endpoint configuration")
    env = matching[0]
    endpoint = _normalize_azure_endpoint(env["AZURE_OPENAI_ENDPOINT"])
    deployment = env.get("AZURE_OPENAI_CHAT_DEPLOYMENT") or env.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    version = env.get("AZURE_OPENAI_API_VERSION")
    if not deployment or not version:
        raise EvaluationError("Streamed-route deployment/API version missing; no backend fallback")
    accounts = az_json([
        "cognitiveservices", "account", "list", *scope, "--query",
        "[].{name:name,endpoint:properties.endpoint}",
    ])
    names = [
        item["name"] for item in accounts
        if _normalize_azure_endpoint(item.get("endpoint") or "") == endpoint
    ]
    if len(names) != 1:
        raise EvaluationError("Cannot uniquely identify the app endpoint's cognitive account")
    deployed = az_json([
        "cognitiveservices", "account", "deployment", "show", "--name", names[0],
        "--deployment-name", deployment, *scope, "--query", "{name:name,model:properties.model}",
    ])
    return {
        "subscription": subscription, "resource_group": resource_group, "container_app": container_app,
        "route_configuration": "app.rag.get_llm / stream_prompt (streamed chat)",
        "transport": "Azure OpenAI SDK streaming; single user message, temperature=1",
        "endpoint": endpoint, "deployment": deployment, "api_version": version,
        "account": names[0], "model": deployed["model"],
        "haystack_chat_endpoint_not_used": env.get("AZURE_OPENAI_ENDPOINT_CHAT"),
        "haystack_chat_api_version_not_used": env.get("AZURE_OPENAI_API_VERSION_CHAT"),
    }


def live_client(config, auth):
    from openai import AzureOpenAI
    if auth == "azure-cli-token":
        credential = az_json([
            "account", "get-access-token", "--subscription", config["subscription"],
            "--resource", "https://cognitiveservices.azure.com/", "--query", "accessToken",
        ])
        authentication = {"azure_ad_token": credential}
    else:
        credential = az_json([
            "cognitiveservices", "account", "keys", "list",
            "--name", config["account"], "--resource-group", config["resource_group"],
            "--subscription", config["subscription"], "--query", "key1",
        ])
        authentication = {"api_key": credential}
    if not isinstance(credential, str) or not credential:
        raise EvaluationError("Selected authentication method returned no credential")
    return AzureOpenAI(
        azure_endpoint=config["endpoint"], api_version=config["api_version"],
        max_retries=0, timeout=90, **authentication,
    )


def call_model(client, config, prompt, max_completion_tokens=MAX_TOKENS):
    raw = ""
    usage = None
    finish = None
    returned_model = None
    started = time.monotonic()
    with client.chat.completions.create(
        model=config["deployment"], messages=[{"role": "user", "content": prompt}],
        temperature=1, max_completion_tokens=max_completion_tokens,
        stream=True, stream_options={"include_usage": True},
    ) as stream:
        for chunk in stream:
            returned_model = chunk.model or returned_model
            if chunk.usage:
                usage = chunk.usage.model_dump()
            for choice in chunk.choices:
                raw += choice.delta.content or ""
                finish = choice.finish_reason or finish
    return {
        "raw_response": raw, "finish_reason": finish, "returned_model": returned_model,
        "elapsed_seconds": round(time.monotonic() - started, 3), "usage": usage,
    }


def summarize(results):
    completed = [row for row in results if "hypothesis_pass" in row]
    scored = [row for row in completed if row["hypothesis_pass"] is not None]
    paired = {}
    for row in completed:
        paired.setdefault(row["scenario_id"], []).append(set(row["retained_ids"]))
    reasoning = [
        (row.get("usage") or {}).get("completion_tokens_details", {}).get("reasoning_tokens")
        for row in completed
        if (row.get("usage") or {}).get("completion_tokens_details")
    ]
    reasoning_known = sum(value is not None for value in reasoning)
    reasoning_total = sum(value or 0 for value in reasoning)
    return {
        "completed_calls": len(completed), "scored_calls": len(scored),
        "hypothesis_passes": sum(row["hypothesis_pass"] for row in scored),
        "hypothesis_failures": sum(not row["hypothesis_pass"] for row in scored),
        "scored_generation_failures": sum(row["generation_failure"] for row in scored),
        "unscored_ambiguous_calls": len(completed) - len(scored),
        "parse_failures": sum(row["parse_failure"] for row in completed),
        "diagnostic_inconclusive_calls": sum(row.get("diagnostic_inconclusive", False) for row in completed),
        "generation_failures": sum(row["generation_failure"] for row in completed),
        "relevance_failures": sum(bool(row["relevance_failure"]) for row in scored),
        "semantic_relevance_scored_calls": sum(row["relevance_failure"] is not None for row in scored),
        "transport_failures": sum("transport_error" in row for row in results),
        "relevant_inclusion_passes": sum(row["expected_relevant_included"] is True for row in scored),
        "peripheral_exclusion_passes": sum(row["peripheral_excluded"] is True for row in scored),
        "zero_match_passes": sum(row["correct_zero_match"] is True for row in scored),
        "zero_match_statements_in_raw_output": sum(
            row.get("raw_explicit_zero_match_statement", False)
            for row in scored if row["correct_zero_match"] is not None
        ),
        "different_retained_sets_across_reversed_repeats": [
            key for key, sets in paired.items() if len(sets) == 2 and sets[0] != sets[1]
        ],
        "usage_totals": {
            field: sum((row.get("usage") or {}).get(field, 0) or 0 for row in completed)
            for field in ("prompt_tokens", "completion_tokens", "total_tokens")
        },
        "reasoning_tokens": reasoning_total if reasoning_known else None,
        "non_reasoning_completion_tokens": sum(
            row["usage"]["completion_tokens"]
            - row["usage"]["completion_tokens_details"]["reasoning_tokens"]
            for row in completed if row.get("usage")
            and (row["usage"].get("completion_tokens_details") or {}).get("reasoning_tokens") is not None
        ) if reasoning_known else None,
        "calls_with_reasoning_usage": reasoning_known,
    }


def reassess_report(source):
    """Reassess saved evidence offline, keeping the entire original report intact."""
    original = copy.deepcopy(source)
    documents = {
        case["id"]: SimpleNamespace(id=case["id"], content=case["content"], meta=case)
        for case in original["synthetic_candidates"]
    }
    results = copy.deepcopy(original["results"])
    for row in results:
        if "raw_response" in row:
            row.update(assess_response(
                row["raw_response"], [documents[key] for key in row["candidate_order"]],
                row["expected_ids"], row["finish_reason"],
            ))
    return {
        "schema_version": 1, "mode": "offline_diagnostic_reassessment",
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "reconciler_sha256": hashlib.sha256(
            inspect.getsource(rag._reconcile_generated_case_list).encode()).hexdigest(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "new_model_calls": 0, "expectation_status": original["expectation_status"],
        "original_report": original, "results": results, "summary": summarize(results),
        "interpretation": (
            "Numbered clarification recognition changes only the diagnostic. It does not "
            "validate the follow-up questions, UX or relevance expectations. Uncertain "
            "numbered output remains inconclusive, never a successful no-match by default."
        ),
    }


def evaluation_plan(args, documents):
    suite = getattr(args, "suite", "chantier")
    by_id = {row["id"]: row for row in scenarios(suite)}
    selected = list(dict.fromkeys(getattr(args, "scenario", None) or by_id))
    repeats = getattr(args, "repeats", 2)
    tokens = getattr(args, "max_completion_tokens", MAX_TOKENS)
    if any(name not in by_id for name in selected):
        raise EvaluationError("Unknown evaluation scenario")
    if type(repeats) is not int or not 1 <= repeats <= 2:
        raise EvaluationError("Repeats must be 1 or 2")
    if type(tokens) is not int or not 1 <= tokens <= 6000:
        raise EvaluationError("Completion-token bound must be between 1 and 6000")
    if not selected or len(selected) * repeats > MAX_CALLS:
        raise EvaluationError("Selected evaluation exceeds the 16-call absolute cap")
    plan, prompts = [], {}
    for name in selected:
        scenario = by_id[name]
        for repeat in range(1, repeats + 1):
            ordered = documents if repeat == 1 else list(reversed(documents))
            prompt = build_prompt(scenario["query"], ordered, suite)
            plan.append({
                "scenario_id": name, "repeat": repeat, "query": scenario["query"],
                "expected_ids": scenario["expected_ids"],
                "candidate_order": [doc.id for doc in ordered],
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt_characters": len(prompt),
            })
            prompts[(name, repeat)] = prompt
    return selected, repeats, tokens, plan, prompts


def validate_resume(saved, fresh):
    if not isinstance(saved, dict) or saved.get("mode") != "live":
        raise EvaluationError("Resume requires a live evaluation artifact")
    identity_fields = (
        "schema_version", "mode", "max_calls", "max_completion_tokens", "auth", "azure_scope",
        "scenario_ids", "repeats", "prompt_template_sha256", "reconciler_sha256",
        "synthetic_candidates", "evaluation_plan", "request_parameters", "sdk_retries",
    )
    for field in identity_fields:
        if saved.get(field) != fresh.get(field):
            raise EvaluationError(f"Resume {field} differs; original evidence preserved, no inference")
    rows = saved.get("results")
    attempts = saved.get("attempted_calls")
    if not isinstance(rows, list) or type(attempts) is not int or not 0 <= attempts <= fresh["max_calls"]:
        raise EvaluationError("Invalid resume call accounting")
    if len(rows) != attempts:
        raise EvaluationError("Resume attempt count does not match saved results")
    if attempts and "configuration" not in saved:
        raise EvaluationError("Resume is missing its original live route configuration")
    # A persisted attempt is never replayed, including one interrupted before its response.
    for row, planned in zip(rows, fresh["evaluation_plan"]):
        if not isinstance(row, dict) or any(row.get(key) != value for key, value in planned.items()):
            raise EvaluationError("Resume results are not an exact prefix of the evaluation plan")


def run(args):
    documents = synthetic_documents(getattr(args, "suite", "chantier"))
    selected, repeats, tokens, plan, prompts = evaluation_plan(args, documents)
    scope = {
        "subscription": getattr(args, "subscription", None) or SUBSCRIPTION,
        "resource_group": getattr(args, "resource_group", None) or RESOURCE_GROUP,
        "container_app": getattr(args, "container_app", None) or CONTAINER_APP,
    }
    report = {
        "schema_version": 2, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "mode": "live" if args.live else "offline_dry_run",
        "expectation_status": HYPOTHESIS,
        "scope": "Current candidate-selection prompt plus production output reconciler only",
        "excluded": ["embedding retrieval/ranking", "workbook", "UX", "HTTP/SSE route integration",
                     "human relevance validation", "production accuracy", "before/after comparison"],
        "max_calls": len(plan), "max_completion_tokens": tokens, "sdk_retries": 0,
        "azure_scope": scope, "scenario_ids": selected, "repeats": repeats, "evaluation_plan": plan,
        "request_parameters": {"temperature": 1, "stream": True, "reasoning_effort": "server_default",
                               "max_completion_tokens": tokens},
        "token_budget_semantics": "Single total completion-token cap includes reasoning and visible output",
        "auth": args.auth if args.live else None, "attempted_calls": 0,
        "prompt_template_sha256": hashlib.sha256(rag.RAG_PROMPT.encode()).hexdigest(),
        "reconciler_sha256": hashlib.sha256(
            inspect.getsource(rag._reconcile_generated_case_list).encode()).hexdigest(),
        "synthetic_candidates": [rag._doc_to_case_dict(doc, i) for i, doc in enumerate(documents)],
        "results": [],
    }
    interval = getattr(args, "interval_seconds", 60)
    if getattr(args, "resume", False):
        saved = json.loads(args.output.read_text(encoding="utf-8"))
        validate_resume(saved, report)
        report = saved
        # Re-score already persisted raw evidence without any extra model calls.
        for row in report["results"]:
            if "raw_response" in row:
                by_id = {doc.id: doc for doc in documents}
                ordered = [by_id[doc_id] for doc_id in row["candidate_order"]]
                row.update(assess_response(
                    row["raw_response"], ordered, row["expected_ids"], row["finish_reason"],
                ))
            elif "transport_error" not in row:
                row["transport_error"] = {"type": "InterruptedAttempt",
                                          "message": "Persisted attempt has no response; never replayed"}
        report["resumed_utc"] = datetime.now(timezone.utc).isoformat()
        if "error" in report:
            report.setdefault("prior_errors", []).append(report.pop("error"))
    report["minimum_interval_seconds"] = interval

    def persist():
        report["summary"] = summarize(report["results"])
        if args.output:
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    client = None
    current_row = None
    previous_started = None
    try:
        if args.live:
            configuration = discover_config(**scope)
            if "configuration" in report and report["configuration"] != configuration:
                raise EvaluationError("Live route configuration changed; refusing mixed evaluation")
            report["configuration"] = configuration
            client = live_client(report["configuration"], args.auth)
        for planned in plan[len(report["results"]):]:
            row = dict(planned)
            ordered = documents if row["repeat"] == 1 else list(reversed(documents))
            prompt = prompts[(row["scenario_id"], row["repeat"])]
            if args.live:
                if report["attempted_calls"] >= report["max_calls"]:
                    raise EvaluationError("Maximum inference-call budget reached")
                if previous_started is not None:
                    time.sleep(max(0, interval - (time.monotonic() - previous_started)))
                report["attempted_calls"] += 1
                current_row = row
                report["results"].append(row)
                persist()
                previous_started = time.monotonic()
                generated = call_model(client, report["configuration"], prompt, tokens)
                row.update(generated)
                row.update(assess_response(
                    generated["raw_response"], ordered, row["expected_ids"], generated["finish_reason"],
                ))
                print(f"{row['scenario_id']} repeat={row['repeat']}: {row['response_kind']} "
                      f"hypothesis_pass={row['hypothesis_pass']}", flush=True)
                current_row = None
            else:
                report["results"].append(row)
            persist()
        transport_failed = any("transport_error" in row for row in report["results"])
        generation_failed = any(row.get("generation_failure") for row in report["results"])
        report["status"] = (
            "completed_with_transport_errors" if transport_failed else
            "inconclusive_generation_failure" if generation_failed else
            "completed" if args.live else "dry_run_ready"
        )
        persist()
        return report, (2 if transport_failed else 3 if generation_failed else
                        1 if report["summary"]["hypothesis_failures"] else 0)
    except Exception as exc:
        report["status"] = "transport_or_config_error"
        report["error"] = {
            "type": type(exc).__name__, "http_status": getattr(exc, "status_code", None),
            "message": str(exc) if isinstance(exc, EvaluationError) else
            "Evaluation stopped; no retry or alternate model. Exception body omitted for privacy.",
        }
        if current_row is not None:
            current_row["transport_error"] = report["error"]
        persist()
        return report, 2
    finally:
        if client is not None:
            client.close()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Authorize at most 16 sequential model calls")
    parser.add_argument("--auth", choices=["azure-cli-token", "azure-cli-key"], default="azure-cli-token",
                        help="Explicit auth method; no automatic fallback or resource/RBAC writes")
    parser.add_argument("--output", type=Path, help="JSON artifact in an existing private directory")
    parser.add_argument("--resume", action="store_true",
                        help="Continue only unattempted scenarios; preserve failures and total 16-call budget")
    parser.add_argument("--interval-seconds", type=float, default=60,
                        help="Minimum delay between request starts (default 60 for existing 10k TPM limit)")
    parser.add_argument("--suite", choices=list(SUITE_CONTEXTS), default="chantier",
                        help="Synthetic fixtures; stock-assumptions covers unstated conditions")
    parser.add_argument("--scenario", action="append",
                        choices=[row["id"] for suite in SUITE_CONTEXTS for row in scenarios(suite)],
                        help="Select a scenario; repeat flag to select several (default: all)")
    parser.add_argument("--repeats", type=int, choices=[1, 2], default=2)
    parser.add_argument("--max-completion-tokens", type=int, default=MAX_TOKENS,
                        help="Total reasoning plus output cap, 1–6000 (default 1200)")
    parser.add_argument("--subscription", help="Azure subscription ID; required explicitly for live runs")
    parser.add_argument("--resource-group", help=f"Required for live; existing dev group: {RESOURCE_GROUP}")
    parser.add_argument("--container-app", help=f"Required for live; existing dev app: {CONTAINER_APP}")
    args = parser.parse_args(argv)
    if any(name not in {row["id"] for row in scenarios(args.suite)} for name in args.scenario or []):
        parser.error("--scenario must belong to the selected --suite")
    if args.live and not args.output:
        parser.error("--live requires --output to preserve evidence")
    if args.output and not args.output.parent.is_dir():
        parser.error("--output parent directory must already exist")
    if args.resume and (not args.live or not args.output or not args.output.is_file()):
        parser.error("--resume requires --live and an existing --output artifact")
    if args.live and args.output.exists() and not args.resume:
        parser.error("Refusing to overwrite live evidence; use --resume or a new --output path")
    if not 0 <= args.interval_seconds <= 300:
        parser.error("--interval-seconds must be between 0 and 300")
    if not 1 <= args.max_completion_tokens <= 6000:
        parser.error("--max-completion-tokens must be between 1 and 6000")
    if args.live and not all((args.subscription, args.resource_group, args.container_app)):
        parser.error("--live requires explicit --subscription, --resource-group and --container-app")
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        report, code = run(args)
    except (EvaluationError, ValueError, OSError) as exc:
        print(json.dumps({"status": "configuration_error", "type": type(exc).__name__,
                          "message": str(exc) if isinstance(exc, EvaluationError)
                          else "Invalid evaluation artifact or output path"}))
        return 2
    print(json.dumps({"status": report["status"], "summary": report["summary"],
                      "error": report.get("error")}, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
