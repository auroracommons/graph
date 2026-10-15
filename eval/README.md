# Extraction eval set

`eval_set.json` is a small, hand labeled evaluation set for this
project's extractors: 8 short documents about technology and science
history, with entities and relations labeled by hand. It exists so the
README can publish precision and recall that come from a real run
(`scripts/evaluate_extraction.py`, results in `results/eval_results.json`)
instead of adjectives.

## Labeling rules

- Entities use the surface form as written in the text, typed as
  PERSON, ORGANIZATION, LOCATION, DATE, or TECHNOLOGY.
- Relations use only the eight types the system supports
  (founded_by, located_in, works_for, acquired, developed, born_in,
  partner_of, competes_with), in the direction conventions documented
  in `knowledge_graph_explorer/llm_extractor.py`.
- When a text states a location as a city, state pair ("headquartered
  in Mountain View, California"), both the city and the state get a
  located_in label.
- A relation is labeled only when the text states it. Facts that are
  true in the world but not stated in the document do not count, and an
  extractor that emits them loses precision. This is the rule that
  makes the co-occurrence relations cost something, as they should.
- Known hard case, labeled deliberately: "Windows" is labeled
  TECHNOLOGY in the Microsoft document. The gazetteer also lists
  Windows as an organization, so the rule based extractor disagrees.
  The label stands, the disagreement is published, and the eval is
  more honest for containing a case the system gets wrong.

## Scoring

Micro averaged precision, recall, and F1 over the whole set. Entities
match on (text, type), case insensitive. Relations match on
(source, target, type); the two symmetric types (partner_of,
competes_with) match in either direction. Relations are scored at the
pipeline level: a gold relation whose endpoint entities the entity
extractor missed counts as missed, because that is what a user of the
pipeline experiences.

## Size, stated plainly

8 documents, 63 gold entities, 31 gold relations. That is a smoke
sized eval, useful for regression tracking and honest comparison
between the rule based and LLM extractors, not a benchmark. Growing
it is a standing good first issue (see CONTRIBUTING.md).
