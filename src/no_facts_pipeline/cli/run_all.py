"""Run the extraction pipeline over all source markdown articles in a directory."""

import argparse
import sys
from pathlib import Path

from no_facts_pipeline.cli.pipeline_agnostic import CHOICES
from no_facts_pipeline.cli.pipeline_agnostic import run as dispatch_run


def run_all(
    mds_dir: str | Path = "../mds",
    model: str = "claude",
    output_dir: str | Path = "../ns4kge-kg/per_article",
    prompt_dir: str | Path = "prompts",
    sidecar_dir: str | Path | None = None,
    skip_existing: bool = False,
    base_url: str | None = None,
    model_name: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
) -> tuple[list[str], list[str], list[str]]:
    mds_dir = Path(mds_dir)
    output_dir = Path(output_dir)
    md_files = sorted(mds_dir.glob("*.md"))
    md_files = [f for f in md_files if not f.stem.endswith(("_no_tables", "_tables_only"))]

    if not md_files:
        print(f"No .md files found in {mds_dir}/")
        sys.exit(1)

    print(f"Found {len(md_files)} article(s) in {mds_dir}/\n")
    ok, skipped, failed = [], [], []

    for md_path in md_files:
        slug = md_path.stem.lower()
        ttl_path = output_dir / f"{slug}.ttl"

        if skip_existing and ttl_path.exists():
            print(f"[SKIP] {md_path.name} - TTL already exists")
            skipped.append(slug)
            continue

        try:
            dispatch_run(
                md_path,
                model=model,
                output_dir=output_dir,
                prompt_dir=prompt_dir,
                sidecar_dir=sidecar_dir,
                base_url=base_url,
                model_name=model_name,
                api_key_env=api_key_env,
            )
            ok.append(slug)
        except Exception as exc:
            print(f"[ERROR] {md_path.name} - {exc}")
            failed.append(slug)

    print(f"\n{'=' * 50}")
    print(f"Done. {len(ok)} ok / {len(skipped)} skipped / {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    return ok, skipped, failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mds_dir", nargs="?", default="../mds")
    parser.add_argument("--model", "-m", default="claude", choices=CHOICES)
    parser.add_argument("--output-dir", default="../ns4kge-kg/per_article")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--sidecar-dir", default=None)
    parser.add_argument("--skip-existing", "-s", action="store_true")
    parser.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible endpoint for --model openweight "
        "(e.g. http://localhost:8000/v1 for vLLM/Ollama).",
    )
    parser.add_argument(
        "--model-name",
        default=None,
        help="Model identifier to request from the endpoint for --model openweight.",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable holding the API key for --model openweight.",
    )
    args = parser.parse_args()
    run_all(
        args.mds_dir,
        model=args.model,
        output_dir=args.output_dir,
        prompt_dir=args.prompt_dir,
        sidecar_dir=args.sidecar_dir,
        skip_existing=args.skip_existing,
        base_url=args.base_url,
        model_name=args.model_name,
        api_key_env=args.api_key_env,
    )


if __name__ == "__main__":
    main()
