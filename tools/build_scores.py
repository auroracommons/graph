#!/usr/bin/env python3
"""Build the scores table on the Graph page from results/eval_results.json.

The table and the prose beside it read the same artifact, so they cannot
drift apart. Run this after an eval, and commit the page it writes.

Run: python3 tools/build_scores.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- scores:begin -->"
END = "<!-- scores:end -->"


def row(name, scores):
    return ("<tr><td>%s</td><td>%.4f</td><td>%.4f</td><td>%.4f</td>"
            "<td>%d</td><td>%d</td><td>%d</td></tr>"
            % (name, scores["precision"], scores["recall"], scores["f1"],
               scores["tp"], scores["fp"], scores["fn"]))


def main():
    data = json.loads(
        (ROOT / "results" / "eval_results.json").read_text(encoding="utf-8"))
    rule = data["rule_based"]
    table = """%s
  <table class="scores-table">
    <thead><tr><th scope="col">What was pulled from the text</th><th scope="col">Precision</th><th scope="col">Recall</th><th scope="col">F1</th><th scope="col">Right</th><th scope="col">Wrong</th><th scope="col">Missed</th></tr></thead>
    <tbody>
    %s
    %s
    </tbody>
  </table>
  <p>Key: precision is the share of what the extractor returned that was right. Recall is the share of the gold set it found. F1 is the balance of the two. Right, wrong, and missed count gold items in the eval set named above: %d documents, %d gold entities, and %d gold relations, in results/eval_results.json in this repository.</p>
%s""" % (BEGIN, row("Entities", rule["entities"]),
         row("Relations", rule["relations"]), data["documents"],
         data["gold_entities"], data["gold_relations"], END)

    path = ROOT / "index.html"
    page = path.read_text(encoding="utf-8")
    if BEGIN in page and END in page:
        before, rest = page.split(BEGIN, 1)
        _, after = rest.split(END, 1)
        page = before + table + after
    else:
        anchor = "  </section>"
        idx = page.find('<h2>Measured result</h2>')
        if idx < 0:
            print("build_scores: Measured result section not found",
                  file=sys.stderr)
            sys.exit(1)
        end = page.find(anchor, idx)
        page = page[:end] + table + "\n" + page[end:]
    path.write_text(page, encoding="utf-8")
    print("build_scores: wrote the scores table from eval_results.json")


if __name__ == "__main__":
    main()
