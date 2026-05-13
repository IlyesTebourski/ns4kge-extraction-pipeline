"""
core/converters.py

Pure transformation utilities: JSON merging and TTL generation.
No API calls, no I/O.
"""

import re


# ─── NS TAXONOMY ─────────────────────────────────────────────────────────────

NS_TAXONOMY = {
    # ── Static NS ─────────────────────────────────────────────────────────────
    "randomcorrupt": { "category": "Static NS", "subcategory": "Random" },
    "random-negative-sampling": { "category": "Static NS", "subcategory": "Random" },
    "uniform-negative-sampling": { "category": "Static NS", "subcategory": "Random" },
    "uniform-random-negative-sampling": { "category": "Static NS", "subcategory": "Random" },
    "pns":           { "category": "Static NS", "subcategory": "Probabilistic" },
    "probabilistic-negative-sampling": { "category": "Static NS", "subcategory": "Probabilistic" },
    "bernoulli":     { "category": "Static NS", "subcategory": "Probabilistic" },
    "bernoulli-negative-sampling": { "category": "Static NS", "subcategory": "Probabilistic" },
    "frr":           { "category": "Static NS", "subcategory": "Probabilistic" },
    "sparsens":      { "category": "Static NS", "subcategory": "Probabilistic" },
    "domainns":      { "category": "Static NS", "subcategory": "Probabilistic" },
    "domain-sampling": { "category": "Static NS", "subcategory": "Probabilistic" },
    "erdns":         { "category": "Static NS", "subcategory": "Probabilistic" },
    "gibbsns":       { "category": "Static NS", "subcategory": "Probabilistic" },
    "nn":            { "category": "Static NS", "subcategory": "Model-guided" },
    "nearest-neighbour-sampling": { "category": "Static NS", "subcategory": "Model-guided" },
    "nearest-neighbor-negative-sampling": { "category": "Static NS", "subcategory": "Model-guided" },
    "approximate-nearest-neighbor-negative-sampling": { "category": "Static NS", "subcategory": "Model-guided" },
    "nmiss":         { "category": "Static NS", "subcategory": "Model-guided" },
    "near-miss-sampling": { "category": "Static NS", "subcategory": "Model-guided" },
    "lemon":         { "category": "Static NS", "subcategory": "Model-guided" },
    "lts":           { "category": "Static NS", "subcategory": "Model-guided" },
    "in-batch-negative-sampling": { "category": "Static NS", "subcategory": "Random" },
    "sans":          { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "rw-sans":       { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "typeconstraints":{ "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "type-constrained-negative-sampling": { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "stc":           { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "structure-aware-negative-sampling": { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "rcwc":          { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "cdns":          { "category": "Static NS", "subcategory": "Knowledge-constrained" },
    "gns":           { "category": "Static NS", "subcategory": "Knowledge-constrained" },

    # ── Dynamic NS ────────────────────────────────────────────────────────────
    "eans":          { "category": "Dynamic NS", "subcategory": "Model-guided" },
    "entity-aware-negative-sampling": { "category": "Dynamic NS", "subcategory": "Model-guided" },
    "entity-aware-negative-sampling-self-adversarial-negative-sampling": { "category": "Dynamic NS", "subcategory": "Model-guided" },
    "ans":           { "category": "Dynamic NS", "subcategory": "Model-guided" },
    "htens":         { "category": "Dynamic NS", "subcategory": "Model-guided" },
    "truncatedns":   { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "adns":          { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "dns":           { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "pre-batch-negative-sampling": { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "reinforced-negative-sampling": { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "self-negative-sampling": { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "sns":           { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "dss":           { "category": "Dynamic NS", "subcategory": "Self-adaptive" },
    "reasonkge":     { "category": "Dynamic NS", "subcategory": "Knowledge-constrained" },

    # ── Adversarial NS ────────────────────────────────────────────────────────
    "kbgan":         { "category": "Adversarial NS", "subcategory": "Standard" },
    "kbgan-complex": { "category": "Adversarial NS", "subcategory": "Standard" },
    "kbgan-distmult": { "category": "Adversarial NS", "subcategory": "Standard" },
    "igan":          { "category": "Adversarial NS", "subcategory": "Standard" },
    "gan-based-negative-sampling": { "category": "Adversarial NS", "subcategory": "Standard" },
    "gan-pretrain":  { "category": "Adversarial NS", "subcategory": "Standard" },
    "gan-scratch":   { "category": "Adversarial NS", "subcategory": "Standard" },
    "adversarial-contrast": { "category": "Adversarial NS", "subcategory": "Standard" },
    "graphgan":      { "category": "Adversarial NS", "subcategory": "Standard" },
    "kcgan":         { "category": "Adversarial NS", "subcategory": "Standard" },
    "gndn":          { "category": "Adversarial NS", "subcategory": "Standard" },
    "ksgan":         { "category": "Adversarial NS", "subcategory": "Knowledge-constrained" },
    "nksgan":        { "category": "Adversarial NS", "subcategory": "Knowledge-constrained" },
    "ruga":          { "category": "Adversarial NS", "subcategory": "Knowledge-constrained" },
    "noigan":        { "category": "Adversarial NS", "subcategory": "Knowledge-constrained" },
    "naganconvkb":   { "category": "Adversarial NS", "subcategory": "Knowledge-constrained" },

    # ── Self Adversarial NS ───────────────────────────────────────────────────
    "las":           { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "loss-adaptive-sampling": { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "cans":          { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "selfadv":       { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "self-adversarial-negative-sampling": { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "nscaching":     { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "asa":           { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "esns":          { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "abns":          { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "tans":          { "category": "Self Adversarial NS", "subcategory": "Direct" },
    "mcns":          { "category": "Self Adversarial NS", "subcategory": "Model-guided" },
    "mdncaching":    { "category": "Self Adversarial NS", "subcategory": "Model-guided" },
    "tuckerdncaching":{ "category": "Self Adversarial NS", "subcategory": "Model-guided" },
    "ccs":           { "category": "Self Adversarial NS", "subcategory": "Model-guided" },
    "hasa":          { "category": "Self Adversarial NS", "subcategory": "Model-guided" },
    "localcognitive":{ "category": "Self Adversarial NS", "subcategory": "Knowledge-constrained" },
    "cake":          { "category": "Self Adversarial NS", "subcategory": "Knowledge-constrained" },
    "structure-aware-negative-sampling-self-adversarial-negative-sampling": { "category": "Self Adversarial NS", "subcategory": "Knowledge-constrained" },

    # ── Mix-up NS ─────────────────────────────────────────────────────────────
    "m2ixkg":        { "category": "Mix-up NS", "subcategory": "Standard" },
    "mixkg":         { "category": "Mix-up NS", "subcategory": "Standard" },
    "hard-negative-mixing": { "category": "Mix-up NS", "subcategory": "Standard" },
    "mixkg-hnm-ces": { "category": "Mix-up NS", "subcategory": "Standard" },
    "mixkg-hnm-sf":  { "category": "Mix-up NS", "subcategory": "Standard" },
    "demix":         { "category": "Mix-up NS", "subcategory": "Standard" },
    "dcns":          { "category": "Mix-up NS", "subcategory": "Memory-based" },

    # ── Text-based NS ─────────────────────────────────────────────────────────
    "ghn":           { "category": "Text-based NS", "subcategory": "Generative" },
    "generative-hard-negative-mining": { "category": "Text-based NS", "subcategory": "Generative" },
    "ghn-sl":        { "category": "Text-based NS", "subcategory": "Generative" },
}


# ─── URI HELPERS ─────────────────────────────────────────────────────────────

def uri(s: str) -> str:
    """Normalize a string into one URL path segment."""
    text = str(s).lower().replace("%", " percent ")
    slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text)).strip("-")
    if slug == "fb15k237":
        return "fb15k-237"
    return slug


def ref(path: str) -> str:
    """Return a Turtle relative IRI reference under the KG base URI."""
    return f"<{path}>"


def article_ref(slug: str) -> str:
    return ref(f"article/{uri(slug)}")


def experimentation_ref(slug: str) -> str:
    return ref(f"experimentation/{uri(slug)}")


def training_protocol_ref(slug: str) -> str:
    return ref(f"training-protocol/{uri(slug)}")


def configuration_ref(slug: str, index: int) -> str:
    return ref(f"configuration/{uri(slug)}/{index}")


def entity_ref(kind: str, name: str) -> str:
    return ref(f"{kind}/{uri(name)}")


def format_decimal(val) -> str:
    """Format a numeric value as a clean decimal string."""
    return f"{float(val):.10f}".rstrip("0").rstrip(".")


def turtle_literal(value: object) -> str:
    """Escape a Python value for use as a quoted Turtle literal."""
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


# ─── URI NORMALIZATION ALIASES ────────────────────────────────────────────────
# These dicts operate on already-kebab-case URIs (output of uri()).
# Example: "neural tensor network" -> uri() -> "neural-tensor-network" -> alias -> "ntn"

_KGE_URI_ALIASES: dict[str, str] = {
    "neural-tensor-model":    "ntn",
    "neural-tensor-network":  "ntn",
    "neural-tensor-networks": "ntn",
    "structured-embedding":   "se",
    "structured-embeddings":  "se",
    "r-gcn":                  "rgcn",
}

# None = drop (too generic or unresolvable)
_NS_URI_ALIASES: dict[str, str | None] = {
    # Uniform
    "uniform-sampling":                                       "uniform-negative-sampling",
    "uniform-random-sampling":                                "uniform-random-negative-sampling",
    # Random
    "random-sampling":                                        "random-negative-sampling",
    # Self-adversarial
    "self-adversarial-sampling":                              "self-adversarial-negative-sampling",
    "self-adv":                                               "self-adversarial-negative-sampling",
    # Bernoulli
    "bernoulli-sampling":                                     "bernoulli-negative-sampling",
    # GAN-based
    "generative-adversarial-network-based-negative-sampling": "gan-based-negative-sampling",
    "gan":                                                    "gan-based-negative-sampling",
    # KBGAN
    "kb-gan":                                                 "kbgan",
    "kbgan-sampling":                                         "kbgan",
    # SANS
    "structure-aware-negative-sampling":                      "sans",
    # RW-SANS
    "random-walk-structure-aware-negative-sampling":          "rw-sans",
    # Uniform RW-SANS
    "uniform-random-walk-structure-aware-negative-sampling":  "uniform-rw-sans",
    # Static / dynamic
    "static-distribution-sampling":                          "static-sampling",
    "dynamic-distribution-sampling":                         "dynamic-negative-sampling",
    # NSCaching
    "ns-caching":                                            "nscaching",
    "nscaching-sampling":                                    "nscaching",
    # Nearest neighbour (typo)
    "nearest-neighbour-sampling":                            "nearest-neighbor-sampling",
    # Local closed world
    "locally-closed-world-negative-sampling":                "local-closed-world-assumption-negative-sampling",
    # Typed (typo + variant)
    "typed-samplin":                                         "typed-negative-sampling",
    "typed-sampling":                                        "typed-negative-sampling",
    # Domain
    "domain-sampling":                                       "domain-based-negative-sampling",
    # Drop
    "negative-sampling":                                     None,
    "none-sampling":                                         None,
}


def normalize_uri_kge(u: str) -> str:
    """Resolve KGE URI aliases. Input and output are kebab-case."""
    return _KGE_URI_ALIASES.get(u, u)


def normalize_uri_ns(u: str) -> str:
    """Resolve NS URI aliases. Returns '' for suppressed/unknown entries."""
    if re.match(r"^unknown(-\d+)?$", u):
        return ""
    result = _NS_URI_ALIASES.get(u, u)
    return result if result is not None else ""


def kge_uri(name: str) -> str:
    """Canonical URI slug for a KGE model: uri() then alias normalization."""
    return normalize_uri_kge(uri(name))


def ns_uri(name: str) -> str:
    """Canonical URI slug for an NS method: uri() then alias normalization.
    Returns '' if the method should be dropped."""
    return normalize_uri_ns(uri(name))


# ─── RESULT NORMALIZATION ─────────────────────────────────────────────────────

_RATIO_METRICS = {
    "mrr", "hits-1", "hits-3", "hits-5", "hits-10", "hits-30", "hits-50",
    "f1", "auc", "auroc", "auprc", "ap", "accuracy", "ndcg", "ndcg-5", "map",
}


def normalize_result(result: float, metric_slug: str) -> float:
    """Normalize to [0,1] if the metric is a ratio reported as a percentage."""
    if metric_slug in _RATIO_METRICS and result > 1:
        return result / 100
    return result


# ─── DEDUPLICATION ───────────────────────────────────────────────────────────

def dedup_configs(configs: list[dict]) -> list[dict]:
    """Keep the best result per (kge, ns, dataset, task, metric) tuple.
    For MR: lowest is best. For all other metrics: highest is best."""
    best: dict = {}
    for cfg in configs:
        result = cfg.get("result")
        if result is None:
            continue
        key = (
            kge_uri(cfg.get("KGEModel", "")),
            ns_uri(cfg.get("NSMethod", "")),
            uri(cfg.get("Dataset", "")),
            uri(cfg.get("Task", "")),
            uri(cfg.get("Metric", "")),
        )
        if key not in best:
            best[key] = cfg
        else:
            current = best[key]["result"]
            is_mr = key[4] == "mr"
            if (is_mr and result < current) or (not is_mr and result > current):
                best[key] = cfg
    return list(best.values())


# ─── JSON MERGE ──────────────────────────────────────────────────────────────

def merge_jsons(json1: dict, json2: dict) -> dict:
    """
    Merge metadata JSON (json1) with results table JSON (json2).
    Configurations from json2 are injected into json1's Experimentation block.
    KGE models and NS methods found in the table are added to the mentions lists.
    """
    merged = json1.copy()
    merged["Experimentation"]["Configurations"] = json2.get("Configurations", [])

    table_kge = list(set(
        c["KGEModel"] for c in json2.get("Configurations", [])
        if c.get("KGEModel")
    ))
    table_ns = list(set(
        c["NSMethod"] for c in json2.get("Configurations", [])
        if c.get("NSMethod") and c["NSMethod"] != "Unknown"
    ))

    proposed_kge = merged.get("proposedKGEModel", "")
    proposed_ns  = merged.get("proposedNSMethod", "")

    merged["mentionedKGEModels"] = list(set(
        merged.get("mentionedKGEModels", []) +
        [m for m in table_kge if m != proposed_kge]
    ))
    merged["mentionedNSMethods"] = list(set(
        merged.get("mentionedNSMethods", []) +
        [m for m in table_ns if m != proposed_ns]
    ))

    return merged


# ─── TTL GENERATION ──────────────────────────────────────────────────────────

def json_to_ttl(merged: dict, slug: str) -> str:
    """
    Convert a merged article JSON into a TTL (Turtle) string.
    Does not include prefix declarations — those are handled by populate_onto.py.
    """
    lines = []
    def add(s): lines.append(s)

    art          = merged.get("Article", {})
    proposed_ns  = ns_uri(merged.get("proposedNSMethod", ""))
    proposed_kge = kge_uri(merged.get("proposedKGEModel", ""))
    mentioned_ns = list(filter(None, (ns_uri(m) for m in merged.get("mentionedNSMethods", []))))
    mentioned_kge = list(filter(None, (kge_uri(m) for m in merged.get("mentionedKGEModels", []))))
    exp          = merged.get("Experimentation", {})
    proto        = exp.get("TrainingProtocol", {})
    configs      = dedup_configs(exp.get("Configurations", []))

# ── Article ───────────────────────────────────────────────────────────────
    article = article_ref(slug)
    experimentation = experimentation_ref(slug)
    training_protocol = training_protocol_ref(slug)

    add(f'{article} rdf:type ns4kge:Article .')
    if art.get("title"):
        add(f'{article} ns4kge:title "{turtle_literal(art["title"])}"^^xsd:string .')
    if art.get("date"):
        add(f'{article} ns4kge:date "{turtle_literal(art["date"])}"^^xsd:gYear .')
    if proposed_ns:
        add(f'{article} ns4kge:proposesNSMethod {entity_ref("ns-method", proposed_ns)} .')
    for ns in mentioned_ns:
        add(f'{article} ns4kge:mentionsNSMethod {entity_ref("ns-method", ns)} .')
    for kge in mentioned_kge:
        add(f'{article} ns4kge:mentionsKGEModel {entity_ref("kge-model", kge)} .')

    # taxonomy
    tax    = NS_TAXONOMY.get(slug, {})
    cat    = tax.get("category")
    subcat = tax.get("subcategory")
    add(f'{article} ns4kge:hasExperimentation {experimentation} .')
    add("")

    # ── Category / Subcategory individuals ───────────────────────────────────
    declared_categories = set()
    declared_subcategories = set()

    def declare_category(name):
        k = uri(name)
        if k not in declared_categories:
            declared_categories.add(k)
            add(f'{entity_ref("category", name)} rdf:type ns4kge:Category .')
            add("")

    def declare_subcategory(name):
        k = uri(name)
        if k not in declared_subcategories:
            declared_subcategories.add(k)
            add(f'{entity_ref("subcategory", name)} rdf:type ns4kge:Subcategory .')
            add("")

    if cat:
        declare_category(cat)
    if subcat:
        declare_subcategory(subcat)

    # ── NS Methods ────────────────────────────────────────────────────────────
    declared_ns = set()
    def declare_ns(name, cat=None, subcat=None):
        k = uri(name)
        taxonomy = NS_TAXONOMY.get(k, {})
        cat = cat or taxonomy.get("category")
        subcat = subcat or taxonomy.get("subcategory")
        if k not in declared_ns:
            declared_ns.add(k)
            method = entity_ref("ns-method", name)
            add(f'{method} rdf:type ns4kge:NSMethod .')
            if cat:
                declare_category(cat)
                add(f'{method} ns4kge:hasCategory {entity_ref("category", cat)} .')
            if subcat:
                declare_subcategory(subcat)
                add(f'{method} ns4kge:hasSubcategory {entity_ref("subcategory", subcat)} .')
            add("")

    if proposed_ns:
        declare_ns(proposed_ns, cat, subcat)
    for ns in mentioned_ns:
        declare_ns(ns)

    # ── KGE Models ────────────────────────────────────────────────────────────
    declared_kge = set()
    def declare_kge(name):
        k = uri(name)
        if k not in declared_kge:
            declared_kge.add(k)
            add(f'{entity_ref("kge-model", name)} rdf:type ns4kge:KGEModel .')
            add("")

    if proposed_kge:
        declare_kge(proposed_kge)
    for kge in mentioned_kge:
        declare_kge(kge)

    # ── Shared entities ───────────────────────────────────────────────────────
    declared_shared = set()
    def declare_once(kind, cls, name):
        k   = uri(name)
        key = f"{kind}/{k}"
        if key not in declared_shared:
            declared_shared.add(key)
            add(f'{ref(key)} rdf:type ns4kge:{cls} .')

    for cfg in configs:
        if cfg.get("Dataset"): declare_once("dataset",   "Dataset",      cfg["Dataset"])
        if cfg.get("Task"):    declare_once("task",       "Task",         cfg["Task"])
        if cfg.get("Metric"):  declare_once("metric",     "Metric",       cfg["Metric"])
    for lf in proto.get("LossFunction", []): declare_once("loss-function", "LossFunction", lf)
    for op in proto.get("Optimizer",    []): declare_once("optimizer",     "Optimizer",    op)
    for hw in exp.get("Hardware",       []): declare_once("hardware",      "Hardware",     hw)
    add("")

    # ── Experimentation ───────────────────────────────────────────────────────
    add(f'{experimentation} rdf:type ns4kge:Experimentation .')
    add(f'{experimentation} ns4kge:hasTrainingProtocol {training_protocol} .')
    for i in range(len(configs)):
        add(f'{experimentation} ns4kge:hasConfiguration {configuration_ref(slug, i + 1)} .')
    add("")

    # ── TrainingProtocol ──────────────────────────────────────────────────────
    add(f'{training_protocol} rdf:type ns4kge:TrainingProtocol .')
    for op in proto.get("Optimizer",     []): add(f'{training_protocol} ns4kge:hasOptimizer    {entity_ref("optimizer", op)} .')
    for lf in proto.get("LossFunction",  []): add(f'{training_protocol} ns4kge:hasLossFunction {entity_ref("loss-function", lf)} .')
    for hw in exp.get("Hardware",        []): add(f'{training_protocol} ns4kge:hasHardware     {entity_ref("hardware", hw)} .')
    for prop, key in [("learningRate", "learningRate"), ("nsRatio", "nsRatio")]:
        val = proto.get(key)
        if val is not None:
            add(f'{training_protocol} ns4kge:{prop} "{format_decimal(val)}"^^xsd:decimal .')
    add("")

    # ── Configurations ────────────────────────────────────────────────────────
    for i, cfg in enumerate(configs, 1):
        cid = configuration_ref(slug, i)
        add(f'{cid} rdf:type ns4kge:Configuration .')
        if cfg.get("Task"):    add(f'{cid} ns4kge:hasTask    {entity_ref("task", cfg["Task"])} .')
        if cfg.get("Dataset"): add(f'{cid} ns4kge:hasDataset {entity_ref("dataset", cfg["Dataset"])} .')
        if cfg.get("Metric"):  add(f'{cid} ns4kge:hasMetric  {entity_ref("metric", cfg["Metric"])} .')
        if cfg.get("KGEModel"):
            k = kge_uri(cfg["KGEModel"])
            declare_kge(k)
            add(f'{cid} ns4kge:hasKGEModel {entity_ref("kge-model", k)} .')
        ns = cfg.get("NSMethod", "")
        if ns and ns != "Unknown":
            k = ns_uri(ns)
            if k:
                declare_ns(k)
                add(f'{cid} ns4kge:hasNSMethod {entity_ref("ns-method", k)} .')
        if cfg.get("result") is not None:
            normalized = normalize_result(float(cfg["result"]), uri(cfg.get("Metric", "")))
            add(f'{cid} ns4kge:result "{format_decimal(normalized)}"^^xsd:decimal .')
        add("")

    return "\n".join(lines)
