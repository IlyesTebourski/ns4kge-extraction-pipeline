"""Assemble per-article TTL files into one populated NS4KGE graph."""

import argparse
import os
from pathlib import Path

from no_facts_pipeline.core.uris import KG_ID_BASE, KG_IRI, KG_VERSION_IRI, ONTOLOGY_IRI, ONTOLOGY_NS

PREFIXES = f"""\
@prefix :          <{KG_ID_BASE}> .
@prefix owl:       <http://www.w3.org/2002/07/owl#> .
@prefix rdf:       <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml:       <http://www.w3.org/XML/1998/namespace> .
@prefix xsd:       <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs:      <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns4kge:    <{ONTOLOGY_NS}> .
@prefix bibo:      <http://purl.org/ontology/bibo/> .
@prefix void:      <http://rdfs.org/ns/void#> .
@prefix dcterms:   <http://purl.org/dc/terms/> .
@prefix dcat:      <http://www.w3.org/ns/dcat#> .
@prefix vann:      <http://purl.org/vocab/vann/> .
@base <{KG_ID_BASE}> .
"""

KG_METADATA = f"""\
<{KG_IRI}> rdf:type void:Dataset , dcat:Dataset ;
    dcterms:title "NS4KGE Knowledge Graph" ;
    dcterms:description "Knowledge graph of negative sampling methods for knowledge graph embeddings extracted from scientific articles." ;
    dcterms:creator "Ilyes Tebourski" , "Pierre-Henri Paris" , "Nicoleta Preda" , "Fatiha Sais" ;
    dcterms:issued "2026-05-06"^^xsd:date ;
    dcterms:bibliographicCitation "Tebourski, I., Paris, P.-H., Preda, N., & Sais, F. (2026). NS4KGE Knowledge Graph (v1.0.0-paper). Zenodo. https://doi.org/10.5281/zenodo.20058972"@en ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    dcterms:conformsTo <{ONTOLOGY_IRI}> ;
    dcterms:hasVersion "v1.0.0-paper" ;
    dcterms:identifier "10.5281/zenodo.20058972" , <{KG_VERSION_IRI}> ;
    dcat:landingPage <https://github.com/IlyesTebourski/ns4kge-kg> ;
    rdfs:seeAlso <https://github.com/IlyesTebourski/ns4kge-kg> , <https://doi.org/10.5281/zenodo.20058972> , <https://doi.org/10.5281/zenodo.20058306> .
"""


def strip_prefixes(ttl_text: str) -> str:
    lines = []
    for line in ttl_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("@prefix") or stripped.startswith("@base"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def load_ontology_body(path: str | Path) -> str:
    path = Path(path)
    if not path.is_file():
        print(f"[WARN] Ontology file not found: {str(path)!r} - skipping schema inclusion.")
        return ""
    return strip_prefixes(path.read_text(encoding="utf-8"))


def slug_from_path(path: str | Path) -> str:
    return Path(path).stem


def populate(
    output_dir: str | Path = "../ns4kge-kg/per_article",
    ontology: str | Path = "../ns4kge-ontology/ontology/ns4kge_ontology.ttl",
    out: str | Path = "../ns4kge-kg/kg/ns4kge_populated.ttl",
) -> Path:
    output_dir = Path(output_dir)
    ontology = Path(ontology)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    article_files = sorted(output_dir.glob("*.ttl"))
    article_files = [f for f in article_files if os.path.abspath(f) != os.path.abspath(out)]

    if not article_files:
        raise SystemExit(f"[ERROR] No .ttl files found in {str(output_dir)!r}.")

    print(f"Found {len(article_files)} article TTL file(s):")
    for f in article_files:
        print(f"  - {f}")

    sections = [PREFIXES, KG_METADATA]
    ontology_body = load_ontology_body(ontology)
    if ontology_body:
        sections.append(
            "##############################################################\n"
            "#  ONTOLOGY SCHEMA\n"
            "##############################################################\n\n"
            + ontology_body
        )

    for filepath in article_files:
        slug = slug_from_path(filepath)
        body = strip_prefixes(filepath.read_text(encoding="utf-8"))
        banner = (
            "\n\n"
            "################################################################\n"
            f"#  ARTICLE: {slug.upper()}\n"
            "################################################################\n\n"
        )
        sections.append(banner + body)

    out.write_text("\n".join(sections), encoding="utf-8")
    print(f"\nPopulated ontology written to: {out}")
    print(f"Articles included: {', '.join(slug_from_path(f) for f in article_files)}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", "--output_dir", default="../ns4kge-kg/per_article")
    parser.add_argument("--ontology", default="../ns4kge-ontology/ontology/ns4kge_ontology.ttl")
    parser.add_argument("--out", default="../ns4kge-kg/kg/ns4kge_populated.ttl")
    args = parser.parse_args()
    populate(output_dir=args.output_dir, ontology=args.ontology, out=args.out)


if __name__ == "__main__":
    main()
