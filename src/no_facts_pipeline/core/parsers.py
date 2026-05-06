"""
core/parsers.py

Parsing utilities for raw LLM outputs.
"""

import json
import re


def parse_json(raw: str) -> dict:
    """
    Parse a JSON string returned by an LLM, stripping markdown code fences if present.
    Raises json.JSONDecodeError if the cleaned string is not valid JSON.
    """
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    return json.loads(cleaned)