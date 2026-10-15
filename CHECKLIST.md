# The 110 percent checklist: Knowledge Graph Explorer

Bedrock alignment: Layer 4, Shared truth. Aligned October 15, 2026 (see "The need" in the README and NEEDS.md in the profile repo).
State as of October 15, 2026. Every line carries its evidence; a line without evidence does not count as done. This file is maintained by the evolution pass.

## 100 percent: completeness
- [x] Every file of the verified local publish tree present on GitHub, proven by tree diff at launch (October 14 to 15, 2026)
- [x] README accurate against the code. The opening claim was corrected October 15, 2026 after an import scan: the extraction and graph core is standard library only; NumPy and Matplotlib serve evaluation metrics and visualization only
- [x] LICENSE present
- [x] COLLABORATE.md present
- [x] CONTRIBUTING.md present
- [x] CI workflow present

## The extra 10 percent
- [x] CI green on GitHub runners (verified October 15, 2026)
- [x] Repo description and topics set (description states the verified eval scores)
- [x] Good first issues open: #1 label two eval documents in a new domain, #2 document a failure (both labeled good first issue, sized in hours)
- [x] Tagged release: v0.1.0, first verified baseline (published, marked Latest)
- [x] Live demo: https://thomassupergravity.github.io/knowledge-graph-explorer/ (render verified October 15, 2026)
- [x] Fresh baseline rerun October 15, 2026: 7 tests OK; eval on 8 documents, 63 gold entities, 31 gold relations: entities F1 0.936, relations F1 0.605, LLM mode skipped (no API key; no LLM metrics claimed anywhere in this repo)

## Working agreements
- AGENTS.md in this repo governs how changes are made and proven here.
