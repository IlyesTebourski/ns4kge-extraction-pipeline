"""
core/loaders.py

I/O utilities: reading markdown files and prompts from disk.
No API calls, no transformations.
"""

import re


def load_prompt(path: str) -> str:
    """Load a plain text prompt file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_md_no_tables(path: str) -> str:
    """
    Load a markdown file, stripping all HTML table blocks
    and everything from the References section onwards.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"<table>[\s\S]*?</table>", "", content)
    content = re.split(r"\n#+\s*references\b", content, flags=re.IGNORECASE)[0]

    return content.strip()


def load_md_tables_only(path: str) -> str:
    """
    Load a markdown file, returning only the HTML table blocks,
    each preceded by its caption if one is found.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(Table\s+\d+[^\n]*)?\s*(<table>[\s\S]*?</table>)\s*(Table\s+\d+[^\n]*)?"
    matches = re.findall(pattern, content)

    result = []
    for caption_before, table, caption_after in matches:
        caption = (caption_before or caption_after).strip()
        result.append(f"{caption}\n{table}" if caption else table)

    return "\n\n".join(result)