# Module 8 readiness and evaluation

## Local validation

Run the focused tests and build the unified graph:

```powershell
python -m pytest tests/unit/test_fusion_engine.py -q
python run_fusion.py
```

The complete local stage sequence can be run with:

```powershell
python run_pipeline.py --input data/Luat_dat_dai_2024.docx --from-stage M1 --to-stage M8 --law-code 59/2024/QH15
```

M6 calls OpenRouter and may incur cost. A pipeline range containing M6 is
refused unless the caller explicitly passes `--allow-llm` and a positive
`--m6-limit`; optional repeated `--node-id` flags narrow the experiment:

```powershell
python run_pipeline.py --input data/Luat_dat_dai_2024.docx --from-stage M1 --to-stage M6 --allow-llm --m6-limit 10 --node-id article-26 --node-id article-28
```

For M6 experiments using already-produced M5/M4 files, bound the API run with
`run_llm_extraction.py --limit 10`; invoking that script calls OpenRouter.
To rank complex routed candidates locally without calling the API, run
`python scripts/sample_m6_candidates.py --limit 10`. Review the generated JSON
and command before choosing whether to launch the paid extraction.

The fusion output contains a `fusion_report`; potential legal conflicts are
warnings for expert review, not legal conclusions. A `RESOLVES_TO` edge is
created only when an explicit or anaphoric citation resolves uniquely within
the physical graph's document/law scope. Document-wide references such as
"Luật này" resolve to a synthetic `DOCUMENT` anchor, never to a chapter.
Out-of-scope citations and general legal scope are reported separately from
unresolved or ambiguous internal citations. SHACL runs without RDFS inference.
Hierarchy-cycle, hierarchy-level, sequence-level, edge-integrity, article
number, and semantic domain/range facts are precomputed in linear passes and
checked by SHACL property shapes; this avoids repeatedly executing expensive
SPARQL queries for every edge while preserving a SHACL conformance report.
The adapter accepts both the legacy
M7 `entities`/`relations` output and the newer M7 `active_nodes`/`concepts`/
`norms`/`active_edges` contract.

## Confidence evaluation

Generate reproducible, stratified review samples from the current UKG:

```powershell
python scripts/sample_fusion_eval.py --size 80 --seed 42
```

This writes sampled rows to `outputs/evaluation/fusion_confidence_gold_template.csv`
and `outputs/evaluation/fusion_quality_gold_template.csv`. The split is grouped
by source physical node to reduce train/test leakage. Sampling never invents
expert labels. Annotators should independently mark each sampled
relation as `label=1` (supported by its evidence and legal context) or `label=0`
(unsupported/incorrect). Keep the preassigned `split` unchanged to preserve the
source-grouped holdout. Do not treat
synthetic examples or unreviewed model output as gold labels.

For quality evaluation, create one `case_id` per evaluated case and task
(`relation_support`, `deontic_conflict`, or `reference_resolution`). The
`annotation` column accepts independent reviewer labels; when reviewers agree,
the evaluator can use that label directly. If they disagree, fill in the
adjudicated `expected` value. The evaluator reports pairwise Cohen's kappa.
For reference resolution,
compare the exact expected and predicted physical node IDs (use `UNRESOLVED`
when appropriate).

After expert annotation:

```powershell
python run_fusion_quality_eval.py outputs/evaluation/fusion_quality_gold.csv --task deontic_conflict --split test
python run_fusion_quality_eval.py outputs/evaluation/fusion_quality_gold.csv --task reference_resolution --split test
python run_fusion_quality_eval.py outputs/evaluation/fusion_quality_gold.csv --task relation_support --split test
python run_fusion_confidence_eval.py outputs/evaluation/fusion_confidence_gold.csv --fit --split train
python run_fusion_confidence_eval.py outputs/evaluation/fusion_confidence_gold.csv --split test
```

The report includes Brier score, expected calibration error, and precision and
recall at 0.8. Keep the test split untouched during fitting. Until a labeled
evaluation has been reviewed, edges carry `confidence_status` set to
`heuristic_uncalibrated`; do not use their values as calibrated probabilities.
The confidence formula is a bounded heuristic before fitting, not a calibrated
probability. `run_fusion.py` automatically loads a fitted calibration artifact
if it exists.

## Neo4j incremental apply

Set `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD`, then run:

```powershell
python run_fusion_delta.py previous_ukg.json current_ukg.json --database neo4j
```

The adapter uses a unique constraint on `UKG_NODE.id`, stable edge keys, and a
single write transaction. Neo4j stores edge properties as JSON strings to
preserve arbitrary graph property structures. Verify the target database and
backup policy before applying production deltas; removed UKG nodes are detached
and deleted.

## Release gate still requiring external evidence

Code tests and SHACL checks cannot substitute for a legal gold set. A release
claim of semantic accuracy requires expert-labeled conflict, reference
resolution, and relation-support examples from multiple laws, with held-out
evaluation results and documented annotation agreement.
