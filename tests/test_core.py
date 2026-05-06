import json
from pathlib import Path

import pytest

from no_facts_pipeline.core import json_to_ttl, parse_json, uri


def test_parse_json_strips_markdown_fences():
    assert parse_json('```json\n{"ok": true}\n```') == {"ok": True}


def test_parse_json_rejects_non_json():
    with pytest.raises(json.JSONDecodeError):
        parse_json("not json")


def test_uri_normalizes_common_names():
    assert uri("FB15K-237") == "fb15k-237"
    assert uri("Hits@10 (%)") == "hits-10-percent"


def test_json_to_ttl_from_fixture():
    fixture = Path(__file__).parents[1] / "fixtures" / "synthetic_merged.json"
    merged = json.loads(fixture.read_text(encoding="utf-8"))
    ttl = json_to_ttl(merged, "synthetic")
    assert "<article/synthetic> rdf:type ns4kge:Article ." in ttl
    assert "<configuration/synthetic/1> ns4kge:result" in ttl
