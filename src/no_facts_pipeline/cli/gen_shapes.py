"""Generate SHACL shapes from the NS4KGE ontology file."""

import argparse
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, OWL, RDF, RDFS, URIRef

from no_facts_pipeline.core.uris import ONTOLOGY_NS

OWL_EXACT = URIRef("http://www.w3.org/2002/07/owl#exactCardinality")
OWL_MIN = URIRef("http://www.w3.org/2002/07/owl#minCardinality")
OWL_MAX = URIRef("http://www.w3.org/2002/07/owl#maxCardinality")


def generate_shapes(
    ontology_path: str | Path = "../ns4kge-ontology/ontology/ns4kge_ontology.ttl",
    shapes_path: str | Path = "../ns4kge-ontology/ontology/ns4kge_shapes.ttl",
) -> Path:
    ontology_path = Path(ontology_path)
    shapes_path = Path(shapes_path)
    shapes_path.parent.mkdir(parents=True, exist_ok=True)

    g = Graph()
    g.parse(ontology_path, format="turtle")
    print(f"Ontology loaded: {len(g)} triples")

    domain_props = defaultdict(list)
    for prop in g.subjects(RDF.type, OWL.ObjectProperty):
        domain = g.value(prop, RDFS.domain)
        range_ = g.value(prop, RDFS.range)
        if domain:
            domain_props[domain].append((prop, range_, False))

    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        domain = g.value(prop, RDFS.domain)
        range_ = g.value(prop, RDFS.range)
        if domain:
            domain_props[domain].append((prop, range_, True))

    cardinalities = defaultdict(dict)
    for cls in g.subjects(RDFS.subClassOf, None):
        for restriction in g.objects(cls, RDFS.subClassOf):
            if (restriction, RDF.type, OWL.Restriction) not in g:
                continue
            prop = g.value(restriction, OWL.onProperty)
            if prop is None:
                continue
            exact = g.value(restriction, OWL_EXACT)
            min_c = g.value(restriction, OWL_MIN)
            max_c = g.value(restriction, OWL_MAX)

            if exact is not None:
                cardinalities[cls][prop] = (int(exact), int(exact))
            else:
                existing = cardinalities[cls].get(prop, (None, None))
                new_min = int(min_c) if min_c is not None else existing[0]
                new_max = int(max_c) if max_c is not None else existing[1]
                cardinalities[cls][prop] = (new_min, new_max)

    lines = [
        "@prefix sh:         <http://www.w3.org/ns/shacl#> .",
        f"@prefix ns4kge: <{ONTOLOGY_NS}> .",
        "@prefix xsd:        <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix rdfs:       <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
    ]

    for domain, props in sorted(domain_props.items(), key=lambda x: str(x[0])):
        class_name = str(domain).split("#")[-1]
        lines.append(f"# -- {class_name}")
        lines.append(f"ns4kge:{class_name}Shape")
        lines.append("    a sh:NodeShape ;")
        lines.append(f"    sh:targetClass ns4kge:{class_name} ;")

        prop_lines = []
        for prop, range_, is_datatype in sorted(props, key=lambda x: str(x[0])):
            prop_name = str(prop).split("#")[-1]
            range_name = str(range_).split("#")[-1] if range_ else None
            parts = [f"sh:path ns4kge:{prop_name}"]

            min_c, max_c = cardinalities.get(domain, {}).get(prop, (None, None))
            if min_c is not None:
                parts.append(f"sh:minCount {min_c}")
            if max_c is not None:
                parts.append(f"sh:maxCount {max_c}")

            if is_datatype and range_:
                range_str = str(range_)
                if "XMLSchema#" in range_str:
                    parts.append(f"sh:datatype xsd:{range_str.split('#')[-1]}")
                else:
                    parts.append("sh:datatype rdfs:Literal")
            elif not is_datatype and range_:
                parts.append(f"sh:class ns4kge:{range_name}")

            prop_lines.append(f"    sh:property [ {' ; '.join(parts)} ]")

        for i, prop_line in enumerate(prop_lines):
            lines.append(prop_line + (" ;" if i < len(prop_lines) - 1 else " ."))
        lines.append("")

    shapes_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Shapes written to {shapes_path}")

    sg = Graph()
    sg.parse(shapes_path, format="turtle")
    print(f"Shapes graph: {len(sg)} triples")
    return shapes_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ontology", default="../ns4kge-ontology/ontology/ns4kge_ontology.ttl")
    parser.add_argument("--out", default="../ns4kge-ontology/ontology/ns4kge_shapes.ttl")
    args = parser.parse_args()
    generate_shapes(ontology_path=args.ontology, shapes_path=args.out)


if __name__ == "__main__":
    main()
