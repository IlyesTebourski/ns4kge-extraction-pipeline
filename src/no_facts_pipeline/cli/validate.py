"""Validate a populated ontology graph against SHACL shapes."""

import argparse
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


def run_validation(
    data: str | Path = "../ns4kge-kg/kg/NSArticles_populated.ttl",
    shapes: str | Path = "../ns4kge-ontology/ontology/NSArticles_shapes.ttl",
) -> bool:
    data = Path(data)
    shapes = Path(shapes)

    dg = Graph()
    dg.parse(data, format="turtle")

    sg = Graph()
    sg.parse(shapes, format="turtle")

    print(f"Data graph:   {len(dg)} triples")
    print(f"Shapes graph: {len(sg)} triples\n")

    conforms, _results_graph, results_text = validate(
        data_graph=dg,
        shacl_graph=sg,
        inference="none",
        advanced=True,
        debug=False,
    )
    print(results_text)
    if conforms:
        print("Ontology conforms to all SHACL shapes.")
    else:
        print("Violations found - see above.")
    return conforms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="../ns4kge-kg/kg/NSArticles_populated.ttl")
    parser.add_argument("--shapes", default="../ns4kge-ontology/ontology/NSArticles_shapes.ttl")
    args = parser.parse_args()
    sys.exit(0 if run_validation(data=args.data, shapes=args.shapes) else 1)


if __name__ == "__main__":
    main()
