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
    # ------------------------------------------------------------------
    # Use Case 1 - Structured exploration of the literature
    # ------------------------------------------------------------------
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
        "CQ2 - KGE models most commonly associated with particular NS strategies",
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
        "CQ3 - Evaluation metrics typically reported",
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
    # ------------------------------------------------------------------
    # Use Case 2 - Reporting coverage and comparability
    # ------------------------------------------------------------------
    (
        "CQ5 - Experimental parameters: how often reported vs missing across papers",
        """
        SELECT ?dimension
            (COUNT(DISTINCT ?reported) AS ?nbReported)
            (COUNT(DISTINCT ?missing) AS ?nbMissing)
        WHERE {
            {
                BIND("optimizer" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                OPTIONAL { ?tp ns4kge:hasOptimizer ?v . }
            } UNION {
                BIND("learningRate" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                OPTIONAL { ?tp ns4kge:learningRate ?v . }
            } UNION {
                BIND("lossFunction" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                OPTIONAL { ?tp ns4kge:hasLossFunction ?v . }
            } UNION {
                BIND("hardware" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                OPTIONAL { ?tp ns4kge:hasHardware ?v . }
            } UNION {
                BIND("nsRatio" AS ?dimension)
                ?article rdf:type ns4kge:Article .
                ?article ns4kge:hasExperimentation ?exp .
                ?exp ns4kge:hasTrainingProtocol ?tp .
                OPTIONAL { ?tp ns4kge:nsRatio ?v . }
            }
            BIND(IF(BOUND(?v), ?article, ?none) AS ?reported)
            BIND(IF(BOUND(?v), ?none, ?article) AS ?missing)
        }
        GROUP BY ?dimension
        ORDER BY DESC(?nbMissing)
        """,
    ),
    (
        "CQ6 - NS methods evaluated across the fewest datasets and KGE models",
        """
        SELECT ?nsMethod
            (COUNT(DISTINCT ?dataset) AS ?nbDatasets)
            (COUNT(DISTINCT ?kgeModel) AS ?nbModels)
            (COUNT(DISTINCT ?config) AS ?nbConfigs)
        WHERE {
            ?config rdf:type ns4kge:Configuration .
            ?config ns4kge:hasNSMethod ?nsMethod .
            OPTIONAL { ?config ns4kge:hasDataset ?dataset . }
            OPTIONAL { ?config ns4kge:hasKGEModel ?kgeModel . }
        }
        GROUP BY ?nsMethod
        ORDER BY ?nbDatasets ?nbModels ?nsMethod
        """,
    ),
    (
        "CQ7 - Articles that do not fully describe their experimental configuration",
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
    # ------------------------------------------------------------------
    # Use Case 3 - Exploration of experimental configurations
    # ------------------------------------------------------------------
    (
        "CQ8 - Negative sampling methods evaluated on a given dataset (dataset/fb15k-237)",
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
        "CQ9 - Most frequent configurations for link-prediction tasks",
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
        "CQ10 - Similar experimental configurations with strongly diverging results",
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
        "CQ11 - Performance differences associated with changes in training configuration",
        """
        SELECT ?dataset ?kgeModel ?nsMethod ?metric
            (COUNT(DISTINCT ?optimizer) AS ?nbOptimizers)
            (COUNT(DISTINCT ?loss) AS ?nbLosses)
            (MIN(?result) AS ?minResult)
            (MAX(?result) AS ?maxResult)
            (MAX(?result) - MIN(?result) AS ?spread)
        WHERE {
            ?article rdf:type ns4kge:Article .
            ?article ns4kge:hasExperimentation ?exp .
            ?exp ns4kge:hasConfiguration ?config .
            ?exp ns4kge:hasTrainingProtocol ?tp .
            ?config ns4kge:hasDataset ?dataset .
            ?config ns4kge:hasKGEModel ?kgeModel .
            ?config ns4kge:hasNSMethod ?nsMethod .
            ?config ns4kge:hasMetric ?metric .
            ?config ns4kge:result ?result .
            OPTIONAL { ?tp ns4kge:hasOptimizer ?optimizer . }
            OPTIONAL { ?tp ns4kge:hasLossFunction ?loss . }
        }
        GROUP BY ?dataset ?kgeModel ?nsMethod ?metric
        HAVING ((COUNT(DISTINCT ?optimizer) > 1 || COUNT(DISTINCT ?loss) > 1) && (MAX(?result) - MIN(?result)) > 0)
        ORDER BY DESC(?spread)
        LIMIT 15
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
