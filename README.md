# Knowledge Graph Explorer

A zero-dependency Python system that extracts entities and
relationships from text to build knowledge graphs, then analyzes and
visualizes them. Extraction quality is not asserted; it is measured
on a hand labeled eval set, and the misses are published next to the
scores.

> **Act 4, the Graph**, in a five part body of work built on one
> thesis: technology should increase human capability without taking
> human agency away.
>
> - Act 1, the Atlas: [supergravity](https://github.com/jthomas48896f/supergravity), how people learn.
> - Act 2, the Commons: [cohort](https://github.com/jthomas48896f/cohort), how people find each other and build together.
> - Act 3, the Machine: [neural-net-lab](https://github.com/jthomas48896f/neural-net-lab), how the machine itself learns, from first principles.
> - Act 5, the Guardrails: [lumen-faith-platform](https://github.com/jthomas48896f/lumen-faith-platform), how all of it stays safe, cited, and human governed.
>
> This act's problem family is information chaos and unorganized
> knowledge. Its north star metric is questions answered from
> organized public knowledge. No number is claimed for it yet; the
> eval below measures the extractor, not usage.
>
> The frame is the post AI renaissance, stated as aspiration and
> direction of travel, never as achievement: knowledge organized
> into structures that can be questioned and checked.

## Measured extraction quality

From `scripts/evaluate_extraction.py`, run 2026-10-15 against the
hand labeled set in `eval/` (8 documents, 63 gold entities, 31 gold
relations; labeling rules in `eval/README.md`). Full artifact:
`results/eval_results.json`.

| | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Entities (rule based) | 0.937 | 0.937 | 0.937 |
| Relations (rule based) | 0.473 | 0.839 | 0.605 |

Read those numbers the way they were earned:

- **Entity extraction is the strong half**, and the eval improved
  it. The first run scored recall 0.889; the misses exposed two
  real bugs (dates before 1900 were invisible to the year patterns;
  the capitalized-name pattern required a connector word, so plain
  two-word names like Pierre Curie never matched). Both are fixed,
  with regression tests, and both runs are on record.
- **Relation precision is the honest weakness.** Recall is high
  because the co-occurrence pass proposes a relation for almost
  every nearby entity pair, and precision pays for it: roughly half
  of the proposed relations are not stated in the text. The eval's
  labeling rule (a relation counts only if the text states it) is
  what makes that cost visible instead of hiding it.
- **The misses are named, not rounded away.** The system misses
  entities its gazetteers do not know (Warsaw, Armonk, Watson,
  iPhone), cannot follow pronouns across sentences ("He joined
  Microsoft" loses the works_for relation), and has documented
  type ambiguities the eval labels against it (Windows and iOS are
  labeled TECHNOLOGY; the gazetteer also lists them as
  organizations). Details: `eval/README.md` and the eval artifact.

## Hybrid extraction, honestly staged

The design is hybrid: rule based extraction always runs, offline,
with no dependencies, and an LLM mode
(`knowledge_graph_explorer/llm_extractor.py`) extracts through the
same type system for comparison on the same eval set.

**The LLM mode has not produced numbers in this environment, and
this README claims none.** With no `OPENAI_API_KEY` set, the mode
records status "skipped" in every eval artifact and returns nothing.
That behavior is itself under test
(`tests/test_extractors.py`). Set the key and rerun
`scripts/evaluate_extraction.py` and the same artifact gains an LLM
section measured the same way; until then, any LLM score for this
project would be invented, and invented numbers are the one thing
this portfolio does not publish.

## Features

- **Entity extraction**: PERSON, ORGANIZATION, LOCATION, DATE, and
  TECHNOLOGY entities via gazetteers, patterns, and heuristics
- **Relation extraction**: founded_by, located_in, works_for,
  acquired, developed, born_in, partner_of, competes_with, via verb
  patterns plus a co-occurrence pass whose cost the eval measures
- **LLM extraction mode**: optional, same schema, skips cleanly
  without a key (see above)
- **Knowledge graph**: typed nodes and edges, CRUD, JSON
  serialization, deduplication
- **Graph algorithms**: PageRank, centrality (betweenness, degree,
  closeness), community detection (Louvain), shortest path,
  connected components
- **Query engine**: a natural-ish query language for traversal
- **Visualization**: force-directed layout from scratch, matplotlib
  rendering
- **Built-in corpus**: 25+ paragraphs on tech companies, AI,
  computing history, and science

## Quick start

```bash
pip install -r requirements.txt
python main.py                                  # build and visualize a graph
python -m unittest discover -s tests            # extractor + eval tests
python scripts/evaluate_extraction.py           # the measured eval
```

Running `main.py` produces `knowledge_graph.json`,
`knowledge_graph.png`, `communities.png`, and
`subgraph_google.png`.

## Query examples

```python
from knowledge_graph_explorer.query_engine import QueryEngine

qe = QueryEngine(graph)
qe.execute("find all entities connected to Google")
qe.execute("path between Elon Musk and Apple")
qe.execute("entities of type PERSON connected to ORGANIZATION")
qe.execute("relations of type founded_by")
qe.execute("info about Tesla")
```

## Project structure

```
knowledge_graph_explorer/
    tokenizer.py           - Sentence/word tokenizer, POS-like tagging
    entity_extractor.py    - Rule based named entity recognition
    relation_extractor.py  - Verb pattern + co-occurrence relations
    llm_extractor.py       - Optional LLM mode (skips without a key)
    knowledge_graph.py     - Graph data structure, CRUD, serialization
    graph_algorithms.py    - PageRank, communities, paths, centrality
    query_engine.py        - Query language for graph traversal
    visualization.py       - Force-directed layout and rendering
    datasets.py            - Built-in text corpus (25+ paragraphs)
    main.py                - Pipeline: extract, build, analyze, visualize
eval/                      - Hand labeled eval set and labeling rules
scripts/evaluate_extraction.py
tests/test_extractors.py
results/eval_results.json
```

## Status and limitations

- Rule based extraction is a teaching-grade instrument: strong on
  gazetteer-known entities, weak on unknown names, pronouns, and
  anything the patterns do not reach. The eval numbers above are
  the current, dated measurement of exactly that.
- The eval set is smoke sized (8 documents). Growing it is a
  standing good first issue; see CONTRIBUTING.md.
- The co-occurrence relation pass trades precision for recall by
  design. A confidence threshold or a stated-ness filter is the
  obvious next experiment, and the eval exists to judge it.

## Requirements

- Python 3.8+
- NumPy, Matplotlib (the LLM mode needs only an API key and the
  standard library)
