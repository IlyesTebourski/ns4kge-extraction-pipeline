"""Run diagnostic SPARQL queries over a populated NS4KGE graph."""

import argparse
from pathlib import Path

from rdflib import Graph

from no_facts_pipeline.core.uris import KG_ID_BASE, ONTOLOGY_NS

PREFIX_SPARQL = f"""
BASE <{KG_ID_BASE}>
PREFIX ns4kge: <{ONTOLOGY_NS}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


def compact_term(value: object) -> str:
    text = str(value)
    for base in (KG_ID_BASE, ONTOLOGY_NS):
        text = text.replace(base, "")
    if "/" in text or text != str(value):
        return text
    return text.split("#")[-1]


DEBUG_QUERIES = [
    (
        "Number of experimentations per article",
        """
        SELECT ?article (COUNT(?exp) AS ?nbExp) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
        }
        GROUP BY ?article
        ORDER BY ?article
        """,
    ),
    (
        "Articles with more than one experimentation",
        """
        SELECT ?article (COUNT(?exp) AS ?nbExp) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
        }
        GROUP BY ?article
        HAVING (COUNT(?exp) > 1)
        """,
    ),
    (
        "Number of configurations per article",
        """
        SELECT ?article (COUNT(?config) AS ?nbConfigs) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
        }
        GROUP BY ?article
        ORDER BY DESC(?nbConfigs)
        """,
    ),
    (
        "Loss functions per article",
        """
        SELECT ?article ?tp (COUNT(?loss) AS ?nbLoss) (GROUP_CONCAT(STR(?loss); separator=", ") AS ?values) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            ?tp ns4kge:hasLossFunction ?loss .
        }
        GROUP BY ?article ?tp
        ORDER BY DESC(?nbLoss)
        """,
    ),
    (
        "Learning rates per article",
        """
        SELECT ?article ?tp (COUNT(?lr) AS ?nbLR) (GROUP_CONCAT(STR(?lr); separator=", ") AS ?values) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            ?tp ns4kge:learningRate ?lr .
        }
        GROUP BY ?article ?tp
        ORDER BY DESC(?nbLR)
        """,
    ),
    (
        "Optimizers per article",
        """
        SELECT ?article ?tp (COUNT(?opt) AS ?nbOpt) (GROUP_CONCAT(STR(?opt); separator=", ") AS ?values) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            ?tp ns4kge:hasOptimizer ?opt .
        }
        GROUP BY ?article ?tp
        ORDER BY DESC(?nbOpt)
        """,
    ),
    (
        "Configurations without an NSMethod",
        """
        SELECT ?article ?config ?dataset ?model WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasKGEModel ?model .
            FILTER NOT EXISTS { ?config ns4kge:hasNSMethod ?m . }
        }
        ORDER BY ?article
        """,
    ),
    (
        "Articles without proposesNSMethod",
        """
        SELECT ?article WHERE {
            ?article rdf:type ns4kge:Article .
            FILTER NOT EXISTS { ?article ns4kge:proposesNSMethod ?m . }
        }
        """,
    ),
    (
        "Configurations without result",
        """
        SELECT ?article ?config WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            FILTER NOT EXISTS { ?config ns4kge:result ?r . }
        }
        ORDER BY ?article
        """,
    ),
    (
        "Outlier results greater than 10000 or below 0",
        """
        SELECT ?article ?config ?result WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?config ns4kge:result ?result .
            FILTER (?result > 10000 || ?result < 0)
        }
        ORDER BY DESC(?result)
        """,
    ),
    (
        "Dataset variants that may need normalization",
        """
        SELECT ?dataset (COUNT(?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasDataset ?dataset .
        }
        GROUP BY ?dataset
        ORDER BY ?dataset
        """,
    ),
    (
        "NSMethod variants that may need normalization",
        """
        SELECT ?method (COUNT(?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasNSMethod ?method .
        }
        GROUP BY ?method
        ORDER BY ?method
        """,
    ),
    (
        "Explicit class type counts",
        """
        SELECT ?type (COUNT(?s) AS ?count) WHERE {
            ?s rdf:type ?type .
            FILTER(STRSTARTS(STR(?type), "https://w3id.org/ns4kge/ontology#"))
        }
        GROUP BY ?type
        ORDER BY DESC(?count)
        """,
    ),
    (
        "Category and subcategory by NSMethod",
        """
        SELECT ?method ?category ?subcategory WHERE {
            ?method rdf:type ns4kge:NSMethod .
            OPTIONAL { ?method ns4kge:hasCategory ?category . }
            OPTIONAL { ?method ns4kge:hasSubcategory ?subcategory . }
        }
        ORDER BY ?method
        """,
    ),
]


def run_query(graph: Graph, title: str, query: str, limit: int) -> None:
    print(f"{'=' * 60}")
    print(f"DEBUG: {title}")
    print(f"{'=' * 60}")
    results = list(graph.query(PREFIX_SPARQL + query))
    if not results:
        print("  (no results)")
    for row in results[:limit]:
        print(" ", " | ".join(compact_term(x) for x in row))
    if len(results) > limit:
        print(f"  ... ({len(results) - limit} more rows)")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="../ns4kge-kg/kg/ns4kge_populated.ttl")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    graph = Graph()
    graph.parse(Path(args.data), format="turtle")
    print(f"Graph loaded: {len(graph)} triples\n")
    for title, query in DEBUG_QUERIES:
        run_query(graph, title, query, args.limit)


if __name__ == "__main__":
    main()
