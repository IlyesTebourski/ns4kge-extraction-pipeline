"""Run SPARQL competency queries over a populated NS4KGE graph."""

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


QUERIES = [
    (
        "CQ1 - Datasets most frequently used to evaluate negative sampling methods",
        """
        SELECT ?dataset (COUNT(DISTINCT ?config) AS ?nbConfigs) (COUNT(DISTINCT ?article) AS ?nbArticles) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasNSMethod ?method .
        }
        GROUP BY ?dataset
        ORDER BY DESC(?nbConfigs)
        """,
    ),
    (
        "CQ2 - KGE models most associated with each negative sampling method",
        """
        SELECT ?nsMethod ?kgeModel (COUNT(DISTINCT ?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasNSMethod ?nsMethod .
            ?config ns4kge:hasKGEModel ?kgeModel .
        }
        GROUP BY ?nsMethod ?kgeModel
        ORDER BY ?nsMethod DESC(?count)
        """,
    ),
    (
        "CQ3 - Evaluation metrics most frequently reported",
        """
        SELECT ?metric (COUNT(DISTINCT ?config) AS ?nbConfigs) (COUNT(DISTINCT ?article) AS ?nbArticles) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?config ns4kge:hasMetric ?metric .
        }
        GROUP BY ?metric
        ORDER BY DESC(?nbConfigs)
        """,
    ),
    (
        "CQ4 - Most frequent dataset, KGE model, and negative sampling method combinations",
        """
        SELECT ?dataset ?kgeModel ?nsMethod (COUNT(DISTINCT ?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasKGEModel ?kgeModel .
            ?config ns4kge:hasNSMethod ?nsMethod .
        }
        GROUP BY ?dataset ?kgeModel ?nsMethod
        ORDER BY DESC(?count)
        """,
    ),
    (
        "CQ5 - Completeness of experimental descriptions by article",
        """
        SELECT ?article
            (IF(BOUND(?opt),  "yes", "no") AS ?hasOptimizer)
            (IF(BOUND(?lr),   "yes", "no") AS ?hasLR)
            (IF(BOUND(?loss), "yes", "no") AS ?hasLoss)
            (IF(BOUND(?hw),   "yes", "no") AS ?hasHardware)
            (IF(BOUND(?nsr),  "yes", "no") AS ?hasNSRatio)
        WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            OPTIONAL { ?tp ns4kge:hasOptimizer ?opt . }
            OPTIONAL { ?tp ns4kge:learningRate ?lr . }
            OPTIONAL { ?tp ns4kge:hasLossFunction ?loss . }
            OPTIONAL { ?tp ns4kge:hasHardware ?hw . }
            OPTIONAL { ?tp ns4kge:nsRatio ?nsr . }
        }
        ORDER BY ?article
        """,
    ),
    (
        "CQ6 - Underrepresented negative sampling method and dataset combinations",
        """
        SELECT ?nsMethod ?dataset (COUNT(DISTINCT ?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasNSMethod ?nsMethod .
            ?config ns4kge:hasDataset ?dataset .
        }
        GROUP BY ?nsMethod ?dataset
        HAVING (COUNT(DISTINCT ?config) = 1)
        ORDER BY ?nsMethod ?dataset
        """,
    ),
    (
        "CQ7 - Articles with incomplete experimental configurations",
        """
        SELECT ?article
            (IF(!BOUND(?opt),  "missing", "ok") AS ?optimizer)
            (IF(!BOUND(?lr),   "missing", "ok") AS ?learningRate)
            (IF(!BOUND(?loss), "missing", "ok") AS ?lossFunction)
            (IF(!BOUND(?hw),   "missing", "ok") AS ?hardware)
            (IF(!BOUND(?nsr),  "missing", "ok") AS ?nsRatio)
        WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            OPTIONAL { ?tp ns4kge:hasOptimizer ?opt . }
            OPTIONAL { ?tp ns4kge:learningRate ?lr . }
            OPTIONAL { ?tp ns4kge:hasLossFunction ?loss . }
            OPTIONAL { ?tp ns4kge:hasHardware ?hw . }
            OPTIONAL { ?tp ns4kge:nsRatio ?nsr . }
            FILTER (!BOUND(?opt) || !BOUND(?lr) || !BOUND(?loss) || !BOUND(?hw) || !BOUND(?nsr))
        }
        ORDER BY ?article
        """,
    ),
    (
        "CQ8 - Experimental dimensions most often missing",
        """
        SELECT ?dimension (COUNT(DISTINCT ?article) AS ?nbMissing) WHERE {
            {
                BIND("optimizer" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                FILTER NOT EXISTS { ?tp ns4kge:hasOptimizer ?v . }
            } UNION {
                BIND("learningRate" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                FILTER NOT EXISTS { ?tp ns4kge:learningRate ?v . }
            } UNION {
                BIND("lossFunction" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                FILTER NOT EXISTS { ?tp ns4kge:hasLossFunction ?v . }
            } UNION {
                BIND("hardware" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                FILTER NOT EXISTS { ?tp ns4kge:hasHardware ?v . }
            } UNION {
                BIND("nsRatio" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                FILTER NOT EXISTS { ?tp ns4kge:nsRatio ?v . }
            }
        }
        GROUP BY ?dimension
        ORDER BY DESC(?nbMissing)
        """,
    ),
    (
        "CQ9 - Negative sampling methods evaluated on dataset/fb15k-237",
        """
        SELECT DISTINCT ?nsMethod (COUNT(DISTINCT ?article) AS ?nbArticles) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?config ns4kge:hasDataset <dataset/fb15k-237> .
            ?config ns4kge:hasNSMethod ?nsMethod .
        }
        GROUP BY ?nsMethod
        ORDER BY DESC(?nbArticles)
        """,
    ),
    (
        "CQ10 - Most frequent configurations for link prediction",
        """
        SELECT ?dataset ?kgeModel ?nsMethod ?metric (COUNT(DISTINCT ?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasTask <task/link-prediction> .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasKGEModel ?kgeModel .
            ?config ns4kge:hasNSMethod ?nsMethod .
            ?config ns4kge:hasMetric ?metric .
        }
        GROUP BY ?dataset ?kgeModel ?nsMethod ?metric
        ORDER BY DESC(?count)
        LIMIT 20
        """,
    ),
    (
        "CQ11 - Similar configurations with divergent results",
        """
        SELECT ?dataset ?kgeModel ?metric
            (MIN(?result) AS ?minResult)
            (MAX(?result) AS ?maxResult)
            (MAX(?result) - MIN(?result) AS ?spread)
            (COUNT(DISTINCT ?article) AS ?nbArticles)
        WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasKGEModel ?kgeModel .
            ?config ns4kge:hasMetric ?metric .
            ?config ns4kge:result ?result .
        }
        GROUP BY ?dataset ?kgeModel ?metric
        HAVING (COUNT(DISTINCT ?article) > 1 && (MAX(?result) - MIN(?result)) > 0)
        ORDER BY DESC(?spread)
        LIMIT 15
        """,
    ),
    (
        "CQ12 - Best negative sampling method by task and dataset according to maximum result",
        """
        SELECT ?task ?dataset ?nsMethod ?kgeModel ?metric (MAX(?result) AS ?bestResult) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasTask ?task .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasNSMethod ?nsMethod .
            ?config ns4kge:hasKGEModel ?kgeModel .
            ?config ns4kge:hasMetric ?metric .
            ?config ns4kge:result ?result .
        }
        GROUP BY ?task ?dataset ?nsMethod ?kgeModel ?metric
        ORDER BY ?task ?dataset DESC(?bestResult)
        """,
    ),
    (
        "UC1 - Negative sampling method, dataset, and KGE model combinations evaluated in the literature",
        """
        SELECT ?nsMethod ?dataset ?kgeModel (COUNT(?config) AS ?count) WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasNSMethod ?nsMethod .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasKGEModel ?kgeModel .
        }
        GROUP BY ?nsMethod ?dataset ?kgeModel
        ORDER BY DESC(?count)
        """,
    ),
    (
        "UC3 - Top link prediction configurations for experimental blueprinting",
        """
        SELECT ?method ?model ?optimizer ?loss ?dataset ?metric (MAX(?result) AS ?bestResult) WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            ?config ns4kge:hasTask <task/link-prediction> .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasNSMethod ?method .
            ?config ns4kge:hasKGEModel ?model .
            ?config ns4kge:hasMetric ?metric .
            ?config ns4kge:result ?result .
            OPTIONAL { ?tp ns4kge:hasOptimizer ?optimizer . }
            OPTIONAL { ?tp ns4kge:hasLossFunction ?loss . }
        }
        GROUP BY ?method ?model ?optimizer ?loss ?dataset ?metric
        ORDER BY ?dataset ?metric DESC(?bestResult)
        """,
    ),
]


def run_query(graph: Graph, title: str, query: str, limit: int) -> None:
    print(f"{'=' * 60}")
    print(f"UC: {title}")
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
    for title, query in QUERIES:
        run_query(graph, title, query, args.limit)


if __name__ == "__main__":
    main()
