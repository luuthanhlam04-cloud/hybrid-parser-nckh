"""CLI for independent, reproducible Benchmark B runs."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from .corpus import DEFAULT_CORPUS_DIR, build_clean_text_corpus, write_article_corpus
from .costs import CostLedger
from .dataset import DEFAULT_DATASET, load_questions, validate_dataset
from .evaluation import evaluate_record, summarise, write_review_csv
from .systems import HybridUKGSystem, LightRAGSystem
from .prepare import V2, MAP, prepare, verify_mapping, sha
from .structural_metrics import evaluate, aggregate
from .review import template, scores as review_scores
from .llm_judge import LLMJudge, DEFAULT_JUDGE_MODEL
from .events import EventLog


OUTPUT_ROOT = Path("outputs/benchmark_b")
FINAL_GOLD = Path("datasets/benchmarks/benchmark_B_v03.json")


def get_system(name: str, *, mode: str = "AUTO_FUSION") -> Any:
    if name == "hybrid":
        return HybridUKGSystem(OUTPUT_ROOT / "hybrid", mode=mode)
    if name == "lightrag":
        return LightRAGSystem(OUTPUT_ROOT / "lightrag")
    raise ValueError(f"Unknown system: {name}")


def load_or_prepare_corpus() -> list[dict[str, Any]]:
    corpus_path = DEFAULT_CORPUS_DIR / "chapter_iii_articles.json"
    if not corpus_path.is_file():
        write_article_corpus()
    return json.loads(corpus_path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def run_benchmark(
    system_name: str,
    *,
    limit: int | None,
    top_k: int,
    mode: str,
    run_id=None,
    dataset_path: str | Path = FINAL_GOLD,
    judge_model: str | None = DEFAULT_JUDGE_MODEL,
    question_ids: set[str] | None = None,
) -> dict[str, Any]:
    system = get_system(system_name, mode=mode)
    if run_id:
        system.output_dir = OUTPUT_ROOT / system_name / run_id
        if isinstance(system, LightRAGSystem):
            system.workspace = system.output_dir / 'workspace'
            from .events import EventLog
            system.events = EventLog(system.output_dir / 'api_events.jsonl',system.name,run_id)
    dataset_path = Path(dataset_path)
    dataset_report = validate_dataset(dataset_path)
    if dataset_report.get("status") != "HUMAN_REVIEWED":
        raise ValueError("Benchmark run requires the HUMAN_REVIEWED v0.3 gold dataset")
    questions = load_questions(dataset_path)
    verify_mapping(json.loads(MAP.read_text(encoding='utf-8')),questions)
    system.output_dir.mkdir(parents=True,exist_ok=True)
    if (system.output_dir / 'answers.jsonl').exists(): raise ValueError('Run already exists; use another --run-id')
    if limit is not None:
        questions = questions[:limit]
    if question_ids:
        unknown=question_ids-{question['question_id'] for question in questions}
        if unknown:
            raise ValueError(f"Unknown or excluded question IDs: {sorted(unknown)}")
        questions=[question for question in questions if question['question_id'] in question_ids]
    results: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        for question in questions:
            result = system.answer(question, top_k=top_k)
            results.append(result)
            with (system.output_dir / 'answers.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(result,ensure_ascii=False)+'\n')
    finally:
        if hasattr(system, "close"):
            system.close()
    output_dir = system.output_dir
    write_jsonl(output_dir / "answers.jsonl", results)
    judge_summary = None
    if judge_model:
        judge = LLMJudge(output_dir, model=judge_model, run_id=f"{run_id}:judge")
        try:
            decisions, judge_summary = judge.judge_all(questions, results)
        finally:
            judge.close()
        for result, decision in zip(results, decisions, strict=True):
            result["human_review"] = review_scores(
                next(q for q in questions if q["question_id"] == result["question_id"]),
                decision,
            )
            result["llm_judge_provenance"] = {
                "reviewer": decision["reviewer"],
                "reviewer_type": decision["reviewer_type"],
                "prompt_version": decision["prompt_version"],
            }
    scores = [evaluate_record(question, result) for question, result in zip(questions, results, strict=True)]
    structural = [evaluate(q,r) for q,r in zip(questions,results,strict=True)]
    structural_report=aggregate(structural)
    for name,item in structural_report.items():
        item['eligible_question_ids']=[q['question_id'] for q,m in zip(questions,structural,strict=True) if m[name]['status']!='not_applicable']
    write_jsonl(output_dir / "per_question_metrics.jsonl", scores)
    deterministic_metrics = summarise(scores)
    if judge_model:
        deterministic_metrics["legal_correctness"] = f"llm_judged:{judge_model}"
    query_cost=system.ledger.to_dict() if isinstance(system, LightRAGSystem) else aggregate_hybrid_usage(results)
    jev_cost=system.jev_cost_summary() if isinstance(system, HybridUKGSystem) else None
    unresolved_context=sum(
        item.get('alignment_status')=='UNRESOLVED'
        for result in results for item in (result.get('context_evidence') or [])
    )
    report = {
        "system": system.name,
        "questions_run": len(results),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "metrics": deterministic_metrics,
        "structural_metrics": structural_report,
        "dataset_sha256": sha(dataset_path),
        "physical_graph_sha256": sha('outputs/physical_graphs/physical_graph.json'),
        "query_cost_ledger": query_cost,
        "jev_cost_ledger": jev_cost,
        "cost_separation": {
            "query_answer_model": query_cost,
            "jev_routing_and_gating": jev_cost,
            "llm_judge": judge_summary,
        },
        "provenance_audit": {
            "context_evidence_items": sum(len(result.get('context_evidence') or []) for result in results),
            "context_evidence_unresolved": unresolved_context,
            "all_context_items_mapped_or_marked_unresolved": all(
                item.get('alignment_status') in {'EXACT','UNRESOLVED'}
                for result in results for item in (result.get('context_evidence') or [])
            ),
            "gold_fields_passed_to_m10": False,
        },
        "dataset": str(dataset_path),
        "dataset_status": dataset_report.get("status"),
        "llm_judge": judge_summary,
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if judge_model is None:
        write_review_csv(questions, results, output_dir / "human_review.csv")
        template(questions,output_dir / 'review_decisions.json')
    write_jsonl(output_dir / 'structural_metrics.jsonl',[dict(question_id=q['question_id'],metrics=m) for q,m in zip(questions,structural,strict=True)])
    return report


def judge_existing_answers(
    answers_path: str | Path,
    *,
    dataset_path: str | Path = FINAL_GOLD,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    rejudge_ids: set[str] | None = None,
) -> dict[str, Any]:
    answers_path = Path(answers_path)
    output_dir = answers_path.parent
    dataset_path = Path(dataset_path)
    dataset_report = validate_dataset(dataset_path)
    if dataset_report.get("status") != "HUMAN_REVIEWED":
        raise ValueError("LLM judging requires the HUMAN_REVIEWED v0.3 gold dataset")
    questions = load_questions(dataset_path)
    by_id = {question["question_id"]: question for question in questions}
    raw_results = [json.loads(line) for line in answers_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    result_by_id = {result["question_id"]: result for result in raw_results}
    if len(raw_results) != 50 or set(result_by_id) != set(by_id):
        raise ValueError("Rejudge requires exactly one answer for each of the 50 gold questions")
    results = [result_by_id[question["question_id"]] for question in questions]
    judge = LLMJudge(output_dir, model=judge_model, run_id=f"{output_dir.name}:judge-v6-targeted")
    try:
        decisions, judge_summary = judge.judge_all(
            questions, results, force_question_ids=rejudge_ids,
        )
    finally:
        judge.close()
    # A failed/resumed judge run may have more than one run_id in the same durable ledger.
    # The final benchmark cost must include every paid judge attempt, including invalid-schema retries.
    judge_event_path = output_dir / "judge_api_events.jsonl"
    judge_events = [
        json.loads(line) for line in judge_event_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("phase") == "judge"
    ] if judge_event_path.is_file() else []
    judge_summary["all_run_attempts"] = {
        "calls": len(judge_events),
        "prompt_tokens": sum(event.get("prompt_tokens") or 0 for event in judge_events),
        "completion_tokens": sum(event.get("completion_tokens") or 0 for event in judge_events),
        "known_provider_cost_usd": sum(event.get("provider_cost_usd") or 0 for event in judge_events),
        "missing_usage_calls": sum(
            event.get("prompt_tokens") is None or event.get("completion_tokens") is None
            for event in judge_events
        ),
        "missing_cost_calls": sum(event.get("provider_cost_usd") is None for event in judge_events),
    }
    for result, question, decision in zip(results, questions, decisions, strict=True):
        result["human_review"] = review_scores(question, decision)
        result["llm_judge_provenance"] = {
            "reviewer": decision["reviewer"],
            "reviewer_type": decision["reviewer_type"],
            "prompt_version": decision["prompt_version"],
        }
    structural = [evaluate(q, r) for q, r in zip(questions, results, strict=True)]
    structural_report = aggregate(structural)
    for name, item in structural_report.items():
        item["eligible_question_ids"] = [
            q["question_id"] for q, metrics in zip(questions, structural, strict=True)
            if metrics[name]["status"] != "not_applicable"
        ]
    write_jsonl(
        output_dir / "structural_metrics.jsonl",
        [dict(question_id=q["question_id"], metrics=m) for q, m in zip(questions, structural, strict=True)],
    )
    report_path = output_dir / "metrics.json"
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        # Resume path: answers completed but the original run stopped during judging.
        # Reconstruct the deterministic report without rerunning M10, Jev, or generation.
        query_cost = aggregate_hybrid_usage(results)
        jev_cost = EventLog(
            output_dir / "jev_api_events.jsonl", "hybrid_ukg", output_dir.name,
        ).summary(phase="jev", scope="m10_jev_routing_and_gating")
        unresolved_context = sum(
            item.get("alignment_status") == "UNRESOLVED"
            for result in results for item in (result.get("context_evidence") or [])
        )
        report = {
            "system": "hybrid_ukg",
            "questions_run": len(results),
            "metrics": summarise([
                evaluate_record(question, result)
                for question, result in zip(questions, results, strict=True)
            ]),
            "dataset_sha256": sha(dataset_path),
            "physical_graph_sha256": sha("outputs/physical_graphs/physical_graph.json"),
            "query_cost_ledger": query_cost,
            "jev_cost_ledger": jev_cost,
            "cost_separation": {
                "query_answer_model": query_cost,
                "jev_routing_and_gating": jev_cost,
                "llm_judge": judge_summary,
            },
            "provenance_audit": {
                "context_evidence_items": sum(len(result.get("context_evidence") or []) for result in results),
                "context_evidence_unresolved": unresolved_context,
                "all_context_items_mapped_or_marked_unresolved": all(
                    item.get("alignment_status") in {"EXACT", "UNRESOLVED"}
                    for result in results for item in (result.get("context_evidence") or [])
                ),
                "gold_fields_passed_to_m10": False,
            },
            "dataset": str(dataset_path),
            "dataset_status": dataset_report.get("status"),
            "recovered_after_judge_interruption": True,
        }
    report["structural_metrics"] = structural_report
    report["llm_judge"] = judge_summary
    report["metrics"]["legal_correctness"] = f"llm_judged:{judge_model}"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "answers": len(results),
        "judge": judge_summary,
        "metrics": str(report_path),
        "structural_metrics": str(output_dir / "structural_metrics.jsonl"),
    }


def extract_m6(run_id,limit):
    from .events import EventLog
    from src.llm_extraction.structured_extractor import StructuredExtractor
    directory=OUTPUT_ROOT/'hybrid'/run_id
    if directory.exists(): raise ValueError('Run directory exists; choose a new run ID')
    directory.mkdir(parents=True)
    log=EventLog(directory/'api_events.jsonl','hybrid_m6',run_id)
    (directory/'manifest.json').write_text(json.dumps(dict(run_id=run_id,scope='M6 extraction only',physical_graph_sha256=sha('outputs/physical_graphs/physical_graph.json'),clean_text_sha256=sha('outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt'),candidates_sha256=sha('outputs/candidate_nodes/routing_candidates.json'),limit=limit),indent=2)+'\n',encoding='utf-8')
    extractor=StructuredExtractor('outputs/candidate_nodes/routing_candidates.json','outputs/physical_graphs/physical_graph.json',event_log=log)
    try:
        result=extractor.run_extraction(limit=limit)
        extractor.export(result,str(directory/'semantic_extraction.json'))
    finally:
        (directory/'extraction_cost.json').write_text(json.dumps(log.summary(),indent=2)+'\n',encoding='utf-8')
    return log.summary()


def aggregate_hybrid_usage(results: list[dict[str, Any]]) -> dict[str, Any]:
    ledger = CostLedger("openai/gpt-4o-mini")
    for result in results:
        ledger.add_usage("query", result.get("usage"))
    return ledger.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark B: independent Hybrid Parser/UKG and LightRAG experiments")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate the fixed 50-question dataset")
    validate_parser.add_argument("--dataset", default=str(FINAL_GOLD))
    subparsers.add_parser("prepare-corpus", help="build the common corpus from physical_graph.json")
    subparsers.add_parser('prepare-v02')
    m6=subparsers.add_parser('extract-m6')
    m6.add_argument('--run-id',required=True)
    m6.add_argument('--limit',type=int,default=0)
    score=subparsers.add_parser('score-v02')
    score.add_argument('--answers',required=True)
    score.add_argument('--reviews')
    judge_parser=subparsers.add_parser('judge',help='LLM-judge an existing complete answer file')
    judge_parser.add_argument('--answers',required=True)
    judge_parser.add_argument('--dataset',default=str(FINAL_GOLD))
    judge_parser.add_argument('--judge-model',default=DEFAULT_JUDGE_MODEL)
    judge_parser.add_argument('--rejudge-id',action='append',default=[])
    index_parser = subparsers.add_parser("index", help="prepare an individual system index")
    index_parser.add_argument("--system", choices=["hybrid", "lightrag"], required=True)
    index_parser.add_argument("--fresh", action="store_true", help="only applies to LightRAG and deletes its isolated workspace")
    index_parser.add_argument('--run-id',required=True)
    index_parser.add_argument('--dataset',default=str(FINAL_GOLD))
    run_parser = subparsers.add_parser("run", help="answer and score questions using an already-indexed system")
    run_parser.add_argument("--system", choices=["hybrid", "lightrag"], required=True)
    run_parser.add_argument("--limit", type=int)
    run_parser.add_argument('--run-id',required=True)
    run_parser.add_argument("--top-k", type=int, default=5)
    run_parser.add_argument("--mode", choices=["A", "B", "AUTO", "AUTO_FUSION"], default="AUTO_FUSION", help="Hybrid M10 retrieval mode")
    run_parser.add_argument('--dataset',default=str(FINAL_GOLD))
    run_parser.add_argument('--judge-model',default=DEFAULT_JUDGE_MODEL)
    run_parser.add_argument('--skip-judge',action='store_true')
    run_parser.add_argument('--question-id',action='append',default=[],help='Run selected IDs only (repeatable; evaluation harness only)')
    args = parser.parse_args()

    if args.command == 'prepare-v02':
        print(json.dumps(prepare(),indent=2)); return
    if args.command == 'extract-m6':
        print(json.dumps(extract_m6(args.run_id,args.limit),indent=2)); return
    if args.command == 'score-v02':
        questions=load_questions(V2)
        verify_mapping(json.loads(MAP.read_text(encoding='utf-8')),questions)
        by_id={q['question_id']:q for q in questions}
        results=[json.loads(line) for line in Path(args.answers).read_text(encoding='utf-8').splitlines()]
        if len({r['question_id'] for r in results})!=len(results): raise ValueError('Duplicate answers are not independent questions')
        reviews={r['question_id']:r for r in json.loads(Path(args.reviews).read_text(encoding='utf-8'))} if args.reviews else {}
        rows=[]
        for result in results:
            q=by_id[result['question_id']]
            result['human_review']=review_scores(q,reviews.get(q['question_id'],{}))
            rows.append(dict(question_id=q['question_id'],metrics=evaluate(q,result)))
        target=Path(args.answers).parent
        write_jsonl(target/'structural_metrics.jsonl',rows)
        report=aggregate([r['metrics'] for r in rows])
        for name,item in report.items(): item['eligible_question_ids']=[r['question_id'] for r in rows if r['metrics'][name]['status']!='not_applicable']
        (target/'structural_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2)); return
    if args.command == 'judge':
        print(json.dumps(judge_existing_answers(
            args.answers, dataset_path=args.dataset, judge_model=args.judge_model,
            rejudge_ids=set(args.rejudge_id),
        ), ensure_ascii=False, indent=2)); return

    if args.command == "validate":
        print(json.dumps(validate_dataset(args.dataset), ensure_ascii=False, indent=2))
        return
    if args.command == "prepare-corpus":
        print(json.dumps(write_article_corpus(), ensure_ascii=False, indent=2))
        return
    if args.command == "index":
        dataset_report=validate_dataset(args.dataset)
        if dataset_report.get('status')!='HUMAN_REVIEWED':
            raise ValueError('Benchmark index requires the HUMAN_REVIEWED v0.3 gold dataset')
        verify_mapping(json.loads(MAP.read_text(encoding='utf-8')),load_questions(args.dataset))
        if args.system == "lightrag":
            corpus = build_clean_text_corpus()
        else:
            write_article_corpus()
            corpus = load_or_prepare_corpus()
        system = get_system(args.system)
        system.output_dir=OUTPUT_ROOT / args.system / args.run_id
        if isinstance(system, LightRAGSystem):
            from .events import EventLog
            system.workspace=system.output_dir/'workspace'
            system.events=EventLog(system.output_dir/'api_events.jsonl',system.name,args.run_id)
        try: print(json.dumps(system.index(corpus, fresh=args.fresh), ensure_ascii=False, indent=2))
        finally:
            if hasattr(system,'close'): system.close()
        return
    if args.top_k<1 or args.limit is not None and args.limit<1: parser.error('top-k and limit must be positive')
    print(json.dumps(run_benchmark(
        args.system, limit=args.limit, top_k=args.top_k, mode=args.mode, run_id=args.run_id,
        dataset_path=args.dataset, judge_model=None if args.skip_judge else args.judge_model,
        question_ids=set(args.question_id) or None,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
