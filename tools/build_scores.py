#!/usr/bin/env python3
"""Build the measured result on the Graph page from results/eval_results.json.

One artifact, two layers, both written by this script so no number is kept
in two hand written copies:

- the surface layer (between the scores markers): plain words, counts in
  full sentences, and a table with plain headers;
- the layer for agents and builders (between the scores-tech markers):
  the exact table with precision, recall, and F1, the artifact file name,
  and the method note.

Run: python3 tools/build_scores.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- scores:begin -->"
END = "<!-- scores:end -->"
TECH_BEGIN = "<!-- scores-tech:begin -->"
TECH_END = "<!-- scores-tech:end -->"


def per100(value):
    return int(round(value * 100))


def surface_block(data):
    rule = data["rule_based"]
    ent = rule["entities"]
    rel = rule["relations"]
    docs = data["documents"]
    gold_ent = data["gold_entities"]
    gold_rel = data["gold_relations"]
    return """%s
  <p>Graph was checked on %d documents that people had labeled by hand. Those documents held %d named things, such as people, groups, places, and dates, and %d links stated between them.</p>
  <p>Of every 100 named things in the documents, Graph found %d and missed %d. Of every 100 links stated in the documents, Graph found %d and missed %d.</p>
  <p>Of every 100 named things Graph returned, %d were right. Of every 100 links Graph returned, %d were right.</p>
  <table class="scores-table">
    <thead><tr><th scope="col">What was looked for</th><th scope="col">Found right</th><th scope="col">Missed</th><th scope="col">Extra and wrong</th></tr></thead>
    <tbody>
    <tr><td>Named things in the text</td><td>%d</td><td>%d</td><td>%d</td></tr>
    <tr><td>Links stated in the text</td><td>%d</td><td>%d</td><td>%d</td></tr>
    </tbody>
  </table>
  <p>Key: Found right is how many Graph found that were truly there. Missed is how many were there and Graph did not find. Extra and wrong is how many Graph returned that were not there.</p>
%s""" % (BEGIN, docs, gold_ent, gold_rel,
         per100(ent["recall"]), 100 - per100(ent["recall"]),
         per100(rel["recall"]), 100 - per100(rel["recall"]),
         per100(ent["precision"]), per100(rel["precision"]),
         ent["tp"], ent["fn"], ent["fp"],
         rel["tp"], rel["fn"], rel["fp"], END)


def tech_row(name, scores):
    return ("<tr><td>%s</td><td>%.4f</td><td>%.4f</td><td>%.4f</td>"
            "<td>%d</td><td>%d</td><td>%d</td></tr>"
            % (name, scores["precision"], scores["recall"], scores["f1"],
               scores["tp"], scores["fp"], scores["fn"]))


def tech_block(data):
    rule = data["rule_based"]
    return """%s
  <p>Precision means the share of what the extractor returned that was right. Recall means the share of the hand labeled set that the extractor found. F1 means the single score that balances precision and recall.</p>
  <table class="scores-table">
    <thead><tr><th scope="col">What was pulled from the text</th><th scope="col">Precision</th><th scope="col">Recall</th><th scope="col">F1</th><th scope="col">Right</th><th scope="col">Wrong</th><th scope="col">Missed</th></tr></thead>
    <tbody>
    %s
    %s
    </tbody>
  </table>
  <p>Method: the extractor was run on the hand labeled set named in the artifact, %d documents with %d gold entities and %d gold relations. The artifact is results/eval_results.json in this repository. Right, wrong, and missed count items in that set.</p>
%s""" % (TECH_BEGIN, tech_row("Entities", rule["entities"]),
         tech_row("Relations", rule["relations"]), data["documents"],
         data["gold_entities"], data["gold_relations"], TECH_END)


def replace_block(page, begin, end, block, label):
    if begin not in page or end not in page:
        print("build_scores: %s markers not found" % label, file=sys.stderr)
        sys.exit(1)
    before, rest = page.split(begin, 1)
    _, after = rest.split(end, 1)
    return before + block + after


def main():
    data = json.loads(
        (ROOT / "results" / "eval_results.json").read_text(encoding="utf-8"))
    path = ROOT / "index.html"
    page = path.read_text(encoding="utf-8")
    page = replace_block(page, BEGIN, END, surface_block(data), "scores")
    page = replace_block(page, TECH_BEGIN, TECH_END, tech_block(data),
                         "scores-tech")
    path.write_text(page, encoding="utf-8")
    print("build_scores: wrote both layers from eval_results.json")


if __name__ == "__main__":
    main()
