# Contributing to NS4KGE

This repository (`ns4kge-extraction-pipeline`) contains the Python tooling used to
extract, assemble, validate, and query the NS4KGE knowledge graph. This guide
explains how to use the pipeline to add a paper to the knowledge graph and how to
propose changes.

## Related repositories

- `ns4kge-ontology` — reusable OWL ontology and SHACL shapes.
- `ns4kge-extraction-pipeline` — this repository: Python tooling for extraction, assembly, validation, and querying.
- `ns4kge-kg` — generated KG artifact: assembled RDF, per-article outputs, provenance, and reports.

The commands below assume the three repositories are cloned side by side in the same parent folder.

## How to propose a change

Contributions are made through pull requests:

1. Fork this repository and create a branch for your change.
2. Make your changes following the conventions below.
3. Check that the pipeline runs end to end (populate, validate, query) without errors.
4. Open a pull request describing the change.

To report an extraction error or ask a question, open an issue rather than a pull request.

## Adding a new paper to the knowledge graph

1. Run the extraction pipeline on the article PDF. Source article text is **not** committed, for copyright reasons.
2. Add the generated per-article outputs under `per_article/` in the `ns4kge-kg` repository.
3. Record the source in `provenance/sources.csv` (title, year, source DOI/URL if available, local filename, SHA-256 checksum).

## Rebuilding and validating

From this repository's folder:

```bash
uv run nofacts-populate-onto \
  --output-dir ../ns4kge-kg/per_article \
  --ontology ../ns4kge-ontology/ontology/ns4kge_ontology.ttl \
  --out ../ns4kge-kg/kg/ns4kge_populated.ttl

uv run nofacts-validate \
  --data ../ns4kge-kg/kg/ns4kge_populated.ttl \
  --shapes ../ns4kge-ontology/ontology/ns4kge_shapes.ttl

uv run nofacts-query --data ../ns4kge-kg/kg/ns4kge_populated.ttl
```

A change is acceptable when SHACL validation passes and the query reports regenerate without errors.

## Conventions

- Entity IRIs use the base `https://w3id.org/ns4kge/id/`; do not invent ad-hoc IRIs.
- Canonical identifiers are snake_case (e.g. `dataset_fb15k237`, `model_transe`).
- Keep missing fields absent rather than filling nulls.
- Write commit messages in the imperative mood.

## Releasing

Bump the version tag, update `provenance/manifest.json` in the KG repository, refresh `reports/`, and publish a new archival DOI on Zenodo.

## License

The pipeline code is licensed under Apache-2.0. Generated KG data and provenance are licensed under CC BY 4.0. Contributions are accepted under the same terms.
