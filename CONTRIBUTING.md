# Contributing to Graph

Contributions are welcome, and the door is kept visibly open: there
is always at least one good first issue available. The house rule
is the evidence rule: a contribution ships with the run that proves
it (the eval artifact, the test output), not just the code.

## Setup

```bash
pip install -r requirements.txt
python -m unittest discover -s tests     # extractor + eval harness tests
python scripts/evaluate_extraction.py    # writes results/eval_results.json
```

## Good first issues (sized in hours)

- **Label two eval documents (1 to 2 hours).** Write two short
  documents in a domain the set does not cover and label their
  entities and relations under the rules in `eval/README.md`.
  Growing the eval set is the highest value small contribution
  this project has.
- **Add a gazetteer regression test (under an hour).** Pick an
  entity the extractor currently misses (the eval diagnostics name
  several) and add a test that pins the desired behavior before
  anyone fixes it.
- **Measure a confidence threshold (1 to 2 hours).** The
  co-occurrence pass trades precision for recall. Run the eval with
  relations below a confidence cutoff filtered out, and report the
  precision/recall curve in the PR. Data first; whether to adopt
  the cutoff is a separate decision.
- **Document a failure (under an hour).** Find a sentence where the
  extractor confidently produces a wrong entity or relation, and
  file it as an issue with the sentence and the wrong output.
  Diagnosis is a contribution.

## Ground rules

- No invented metrics, ever. If the LLM mode did not run, the
  artifact says skipped and the README says so. A PR that adds an
  unmeasured quality claim does not merge.
- Eval changes and code changes are judged together: if you change
  the extractor, rerun the eval and include the new artifact, even
  if the numbers got worse. Especially if the numbers got worse.
- Labeling rules live in `eval/README.md`. If a label seems wrong,
  argue with the rule in the open rather than quietly relabeling.

## Pull requests

Keep them small and single purpose. State the evidence in the PR
description: what you ran and what it showed. Contributors are
named in release notes.
