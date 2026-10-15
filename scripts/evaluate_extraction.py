#!/usr/bin/env python3
"""
Evaluate extraction quality on the hand labeled eval set (eval/).

Runs the real pipeline: EntityExtractor, then RelationExtractor on the
extracted entities. Scores entities and relations with micro averaged
precision, recall, and F1, writes results/eval_results.json, and
prints a table. The README quotes that JSON, not this terminal.

The LLM extractor is attempted on the same set. With no OPENAI_API_KEY
in the environment it records status "skipped" and NO metrics, by
design. LLM numbers only ever appear here after a real API run.

Usage:
    python scripts/evaluate_extraction.py [--out results/eval_results.json]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from knowledge_graph_explorer.entity_extractor import EntityExtractor
from knowledge_graph_explorer.relation_extractor import RelationExtractor
from knowledge_graph_explorer.llm_extractor import LLMExtractor

REPO = Path(__file__).resolve().parents[1]
SYMMETRIC = {"partner_of", "competes_with"}


def entity_key(text, entity_type):
    return (text.lower(), entity_type)


def relation_key(source, target, relation_type):
    if relation_type in SYMMETRIC and target.lower() < source.lower():
        source, target = target, source
    return (source.lower(), target.lower(), relation_type)


def prf(gold, predicted):
    tp = len(gold & predicted)
    fp = len(predicted - gold)
    fn = len(gold - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 4), "recall": round(recall, 4),
            "f1": round(f1, 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "results" / "eval_results.json"))
    args = ap.parse_args()

    eval_set = json.loads((REPO / "eval" / "eval_set.json").read_text())
    documents = eval_set["documents"]

    gold_entities, pred_entities = set(), set()
    gold_relations, pred_relations = set(), set()
    for doc in documents:
        doc_id = doc["id"]
        for e in doc["entities"]:
            gold_entities.add((doc_id,) + entity_key(e["text"], e["type"]))
        for r in doc["relations"]:
            gold_relations.add((doc_id,) + relation_key(r["source"], r["target"], r["type"]))

        extractor = EntityExtractor()
        entities = extractor.extract(doc["text"])
        for e in entities:
            pred_entities.add((doc_id,) + entity_key(e.text, e.entity_type))
        relations = RelationExtractor().extract(doc["text"], entities)
        for r in relations:
            pred_relations.add((doc_id,) + relation_key(r.source.text, r.target.text,
                                                        r.relation_type))

    entity_scores = prf(gold_entities, pred_entities)
    relation_scores = prf(gold_relations, pred_relations)

    # LLM mode: skipped unless a key exists and a real run succeeds.
    llm = LLMExtractor()
    llm_section = {"status": "skipped", "reason": "", "model": llm.model}
    probe = llm.extract("Probe sentence. Ada Lovelace was born in London.")
    if probe.status != "ok":
        llm_section["status"] = probe.status
        llm_section["reason"] = probe.reason
    else:
        llm_gold_e, llm_pred_e = set(), set()
        llm_gold_r, llm_pred_r = set(), set()
        for doc in documents:
            doc_id = doc["id"]
            for e in doc["entities"]:
                llm_gold_e.add((doc_id,) + entity_key(e["text"], e["type"]))
            for r in doc["relations"]:
                llm_gold_r.add((doc_id,) + relation_key(r["source"], r["target"], r["type"]))
            result = llm.extract(doc["text"])
            if result.status != "ok":
                llm_section = {"status": result.status, "reason": result.reason,
                               "model": llm.model}
                break
            for e in result.entities:
                llm_pred_e.add((doc_id,) + entity_key(e.text, e.entity_type))
            for r in result.relations:
                llm_pred_r.add((doc_id,) + relation_key(r.source.text, r.target.text,
                                                        r.relation_type))
        else:
            llm_section = {"status": "ok", "model": llm.model,
                           "entities": prf(llm_gold_e, llm_pred_e),
                           "relations": prf(llm_gold_r, llm_pred_r)}

    results = {
        "eval_set": "eval/eval_set.json",
        "documents": len(documents),
        "gold_entities": len(gold_entities),
        "gold_relations": len(gold_relations),
        "rule_based": {"entities": entity_scores, "relations": relation_scores},
        "llm": llm_section,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))

    print(f"documents: {len(documents)}  gold entities: {len(gold_entities)}  "
          f"gold relations: {len(gold_relations)}")
    print(f"rule based entities : P {entity_scores['precision']:.3f}  "
          f"R {entity_scores['recall']:.3f}  F1 {entity_scores['f1']:.3f}")
    print(f"rule based relations: P {relation_scores['precision']:.3f}  "
          f"R {relation_scores['recall']:.3f}  F1 {relation_scores['f1']:.3f}")
    print(f"llm mode: {llm_section['status']}"
          + (f" ({llm_section['reason']})" if llm_section.get("reason") else ""))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
