"""Reproducible v0.2 migration. Original v0.1 is never overwritten."""
import hashlib
import json
from pathlib import Path
from .contracts import CanonicalLocator, AtomicFact, ReferenceStep
from .dataset import DEFAULT_DATASET, load_dataset
from .corpus import DEFAULT_GRAPH

V2 = Path('datasets/benchmarks/benchmark_B_v02.json')
MAP = Path('datasets/benchmarks/benchmark_b_locator_map.json')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_mapping(graph_path=DEFAULT_GRAPH):
    nodes = json.loads(Path(graph_path).read_text(encoding='utf-8'))['nodes']
    by_id = {n['id']: n for n in nodes}
    mappings = {}
    for node in nodes:
        if not set(node['labels']) & {'ARTICLE', 'CLAUSE', 'POINT'}:
            continue
        ancestry, seen, current = [], set(), node
        while current:
            if current['id'] in seen:
                raise ValueError('Cyclic physical hierarchy')
            seen.add(current['id']); ancestry.append(current)
            current = by_id.get(current['properties'].get('parent_id'))
        props = {}
        for ancestor in ancestry:
            p, labels = ancestor['properties'], ancestor['labels']
            if 'ARTICLE' in labels: props['article'] = str(p['number'])
            if 'CLAUSE' in labels: props['clause'] = str(p['number'])
            if 'POINT' in labels: props['point'] = str(p['marker'])
        locator = CanonicalLocator(**props).canonical_locator
        if locator in mappings: raise ValueError(f'Duplicate locator: {locator}')
        p = node['properties']
        mappings[locator] = dict(physical_node_id=node['id'], node_type=next(x for x in node['labels'] if x in {'ARTICLE','CLAUSE','POINT'}), parent_locator=locator.rsplit(':',1)[0] if ':K' in locator else None, text=p.get('text') or '', text_sha256=hashlib.sha256((p.get('text') or '').encode()).hexdigest(), source_start_idx=p.get('start_idx'), source_end_idx=p.get('end_idx'))
    return dict(benchmark_version='B-v0.2', physical_graph_sha256=sha(graph_path), mappings=mappings)


def verify_mapping(mapping, questions, graph_path=DEFAULT_GRAPH):
    if mapping['physical_graph_sha256'] != sha(graph_path): raise ValueError('Physical graph changed: regenerate mapping')
    regenerated = make_mapping(graph_path)
    if mapping['mappings'] != regenerated['mappings']: raise ValueError('Locator/text mapping was modified or is stale')
    missing = {g['canonical_locator'] for q in questions for g in q['gold_locations']} - set(mapping['mappings'])
    if missing: raise ValueError(f'Unmapped gold: {sorted(missing)}')


def prepare():
    data, mapping = load_dataset(), make_mapping()
    for q in data['questions']:
        for g in q['gold_locations']:
            g['node_id'] = mapping['mappings'].get(g['canonical_locator'], {}).get('physical_node_id')
        locators = [g['canonical_locator'] for g in q['gold_locations'] if g['role'] != 'scope_boundary']
        q['acceptable_evidence_sets'] = [locators] if locators else []
        q['hierarchy_requirements'] = dict(parent_context=[x for x in locators if ':D' not in x], child_evidence=[x for x in locators if ':D' in x])
        paths = []
        for chain in q['reference_chain']:
            steps = []
            for source, target in zip(chain, chain[1:]):
                # Hierarchy is mechanically decidable; legal semantic labels require review.
                kind = 'PARENT_CHILD_CONTEXT' if target.startswith(source + ':') else 'DIRECT_REFERENCE'
                step = ReferenceStep(source=source, target=target, relation_type=kind).model_dump()
                step['review_status'] = 'STRUCTURAL' if kind == 'PARENT_CHILD_CONTEXT' else 'HUMAN_REVIEW_REQUIRED'
                steps.append(step)
            paths.append({'steps': steps})
        # All branches in v0.1 remain jointly required. Additional groups represent alternatives.
        q['accepted_chain_sets'] = [{'required_paths': paths}] if paths else []
        facts = []
        for f in q['atomic_facts_detailed']:
            facts.append(AtomicFact(fact_id=f['fact_id'], text=f['fact'], role='UNREVIEWED', evidence_any_of=f.get('evidence_locators', [])).model_dump())
        q['atomic_annotations'] = facts
        for field, role in [('required_exceptions','EXCEPTION'), ('forbidden_claims','FORBIDDEN_CLAIM')]:
            q[field + '_annotations'] = [dict(annotation_id=f"{q['question_id']}_{role}_{i}", text=text, role=role, supporting_locators=[], candidate_locators=locators, review_status='HUMAN_REVIEW_REQUIRED') for i,text in enumerate(q[field],1)]
    data['metadata'].update(version='0.2-draft', status='REQUIRES_HUMAN_LEGAL_REVIEW', source_v01_sha256=sha(DEFAULT_DATASET), physical_graph_sha256=mapping['physical_graph_sha256'])
    verify_mapping(mapping, data['questions'])
    for path, payload in [(V2,data), (MAP,mapping)]:
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return dict(questions=len(data['questions']), gold_occurrences=sum(len(q['gold_locations']) for q in data['questions']), mapped_locators=len(mapping['mappings']), chain_questions=sum(bool(q['accepted_chain_sets']) for q in data['questions']), facts=sum(len(q['atomic_annotations']) for q in data['questions']), status=data['metadata']['status'])

if __name__ == '__main__': print(json.dumps(prepare(), indent=2))
