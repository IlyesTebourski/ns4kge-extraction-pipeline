"""OpenAI GPT pipeline: markdown article to JSON and per-article TTL."""

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from no_facts_pipeline.core import (
    json_to_ttl,
    load_md_no_tables,
    load_md_tables_only,
    load_prompt,
    merge_jsons,
    parse_json,
)

DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 16000


def call(client: OpenAI, prompt: str, text: str, model: str, max_tokens: int) -> str:
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": f"{text}\n\n{prompt}"}],
    )
    usage = response.usage
    print(f"    Input tokens: {usage.prompt_tokens} | Output tokens: {usage.completion_tokens}")
    return response.choices[0].message.content


def run(
    md_path: str | Path,
    output_dir: str | Path = "../ns4kge-kg/per_article",
    prompt_dir: str | Path = "prompts",
    sidecar_dir: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> dict:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    md_path = Path(md_path)
    output_dir = Path(output_dir)
    prompt_dir = Path(prompt_dir)
    slug = md_path.stem.lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== [GPT] Pipeline for {md_path} (slug: {slug}) ===\n")
    print("Loading markdown...")
    md_no_tables = load_md_no_tables(str(md_path))
    md_tables = load_md_tables_only(str(md_path))

    if sidecar_dir is not None:
        sidecar_dir = Path(sidecar_dir)
        sidecar_dir.mkdir(parents=True, exist_ok=True)
        (sidecar_dir / f"{slug}_no_tables.md").write_text(md_no_tables, encoding="utf-8")
        (sidecar_dir / f"{slug}_tables_only.md").write_text(md_tables, encoding="utf-8")

    print("Step 1 - Extracting metadata...")
    prompt1 = load_prompt(str(prompt_dir / "prompt1_no_results.txt"))
    json1 = parse_json(call(client, prompt1, md_no_tables, model, max_tokens))
    with (output_dir / f"{slug}_json1.json").open("w", encoding="utf-8") as f:
        json.dump(json1, f, indent=2)
    print(f"    Saved {output_dir / f'{slug}_json1.json'}")

    print("Step 2 - Extracting results table...")
    prompt2 = load_prompt(str(prompt_dir / "prompt2_tab.txt"))
    context = _build_context(json1, md_tables)
    json2 = parse_json(call(client, prompt2, context, model, max_tokens))
    with (output_dir / f"{slug}_json2.json").open("w", encoding="utf-8") as f:
        json.dump(json2, f, indent=2)
    print(f"    Saved {output_dir / f'{slug}_json2.json'}")

    print("Step 3 - Merging...")
    merged = merge_jsons(json1, json2)
    with (output_dir / f"{slug}_merged.json").open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    print(f"    Saved {output_dir / f'{slug}_merged.json'}")

    print("Step 4 - Generating TTL...")
    ttl = json_to_ttl(merged, slug)
    (output_dir / f"{slug}.ttl").write_text(ttl, encoding="utf-8")
    print(f"    Saved {output_dir / f'{slug}.ttl'}")

    return merged


def _build_context(json1: dict, md_tables: str) -> str:
    return (
        "ARTICLE CONTEXT (use these names when possible):\n"
        f"- Proposed NS Method: {json1.get('proposedNSMethod', '')}\n"
        f"- Mentioned NS Methods: {', '.join(json1.get('mentionedNSMethods', []))}\n"
        f"- Mentioned KGE Models: {', '.join(json1.get('mentionedKGEModels', []))}\n\n"
        "For KGEModel and NSMethod names, prefer the names listed above when they match "
        "what appears in the table. Table entries are often abbreviated. "
        "If a name clearly matches one in the context, use the full name from the context. "
        "If a name is not in the context, use it exactly as written in the table.\n\n"
        f"TABLES:\n{md_tables}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("md_path", nargs="?", default="../mds/EANS.md")
    parser.add_argument("--output-dir", default="../ns4kge-kg/per_article")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--sidecar-dir", default=None)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    args = parser.parse_args()
    run(
        args.md_path,
        output_dir=args.output_dir,
        prompt_dir=args.prompt_dir,
        sidecar_dir=args.sidecar_dir,
        model=args.model,
        max_tokens=args.max_tokens,
    )


if __name__ == "__main__":
    main()
