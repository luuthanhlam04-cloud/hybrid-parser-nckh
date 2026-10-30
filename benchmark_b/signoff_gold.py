"""Finalize the audited gold only after a named human reviewer attests review."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .review_gold import OUTPUT as CANDIDATE, SIGNOFF_CSV, STATUS as AI_STATUS
from .prepare import sha


FINAL = Path("datasets/benchmarks/benchmark_B_v03.json")


def signoff(reviewer: str, review_date: str) -> dict:
    if not reviewer.strip():
        raise ValueError("A named human reviewer is required")
    payload = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    with SIGNOFF_CSV.open(encoding="utf-8-sig", newline="") as stream:
        approvals = list(csv.DictReader(stream))
    if len(approvals) != 50 or {row["question_id"] for row in approvals} != {q["question_id"] for q in payload["questions"]}:
        raise ValueError("Human sign-off CSV must contain exactly the same 50 question IDs")
    incomplete = [row["question_id"] for row in approvals if row["human_decision"] != "APPROVED" or not row["reviewer"] or not row["review_date"]]
    if incomplete:
        raise ValueError(f"Human sign-off is incomplete for: {', '.join(incomplete)}")
    if payload["metadata"].get("status") != AI_STATUS:
        raise ValueError("Candidate status is not ready for human sign-off")
    for question in payload["questions"]:
        question["annotation_status"] = "HUMAN_REVIEWED"
        for fact in question.get("atomic_annotations", []):
            if fact["review_status"] == AI_STATUS:
                fact["review_status"] = "REVIEWED"
        for key in ("required_exceptions_annotations", "forbidden_claims_annotations"):
            for annotation in question.get(key, []):
                if annotation["review_status"] == AI_STATUS:
                    annotation["review_status"] = "REVIEWED"
        for group in question.get("accepted_chain_sets", []):
            for path in group["required_paths"]:
                for step in path["steps"]:
                    if step["review_status"] == AI_STATUS:
                        step["review_status"] = "REVIEWED"
    payload["metadata"]["version"] = "0.3"
    payload["metadata"]["status"] = "HUMAN_REVIEWED"
    payload["metadata"]["review_provenance"]["human_signoff"] = {
        "reviewer": reviewer.strip(),
        "review_date": review_date,
        "attestation": "Reviewed all 50 questions, gold locators, facts, exceptions, forbidden claims and reference chains.",
        "signoff_csv_sha256": sha(SIGNOFF_CSV),
    }
    FINAL.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"output": str(FINAL), "questions": len(payload["questions"]), "reviewer": reviewer, "status": "HUMAN_REVIEWED"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--review-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--confirm-reviewed-all-50", action="store_true", required=True)
    args = parser.parse_args()
    print(json.dumps(signoff(args.reviewer, args.review_date), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
