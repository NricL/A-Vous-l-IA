"""Structural/source gates, not a substitute for semantic editorial review."""
import argparse
import json
from pathlib import Path
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CLAIMS = ("gain", "deliverable", "horizon", "useful_when", "tradeoff")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Evidence(StrictModel):
    field: Literal["title", "description", "first_action", "guardrails"]
    quote: str = Field(min_length=5, max_length=600)


class Claim(StrictModel):
    text: str | None
    evidence: list[Evidence]
    unknown_reason: str | None = None

    @model_validator(mode="after")
    def justified_or_unknown(self):
        if self.text is None:
            if not self.unknown_reason or not self.unknown_reason.strip() or self.evidence:
                raise ValueError("Unknown claim needs a reason and no evidence-shaped fallback")
        else:
            if not self.text.strip() or len(self.text) > 360 or not self.evidence or self.unknown_reason:
                raise ValueError("Authored claim needs bounded text and exact source evidence")
            if re.search(r"\d|[%€$]|<[^>]*>", self.text):
                raise ValueError("Claims must not convert example numbers into value promises or contain HTML")
            if re.search(r"\bgaranti\w*|\bcertifi\w*|sans erreur|conformité acquise", self.text, re.I):
                raise ValueError("Unsupported assurance or certification language")
            if re.search(r"(?:envoi|diffusion|publication|décision)\s+automatique|"
                         r"(?:déployé|déployée|opérationnel|opérationnelle)\b|"
                         r"\ben production\b", self.text, re.I):
                raise ValueError("First-output hypotheses must not claim autonomous or deployed operation")
        return self


class EditorialCase(StrictModel):
    case_id: str = Field(pattern=r"^UC-\d{4}$")
    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    review_status: Literal["authored_source_reviewed"]
    horizon_kind: Literal["first_reviewed_output", "after_setup_and_validation", "after_comparison", "unknown"]
    claims: dict[str, Claim]
    review_note: str = Field(min_length=12, max_length=500)

    @model_validator(mode="after")
    def complete_review(self):
        if set(self.claims) != set(CLAIMS):
            raise ValueError("Every value field must be evaluated, including explicit unknowns")
        if (self.horizon_kind == "unknown") != (self.claims["horizon"].text is None):
            raise ValueError("Unknown horizon must remain explicitly unknown")
        return self


def validate_rows(rows, sources):
    known = {row["case_id"]: row for row in sources}
    validated, seen = [], set()
    for raw in rows:
        row = EditorialCase.model_validate(raw)
        if row.case_id in seen or row.case_id not in known:
            raise ValueError("Duplicate or unknown source identity")
        seen.add(row.case_id)
        source = known[row.case_id]
        if row.source_fingerprint != source["source_fingerprint"]:
            raise ValueError(f"{row.case_id}: source fingerprint mismatch")
        for name, claim in row.claims.items():
            for evidence in claim.evidence:
                if evidence.quote not in source["fields"][evidence.field]:
                    raise ValueError(f"{row.case_id}/{name}: source quote not found")
        validated.append(row.model_dump())
    return validated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    args = parser.parse_args()
    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    if isinstance(sources, dict):
        sources = sources["cases"]
    rows = json.loads(args.draft.read_text(encoding="utf-8"))
    checked = validate_rows(rows, sources)
    print(json.dumps({"structural_source_gate": "passed", "evaluated_cases": len(checked),
                      "unknown_fields": sum(c["text"] is None for row in checked for c in row["claims"].values()),
                      "semantic_review_not_proven_by_this_gate": True}))
