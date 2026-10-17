#!/usr/bin/env python3
"""
Retrieval integration demo (added October 17, 2026), GraphRAG style.

Why this exists: the eval measures extraction (what the pipeline pulls
out of one document). It did not measure the step a reader actually
takes next: build one graph from many documents and retrieve an answer
from it. This demo runs that step end to end on the standing eval
corpus, with the repo's own extractors, KnowledgeGraph, and
QueryEngine, and measures it against the gold labels:

- For every eval document with at least one gold relation, it asks
  "neighbors of <source>" for the first gold relation's source and
  checks whether the gold target is among the retrieved neighbors.
- It also asks "path between <source> and <target>" and checks
  whether a path comes back.

A miss means the merged graph cannot answer a question whose answer
the gold labels say is in the corpus: an extraction miss upstream, a
merge that lost the edge, or a query the engine cannot route. The
per query outcomes are written to results/retrieval_demo.json with
the misses named, and the README quotes that file, not this terminal.

Usage:
    python scripts/retrieval_demo.py [--out results/retrieval_demo.json]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from knowledge_graph_explorer.entity_extractor import EntityExtractor
from knowledge_graph_explorer.relation_extractor import RelationExtractor
from knowledge_graph_explorer.knowledge_graph import KnowledgeGraph
from knowledge_graph_explorer.query_engine import QueryEngine

REPO = Path(__file__).resolve().parents[1]


def result_text(result):
    return json.dumps(result.data, default=str).lower() if result.data is not None else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/retrieval_demo.json")
    args = ap.parse_args()

    docs = json.loads((REPO / "eval" / "eval_set.json").read_text(encoding="utf-8"))["documents"]

    extractor = EntityExtractor()
    relation_extractor = RelationExtractor()
    kg = KnowledgeGraph()
    for doc in docs:
        entities = extractor.extract(doc["text"])
        relations = relation_extractor.extract(doc["text"], entities)
        kg.build_from_extractions(entities, relations)
    stats = kg.get_statistics()

    qe = QueryEngine(kg)
    rows = []
    for doc in docs:
        if not doc.get("relations"):
            continue
        rel = doc["relations"][0]
        source, target = rel["source"], rel["target"]
        neighbors = qe.execute(f"neighbors of {source}")
        path = qe.execute(f"path between {source} and {target}")
        rows.append({
            "doc": doc["id"],
            "gold_relation": rel,
            "neighbors_query": f"neighbors of {source}",
            "target_in_neighbors": target.lower() in result_text(neighbors),
            "path_query": f"path between {source} and {target}",
            "path_found": bool(path.data),
        })

    n = len(rows)
    summary = {
        "queries": n,
        "target_in_neighbors": sum(r["target_in_neighbors"] for r in rows),
        "target_in_neighbors_rate": round(sum(r["target_in_neighbors"] for r in rows) / n, 4) if n else 0,
        "path_found": sum(r["path_found"] for r in rows),
        "path_found_rate": round(sum(r["path_found"] for r in rows) / n, 4) if n else 0,
    }
    artifact = {
        "corpus": "eval/eval_set.json, 22 documents, extracted with the repo's rule based pipeline and merged into one KnowledgeGraph",
        "graph": {"nodes": stats["node_count"], "edges": stats["edge_count"]},
        "summary": summary,
        "rows": rows,
        "note": "Queries are derived from the gold labels, one per document with a gold relation. A miss is published in rows, not averaged away.",
    }
    out = REPO / args.out
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"graph: {stats['node_count']} nodes, {stats['edge_count']} edges from {len(docs)} documents")
    print(f"neighbors: gold target retrieved in {summary['target_in_neighbors']} of {n} queries ({summary['target_in_neighbors_rate']})")
    print(f"paths: path found in {summary['path_found']} of {n} queries ({summary['path_found_rate']})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
