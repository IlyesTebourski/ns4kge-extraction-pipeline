"""Convert a merged extraction JSON file into per-article TTL."""

import argparse
import json
from pathlib import Path

from no_facts_pipeline.core import json_to_ttl


def run(merged_path: str | Path, output_dir: str | Path = "../ns4kge-kg/per_article") -> Path:
    merged_path = Path(merged_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = merged_path.name.replace("_merged.json", "").lower()

    print(f"Generating TTL for {merged_path}...")
    with merged_path.open("r", encoding="utf-8") as f:
        merged = json.load(f)

    out_path = output_dir / f"{slug}.ttl"
    out_path.write_text(json_to_ttl(merged, slug), encoding="utf-8")
    print(f"    Saved {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("merged_path", nargs="?", default="../ns4kge-kg/per_article/eans_merged.json")
    parser.add_argument("--output-dir", default="../ns4kge-kg/per_article")
    args = parser.parse_args()
    run(args.merged_path, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
