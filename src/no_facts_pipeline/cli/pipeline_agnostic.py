"""Model-dispatch pipeline for Claude or GPT."""

import argparse
from pathlib import Path

from no_facts_pipeline.cli.pipeline_claude import run as run_claude
from no_facts_pipeline.cli.pipeline_gpt import run as run_gpt

SUPPORTED = {
    "claude": run_claude,
    "gpt": run_gpt,
}


def run(
    md_path: str | Path,
    model: str = "claude",
    output_dir: str | Path = "../ns4kge-kg/per_article",
    prompt_dir: str | Path = "prompts",
    sidecar_dir: str | Path | None = None,
):
    runner = SUPPORTED[model]
    return runner(md_path, output_dir=output_dir, prompt_dir=prompt_dir, sidecar_dir=sidecar_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("md_path", nargs="?", default="../mds/EANS.md")
    parser.add_argument("--model", "-m", default="claude", choices=SUPPORTED.keys())
    parser.add_argument("--output-dir", default="../ns4kge-kg/per_article")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--sidecar-dir", default=None)
    args = parser.parse_args()
    run(
        args.md_path,
        model=args.model,
        output_dir=args.output_dir,
        prompt_dir=args.prompt_dir,
        sidecar_dir=args.sidecar_dir,
    )


if __name__ == "__main__":
    main()
