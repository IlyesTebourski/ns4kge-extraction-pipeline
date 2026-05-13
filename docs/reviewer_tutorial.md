# Reviewer Tutorial

This tutorial shows how to verify the NS4KGE extraction pipeline without publishing or requiring the private source article markdown used for the paper KG artifact.

## Prerequisites
- Python 3.11 or newer.
- `uv` installed.
- The companion ontology and KG repositories checked out as sibling folders when running cross-artifact validation.

Expected sibling layout:

```text
ns4kge-ontology/
ns4kge-extraction-pipeline/
ns4kge-kg/
```

## Install
Run from `ns4kge-extraction-pipeline/`:

```bash
uv sync
```

## Run Tests
```bash
uv run pytest
```

Expected result for this release: all tests pass.

## Synthetic No-API Workflow
The `fixtures/` folder contains synthetic data that is safe to publish. This path exercises postprocessing and Turtle generation without using hosted LLM APIs.

```bash
mkdir -p /tmp/ns4kge-review/per_article
uv run nofacts-postproc fixtures/synthetic_merged.json --output-dir /tmp/ns4kge-review/per_article
```

The command writes:

```text
/tmp/ns4kge-review/per_article/synthetic.ttl
```

The generated per-article TTL intentionally omits prefixes. This mirrors the paper artifact workflow, where per-article TTL files are assembled into a complete graph before validation.

## Validate The Released KG
Assuming the companion ontology and KG repositories are present as siblings:

```bash
uv run nofacts-validate --data ../ns4kge-kg/kg/ns4kge_populated.ttl --shapes ../ns4kge-ontology/ontology/ns4kge_shapes.ttl
```

Expected result for this release: `Conforms: True`.

## Query The Released KG
```bash
uv run nofacts-query --data ../ns4kge-kg/kg/ns4kge_populated.ttl
uv run nofacts-debug --data ../ns4kge-kg/kg/ns4kge_populated.ttl
```

These commands reproduce the competency-query and diagnostic outputs stored in the KG artifact reports.

## Optional LLM Workflow
To run extraction from a markdown article, set the relevant API key in `.env` or the environment.

```text
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

Run the synthetic markdown fixture through Claude:

```bash
uv run nofacts-pipeline fixtures/synthetic_article.md --model claude --output-dir /tmp/ns4kge-review/per_article --prompt-dir prompts
```

Run the synthetic markdown fixture through GPT:

```bash
uv run nofacts-pipeline fixtures/synthetic_article.md --model gpt --output-dir /tmp/ns4kge-review/per_article --prompt-dir prompts
```

Default models in this release:

- Claude: `claude-opus-4-6`.
- GPT: `gpt-4o`.

## Paper Artifact Boundary
- The source article markdown used for the paper KG artifact is not included in this repository.
- The generated KG repository records source titles, source DOIs or URLs where available, local source filenames, and source-file checksums.
- Reviewers can validate the released KG and run all tests without access to the private source article text.
