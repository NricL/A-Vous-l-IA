"""Repository contract and explicitly synthetic, offline preview catalogue.

This module is not imported by the production RAG or its routes. A real indexed
adapter must implement the same contract; the fixture matcher is not a RAG.
"""

import hashlib
import copy
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.rag_constants import (
    CHOIX_Q1_TO_DOMAINE_CODE, Q1_DOMAINS_LIST, SECTEURS_PAR_DOMAINE,
)

DOMAINS = dict(zip(CHOIX_Q1_TO_DOMAINE_CODE.values(), Q1_DOMAINS_LIST))
OTHER_SECTOR = "Autre / Non spécifique"
MULTI_SECTOR = "Multi-sectoriel"


def canonical_id(kind: str, *values: str) -> str:
    # Source identity, not the displayed position or the question wording.
    digest = hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()[:24]
    return f"{kind}:{digest}"


def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


@dataclass(frozen=True)
class Filters:
    domain: str
    sector: str | None
    objective: str

    def as_dict(self) -> dict:
        return {
            "domain": self.domain, "sector": self.sector, "objective": self.objective,
            "sector_policy": "selected_or_multi" if self.sector not in (None, OTHER_SECTOR)
            else "multi_only" if self.sector == OTHER_SECTOR else "not_applicable",
        }


@dataclass(frozen=True)
class Case:
    case_id: str
    domain: str
    objective: str
    sectors: tuple[str, ...]
    title: str
    description: str
    source_hash: str
    source_fields: dict
    source_url: str | None = None
    parcours_url: str | None = None
    case_hash: str | None = None

    @property
    def objective_id(self) -> str:
        return canonical_id("objective", self.domain, self.objective)


@dataclass(frozen=True)
class Retrieval:
    filters: dict
    candidates: tuple[str, ...]
    results: tuple[str, ...]
    mode: str
    details: dict = field(default_factory=dict)


class CatalogueRepository(Protocol):
    revision: str
    provenance: dict

    def sectors(self, domain: str) -> list[str]: ...
    def objectives(self, domain: str, sector: str | None) -> list[tuple[str, str]]: ...
    def get(self, case_id: str) -> Case | None: ...
    def eligible(self, case: Case, filters: Filters) -> bool: ...
    def search(self, problem: str, filters: Filters) -> Retrieval: ...
    def orient(self, problem: str, filters: Filters) -> Retrieval: ...


class SyntheticRepository:
    def __init__(self, path: Path | None = None):
        raw = (path or Path(__file__).with_name("preview_fixture.json")).read_bytes()
        payload = json.loads(raw)
        if payload["source_mode"] != "SYNTHETIC":
            raise ValueError("The fixture adapter accepts SYNTHETIC data only")
        self.revision = hashlib.sha256(raw).hexdigest()
        self._records = {item["case_id"]: item for item in payload["cases"]}
        if len(self._records) != len(payload["cases"]):
            raise ValueError("Duplicate fixture case ID")
        self._cases = {}
        for key, item in self._records.items():
            if not key.startswith("SYN-") or item["domain"] not in DOMAINS:
                raise ValueError("Invalid synthetic identity")
            source = copy.deepcopy(item["source_fields"])
            # Lossless schema mapping, not generation from the user's need.
            # Shared demonstration fields are explicitly authored in the fixture.
            source["parcours"] = {
                **copy.deepcopy(payload["parcours_demonstration"]),
                "use_case_id": key, "cas_utilisation": source["title"],
                "description_cas_utilisation": source["description"],
                "domaine_label": DOMAINS[item["domain"]], "intention": item["objective"],
                "secteur": " / ".join(item["sectors"]),
            }
            self._cases[key] = Case(
                key, item["domain"], item["objective"], tuple(item["sectors"]),
                source["title"], source["description"],
                hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                source,
            )
        self.provenance = {
            "source_mode": "SYNTHETIC", "catalogue_version": payload["version"],
            "catalogue_revision": self.revision, "case_count": len(self._cases),
            "coverage": "Uniquement ces cas fictifs ; aucun accès aux 1 021 cas v461.",
            "retrieval_engine": "Règles de tâches sur fixtures, sans LLM ni RAG de production.",
            "orientation_coverage": "Tous les cas de cette fixture uniquement.",
        }

    def sectors(self, domain: str) -> list[str]:
        if domain not in SECTEURS_PAR_DOMAINE:
            return []
        known = list(SECTEURS_PAR_DOMAINE[domain])
        for case in self._cases.values():
            if case.domain == domain:
                for sector in case.sectors:
                    if sector not in known and sector != MULTI_SECTOR:
                        known.append(sector)
        return known + [OTHER_SECTOR]

    def _sector_eligible(self, case: Case, sector: str | None) -> bool:
        return sector is None or MULTI_SECTOR in case.sectors or sector in case.sectors

    def objectives(self, domain: str, sector: str | None) -> list[tuple[str, str]]:
        return sorted({(case.objective_id, case.objective) for case in self._cases.values()
                       if case.domain == domain and self._sector_eligible(case, sector)},
                      key=lambda item: item[1])

    def get(self, case_id: str) -> Case | None:
        return self._cases.get(case_id)

    def eligible(self, case: Case, filters: Filters) -> bool:
        return (case.domain == filters.domain and case.objective_id == filters.objective
                and self._sector_eligible(case, filters.sector))

    @staticmethod
    def _affirmative_match(pattern: str, text: str) -> bool:
        for match in re.finditer(pattern, text):
            # Conservative fixture-only abstention: do not interpret a task or
            # prerequisite occurring in the scope of an explicit exclusion.
            clause = re.split(r"[.!?;\n,]|\b(?:mais|plutot)\b", text[:match.start()])[-1]
            if not re.search(r"\b(?:pas|sans|aucun|aucune|ni|non|eviter|exclure)\b", clause):
                return True
        return False

    def _matches(self, case: Case, problem: str) -> bool:
        item = self._records[case.case_id]
        text = normalize(problem)
        return (any(self._affirmative_match(pattern, text) for pattern in item["task_patterns"])
                and all(self._affirmative_match(r"\b" + re.escape(normalize(term)) + r"\b", text)
                        for term in item.get("required_context", [])))

    def search(self, problem: str, filters: Filters) -> Retrieval:
        candidates = tuple(case.case_id for case in self._cases.values()
                           if self.eligible(case, filters))
        results = tuple(key for key in candidates if self._matches(self._cases[key], problem))
        return Retrieval(filters.as_dict(), candidates, results, "synthetic-main")

    def orient(self, problem: str, filters: Filters) -> Retrieval:
        # One bounded catalogue pass, not calls to every objective. Keep the
        # sector constraint; alternatives are never added to the main results.
        candidates = tuple(case.case_id for case in self._cases.values()
                           if (case.domain != filters.domain or case.objective_id != filters.objective)
                           and self._sector_eligible(case, filters.sector))
        results = tuple(key for key in candidates if self._matches(self._cases[key], problem))
        return Retrieval({"search": "orientation", "sector": filters.sector,
                          "sector_policy": filters.as_dict()["sector_policy"]},
                         candidates, results, "synthetic-orientation")
