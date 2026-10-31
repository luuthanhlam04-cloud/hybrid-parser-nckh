"""Align retrieved text only. Never search question gold or generated answers."""
from .contracts import EvidenceItem


def align(source_id, text, rank, mapping, score=None, stage='retrieved', article_scope=None):
    rows = mapping['mappings']
    direct = [(loc,row) for loc,row in rows.items() if row['physical_node_id'] == source_id]
    # Text must be present in returned evidence, not just inferred from a document ID.
    hits = [(loc,row) for loc,row in rows.items() if row['text'].strip() and len(row['text'].strip()) >= 15 and row['text'].strip() in text and (article_scope is None or loc.split(':')[1][1:]==article_scope)]
    # Identical text at several locations cannot establish a unique provenance.
    counts={row['text']:sum(other['text']==row['text'] for _,other in hits) for _,row in hits}
    hits=[(loc,row) for loc,row in hits if counts[row['text']]==1]
    if direct:
        loc,row = direct[0]
        # Norm summaries do not automatically contain the entire source provision.
        if row['text'].strip() and row['text'].strip() in text:
            hits=[(loc,row)]
    locations = list(dict.fromkeys(loc for loc,row in hits))
    return EvidenceItem(rank=rank, raw_source_id=source_id, canonical_locators=locations,
        granularity='POINT' if any(':D' in x for x in locations) else 'CLAUSE' if any(':K' in x for x in locations) else 'ARTICLE',
        alignment_status='EXACT' if locations else 'UNRESOLVED', retrieval_score=score, text=text, stage=stage).model_dump()


def hybrid_evidence(result, mapping):
    if result.get('expanded_evidence') is not None:
        def from_candidates(rows, stage):
            output=[]
            known=mapping['mappings']
            for candidate in rows:
                locator=candidate.get('canonical_locator')
                mapped=bool(locator and locator in known)
                output.append(EvidenceItem(
                    rank=len(output)+1,
                    raw_source_id=str(candidate.get('node_id') or 'UNRESOLVED'),
                    canonical_locators=[locator] if mapped else [],
                    granularity='POINT' if locator and ':D' in locator else 'CLAUSE' if locator and ':K' in locator else 'ARTICLE',
                    alignment_status='EXACT' if mapped else 'UNRESOLVED',
                    retrieval_score=candidate.get('rank_score'),
                    text=str(candidate.get('text') or ''),
                    stage=stage,
                ).model_dump())
            return output
        return (
            from_candidates(result.get('expanded_evidence',[]),'expanded'),
            from_candidates(result.get('context_evidence',[]),'generation_context'),
        )
    evidence = []
    context = result.get('context','')
    for record in result.get('retrieval_records', []):
        if record.get('anchor_id'):
            text = record.get('evidence') or record.get('anchor_text') or ''
            evidence.append(align(record['anchor_id'], str(text), len(evidence)+1, mapping, stage='retrieved'))
        for node in record.get('nodes', []):
            p=node.get('properties',{}); text=p.get('text') or p.get('title') or ''
            evidence.append(align(node['id'],text,len(evidence)+1,mapping,stage='retrieved'))
    # The actual bounded context is evaluated separately from all retrieved records.
    return evidence, [align('m10_context',context,1,mapping,stage='generation_context')]


def hybrid_paths(records,mapping):
    reverse={row['physical_node_id']:loc for loc,row in mapping['mappings'].items()}
    paths=[]
    for record in records:
        steps=[]
        for edge in record.get('relationships',[]):
            source=reverse.get(edge.get('source_id')); target=reverse.get(edge.get('target_id'))
            if not source or not target: continue
            kind=edge['type']
            if kind=='BELONG_TO':
                source,target=target,source; kind='PARENT_CHILD_CONTEXT'
            elif kind in {'REFERS_TO','REFERENCE_TO'}: kind='DIRECT_REFERENCE'
            elif kind not in {'DIRECT_REFERENCE','REQUIRES_CONDITION_FROM','EXCEPTION_REFERENCE','INHERITS_RIGHTS_OBLIGATIONS','EXTERNAL_REFERENCE'}: continue
            steps.append(dict(source=source,relation_type=kind,target=target))
        if steps: paths.append(dict(steps=steps))
    return paths
