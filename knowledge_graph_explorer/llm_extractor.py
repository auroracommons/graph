"""
LLM based extraction mode for the knowledge graph explorer.

This is the second half of the hybrid extraction design: the rule based
extractors (entity_extractor.py, relation_extractor.py) always run,
offline, with no dependencies. This module optionally asks a large
language model to extract entities and relations from the same text,
so the two approaches can be compared on the labeled eval set in
eval/.

Honesty contract, enforced in code:

- No API key in the environment means the mode SKIPS. It returns a
  result with status "skipped" and produces no entities, no relations,
  and no metrics. Nothing in this repository ever presents an LLM
  number that did not come from a real API run.
- The only provider wired up is OpenAI, via a plain HTTPS call with the
  standard library (urllib), key read from OPENAI_API_KEY. Set
  KG_LLM_MODEL to override the model name.
- API or parse failures are reported as status "error" with the reason,
  never silently converted into empty extraction success.
"""

import json
import os
import urllib.request
import urllib.error
from typing import List, Optional

from .entity_extractor import Entity
from .relation_extractor import Relation

API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"

ENTITY_TYPES = ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "TECHNOLOGY"]
RELATION_TYPES = [
    "founded_by", "located_in", "works_for", "acquired",
    "developed", "born_in", "partner_of", "competes_with",
]

PROMPT = """Extract entities and relations from the text below.

Entity types allowed: {entity_types}
Relation types allowed: {relation_types}

Relation direction conventions:
- founded_by: source is the founder (PERSON), target is the ORGANIZATION.
- located_in: source is the thing located, target is the LOCATION.
- works_for: source is the PERSON, target is the ORGANIZATION.
- acquired: source is the acquirer, target is the acquired ORGANIZATION.
- developed: source created or built the target.
- born_in: source is the PERSON, target is the LOCATION or DATE.
- partner_of, competes_with: symmetric, either order is fine.

Reply with JSON only, in exactly this shape:
{{"entities": [{{"text": "...", "type": "..."}}],
  "relations": [{{"source": "...", "target": "...", "type": "..."}}]}}

Only include entities and relations the text actually states. Do not
invent anything.

Text:
{text}
"""


class ExtractionResult:
    """Outcome of one extraction attempt, including the skip case."""

    def __init__(self, status: str, entities=None, relations=None,
                 reason: str = ""):
        self.status = status  # "ok" | "skipped" | "error"
        self.entities = entities or []
        self.relations = relations or []
        self.reason = reason

    def __repr__(self):
        return (f"ExtractionResult(status={self.status!r}, "
                f"entities={len(self.entities)}, "
                f"relations={len(self.relations)}, reason={self.reason!r})")


class LLMExtractor:
    """Entity and relation extraction via an LLM API call."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("KG_LLM_MODEL", DEFAULT_MODEL)

    def is_available(self) -> bool:
        return bool(self.api_key)

    def extract(self, text: str) -> ExtractionResult:
        if not self.is_available():
            return ExtractionResult(
                status="skipped",
                reason="OPENAI_API_KEY is not set; LLM extraction did not run. "
                       "No LLM results are reported anywhere in this repo "
                       "unless a real run produced them.")

        prompt = PROMPT.format(
            entity_types=", ".join(ENTITY_TYPES),
            relation_types=", ".join(RELATION_TYPES),
            text=text)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (urllib.error.URLError, KeyError, IndexError,
                json.JSONDecodeError) as exc:
            return ExtractionResult(status="error", reason=f"{type(exc).__name__}: {exc}")

        entities: List[Entity] = []
        by_text = {}
        for item in parsed.get("entities", []):
            text_value = str(item.get("text", "")).strip()
            type_value = str(item.get("type", "")).strip().upper()
            if not text_value or type_value not in ENTITY_TYPES:
                continue
            ent = Entity(text_value, type_value, confidence=1.0)
            entities.append(ent)
            by_text[text_value] = ent

        relations: List[Relation] = []
        for item in parsed.get("relations", []):
            src = by_text.get(str(item.get("source", "")).strip())
            tgt = by_text.get(str(item.get("target", "")).strip())
            rtype = str(item.get("type", "")).strip()
            if src is None or tgt is None or rtype not in RELATION_TYPES:
                continue
            relations.append(Relation(src, tgt, rtype, confidence=1.0))

        return ExtractionResult(status="ok", entities=entities, relations=relations)
