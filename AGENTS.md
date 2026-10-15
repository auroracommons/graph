# AGENTS.md

Working agreement for any agent changing this repo. Read this first, then README.md and CONTRIBUTING.md, and `eval/README.md` before touching the extractor or the eval set.

## What this is
Knowledge Graph Explorer: knowledge graph extraction from text, steered by a hand labeled evaluation whose failures are published, not hidden.

## Commands
- Install: `pip install -r requirements.txt`
- Test: `python -m unittest discover -s tests -v`
- Eval: `python scripts/evaluate_extraction.py --out /tmp/eval_results.json`
- CI runs the tests and the labeled eval on every push

## House rules
- Evidence rule: a change ships with the run that proves it (the eval artifact, the test output), never code alone.
- Honesty rule: no invented metrics, ever. LLM extraction mode skips gracefully without an API key and the artifact says skipped; no LLM quality number may be written unless an LLM run produced it.
- One improvement per pass. Finish it, prove it, commit it.
- No placeholders. If something is a scaffold, label it a scaffold in the same breath that names it.
- Eval changes and code changes are judged together: if you change the extractor, rerun the eval and include the new artifact, even if the numbers got worse. Especially if the numbers got worse.

## External agents

You are welcome here as a contributor. Read OPEN_TABLE.md on the profile (https://github.com/thomassupergravity/thomassupergravity/blob/main/OPEN_TABLE.md) for the terms. The binding rules in one breath: evidence attached or it does not merge, one improvement per pull request, run this repo's commands and report the results, state that you are an agent and name your operator, never submit results you did not run.
