# NS4KGE Extraction Pipeline

LLM-assisted pipeline that extracts structured negative-sampling information from scientific articles and builds an instantiated knowledge graph using the NS4KGE ontology.

## Contents
- `src/no_facts_pipeline/` contains the Python package and CLI entrypoints.
- `prompts/` contains the two extraction prompts used by the pipeline.
- `fixtures/` contains synthetic reviewer-safe inputs and expected structured data.
- `tests/` contains unit tests for parsing, URI normalization, and Turtle generation.
- `docs/reviewer_tutorial.md` gives a concise reviewer workflow from synthetic input to validation.

## Version
- Current artifact version: `v1.0.1`.

## Resource Availability
- Repository: `https://github.com/IlyesTebourski/ns4kge-extraction-pipeline`.
- Release: `v1.0.1`.
- Release date: 2026-05-13.
- License: Apache-2.0.
- Zenodo DOI: `https://doi.org/10.5281/zenodo.20160460`.
- Ontology artifact: `https://doi.org/10.5281/zenodo.20058306` and `https://github.com/IlyesTebourski/ns4kge-ontology`.
- KG artifact: `https://github.com/IlyesTebourski/ns4kge-kg`.

The repository contains code, prompts, tests, and synthetic fixtures. It does not redistribute source article text.

## Setup
This project uses `uv` and a `src/` layout.

```bash
uv sync
```

LLM calls load `.env` from the current working directory. Set the relevant key before running extraction:

```text
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

The default hosted LLM models wired in this release are:

- Claude pipeline: `claude-opus-4-6`.
- GPT pipeline: `gpt-4o`.

Reviewer-safe tests and postprocessing do not require API keys.

## Main Commands
Run one article with the dispatcher:

```bash
uv run nofacts-pipeline ../mds/EANS.md --model claude --output-dir ../ns4kge-kg/per_article --prompt-dir prompts
```

Run all local source articles, skipping articles that already have TTL output:

```bash
uv run nofacts-run-all ../mds --model claude --skip-existing --output-dir ../ns4kge-kg/per_article --prompt-dir prompts
```

Regenerate one per-article TTL from a corrected merged JSON:

```bash
uv run nofacts-postproc ../ns4kge-kg/per_article/eans_merged.json --output-dir ../ns4kge-kg/per_article
```

Assemble the populated KG from all per-article TTL files:

```bash
uv run nofacts-populate-onto --output-dir ../ns4kge-kg/per_article --ontology ../ns4kge-ontology/ontology/ns4kge_ontology.ttl --out ../ns4kge-kg/kg/ns4kge_populated.ttl
```

Validate the populated KG:

```bash
uv run nofacts-validate --data ../ns4kge-kg/kg/ns4kge_populated.ttl --shapes ../ns4kge-ontology/ontology/ns4kge_shapes.ttl
```

Run competency and diagnostic queries:

```bash
uv run nofacts-query --data ../ns4kge-kg/kg/ns4kge_populated.ttl
uv run nofacts-debug --data ../ns4kge-kg/kg/ns4kge_populated.ttl
```

## Inputs And Outputs
- Source article markdown is expected outside this repo, usually in local `../mds/`; do not publish full source papers unless rights allow it.
- Prompts are in `prompts/` and must keep returning strict JSON matching the existing schemas.
- Per-article output goes to an output directory as `<slug>_json1.json`, `<slug>_json2.json`, `<slug>_merged.json`, and `<slug>.ttl`.
- Per-article TTL intentionally has no prefix declarations; assemble with `nofacts-populate-onto` before RDF parsing or SHACL validation.

## Reviewer Workflow Without Private Source Text
Run unit tests:

```bash
uv run pytest
```

Regenerate a synthetic per-article TTL from the safe fixture:

```bash
mkdir -p /tmp/ns4kge-review/per_article
uv run nofacts-postproc fixtures/synthetic_merged.json --output-dir /tmp/ns4kge-review/per_article
```

Validate the released KG artifact, assuming the three sibling artifact repositories are checked out next to each other:

```bash
uv run nofacts-validate --data ../ns4kge-kg/kg/ns4kge_populated.ttl --shapes ../ns4kge-ontology/ontology/ns4kge_shapes.ttl
```

For a fuller tutorial, see `docs/reviewer_tutorial.md`.

## URI Policy
- Ontology classes and properties use `https://w3id.org/ns4kge/ontology#`.
- Generated KG instances use REST-like IRIs under `https://w3id.org/ns4kge/id/`, such as `article/eans`, `ns-method/entity-aware-negative-sampling`, and `configuration/eans/1`.
- The assembled KG declares `@base <https://w3id.org/ns4kge/id/>`, so per-article TTL files can use relative instance IRIs.

## Tests
```bash
uv run pytest
```

The fixture data is synthetic and safe to publish.

## Reproducibility Notes
- The code and prompts are versioned, but hosted LLM providers may change model behavior over time.
- The paper KG artifact was generated from local source article markdown that is not redistributed because of copyright boundaries.
- Exact per-file model provenance for the moved legacy KG outputs is incomplete and documented in the KG manifest.
- Reproducible structural checks are supported through synthetic fixtures, generated SHACL shapes, and the assembled KG validation command.

## Limitations
- Extraction quality depends on source document conversion quality, table structure, prompt behavior, and model behavior.
- The pipeline can produce extraction errors or omissions and should not be treated as a fully automatic ground-truth generator.
- LLM calls are not guaranteed to be deterministic across time, providers, or model revisions.
- Source article text is intentionally outside this repository; users must obtain source papers independently if they want to rerun the paper extraction from original text.

## Continuous Integration
The repository includes a GitHub Actions workflow that runs `uv run pytest` and `uv build` on pushes and pull requests.

## License
Pipeline code is licensed under Apache-2.0. Ontology and KG artifacts are separate repositories licensed under CC BY 4.0.
