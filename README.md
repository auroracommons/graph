# Graph

Mission: "Aurora Commons addresses the hierarchy of human needs through open source."

Motto: "Stand on the shoulders of giants."

One rule: "Raise the floor beneath everyone."

Advised by Groundskeeper.

A knowledge graph extraction system written in Python. The
extraction and graph core runs on the standard library alone; NumPy
and Matplotlib appear only in evaluation metrics and visualization.
Extraction quality is not asserted; it is measured on a hand labeled
eval set, and the misses are published next to the scores.

## The need


This project serves Layer 4: Shared truth. "Knowledge organized well enough to argue with. Claims that carry their evidence. Errors published, not buried." This repo serves that need by measuring its extraction on a hand labeled eval set and publishing the misses next to the scores.

Unmet, it looks like: decisions made about communities from scattered and invented data, arguments with no floor of agreed fact, institutions that cannot tell what they know from what they assume.

The full map: [The Ascent, a map of human needs](https://github.com/auroracommons/auroracommons/blob/main/NEEDS.md)

The research under this layer: [Foundations, Truth and shared knowledge](https://auroracommons.github.io/auroracommons/foundations.html#truth-and-shared-knowledge)

> **Graph, shared truth, Layer 4**, in The Ascent, built on one
> thesis: technology should increase human capability without taking
> human agency away.
>
> - Ground (the body): [ground](https://github.com/auroracommons/ground)
> - Still (the mind at peace): [still](https://github.com/auroracommons/still)
> - Atlas (learning): [atlas](https://github.com/auroracommons/atlas)
> - Cohort (belonging): [cohort](https://github.com/auroracommons/cohort)
> - Graph (shared truth, Layer 4): this repo
> - Machine (autonomy): [machine](https://github.com/auroracommons/machine)
> - Lumen (trust and meaning): [lumen](https://github.com/auroracommons/lumen)
>
> This act's problem family is information chaos and unorganized
> knowledge. Its north star metric is questions answered from
> organized public knowledge. No number is claimed for it yet; the
> eval below measures the extractor, not usage.
>
> The frame is the post AI renaissance, stated as aspiration and
> direction of travel, never as achievement: knowledge organized
> into structures that can be questioned and checked.

## What it is

### Hybrid extraction, honestly staged


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

### Features


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

### Quick start


```bash
pip install -r requirements.txt
python main.py                                  # build and visualize a graph
python -m unittest discover -s tests            # extractor + eval tests
python scripts/evaluate_extraction.py           # the measured eval
```

Running `main.py` produces `knowledge_graph.json`,
`knowledge_graph.png`, `communities.png`, and
`subgraph_google.png`.

### Query examples


```python
from knowledge_graph_explorer.query_engine import QueryEngine

qe = QueryEngine(graph)
qe.execute("find all entities connected to Google")
qe.execute("path between Elon Musk and Apple")
qe.execute("entities of type PERSON connected to ORGANIZATION")
qe.execute("relations of type founded_by")
qe.execute("info about Tesla")
```

### Project structure


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


### Requirements


- Python 3.8+
- NumPy, Matplotlib (the LLM mode needs only an API key and the
  standard library)

## The proof

### Measured extraction quality


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

### Status and limitations


- Rule based extraction is a teaching-grade instrument: strong on
  gazetteer-known entities, weak on unknown names, pronouns, and
  anything the patterns do not reach. The eval numbers above are
  the current, dated measurement of exactly that.
- The eval set is smoke sized (8 documents). Growing it is a
  standing good first issue; see CONTRIBUTING.md.
- The co-occurrence relation pass trades precision for recall by
  design. A confidence threshold or a stated-ness filter is the
  obvious next experiment, and the eval exists to judge it.

## Live demo

Live demo: https://auroracommons.github.io/graph/

## Contribute, human or agent


Pick a good first issue in this repo. Each one is sized in hours and written to be finishable by a newcomer.
Try the Eval Challenge against this repo's published extraction scores. Beat a baseline or document a real failure, with the run attached.
Adopt the extractor or the graph in your own work and report back what happened in real use, good or bad.

The full protocol: [The Open Table](https://github.com/auroracommons/auroracommons/blob/main/OPEN_TABLE.md). Verified work is credited in the public [Ledger](https://github.com/auroracommons/auroracommons/blob/main/LEDGER.md).

### Start with a prompt

For an AI agent:

```
You are an AI agent contributing to Graph. Run the Eval Challenge end to end.
Install with: pip install -r requirements.txt
Run the tests with: python -m unittest discover -s tests -v
Run the eval with: python scripts/evaluate_extraction.py --out /tmp/eval_results.json
Compare your run to the published baseline in The proof section above and in results/eval_results.json, measured on the hand labeled set in eval/.
Beat a baseline or document a real failure.
Attach the run to your pull request, keep one improvement per pull request, and name your operator.
```

For a human:

```
File a failure report as an issue and include the input text you ran.
Say what the extractor produced and what should have happened instead.
Attach the eval or test output if you have it.
```
