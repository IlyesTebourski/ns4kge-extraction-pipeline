"""Model-agnostic dispatch pipeline.

Routes an article to one of three backends:
- ``claude``     : Anthropic API (closed-weight)
- ``gpt``        : OpenAI API (closed-weight)
- ``openweight`` : any OpenAI-compatible server (vLLM, Ollama, TGI, Together,
                   Groq, OpenRouter, ...), which is how open-weight models such
                   as Llama, Mistral, Qwen or DeepSeek are served. This reuses
                   the GPT runner with a custom ``base_url`` / model name.
"""

import argparse
from pathlib import Path

from no_facts_pipeline.cli.pipeline_claude import run as run_claude
from no_facts_pipeline.cli.pipeline_gpt import run as run_gpt

SUPPORTED = {
    "claude": run_claude,
    "gpt": run_gpt,
}

CHOICES = [*SUPPORTED, "openweight"]


def run(
    md_path: str | Path,
    model: str = "claude",
    output_dir: str | Path = "../ns4kge-kg/per_article",
    prompt_dir: str | Path = "prompts",
    sidecar_dir: str | Path | None = None,
    base_url: str | None = None,
    model_name: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
):
    if model == "openweight":
        if not base_url:
            raise ValueError(
                "model='openweight' requires --base-url pointing at an "
                "OpenAI-compatible server (e.g. http://localhost:8000/v1)."
            )
        kwargs = {"base_url": base_url, "api_key_env": api_key_env}
        if model_name:
            kwargs["model"] = model_name
        return run_gpt(
            md_path,
            output_dir=output_dir,
            prompt_dir=prompt_dir,
            sidecar_dir=sidecar_dir,
            **kwargs,
        )

    runner = SUPPORTED[model]
    return runner(md_path, output_dir=output_dir, prompt_dir=prompt_dir, sidecar_dir=sidecar_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("md_path", nargs="?", default="../mds/EANS.md")
    parser.add_argument("--model", "-m", default="claude", choices=CHOICES)
    parser.add_argument("--output-dir", default="../ns4kge-kg/per_article")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--sidecar-dir", default=None)
    parser.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible endpoint for --model openweight "
        "(e.g. http://localhost:8000/v1 for vLLM/Ollama).",
    )
    parser.add_argument(
        "--model-name",
        default=None,
        help="Model identifier to request from the endpoint for --model openweight "
        "(e.g. meta-llama/Llama-3.1-70B-Instruct).",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable holding the API key for --model openweight.",
    )
    args = parser.parse_args()
    run(
        args.md_path,
        model=args.model,
        output_dir=args.output_dir,
        prompt_dir=args.prompt_dir,
        sidecar_dir=args.sidecar_dir,
        base_url=args.base_url,
        model_name=args.model_name,
        api_key_env=args.api_key_env,
    )


if __name__ == "__main__":
    main()
