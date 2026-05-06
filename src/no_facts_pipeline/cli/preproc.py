"""Split a markdown article into no-table and tables-only sidecars."""

import argparse
from pathlib import Path

from no_facts_pipeline.core import load_md_no_tables, load_md_tables_only


def run(md_path: str | Path, out_dir: str | Path | None = None) -> tuple[Path, Path]:
    md_path = Path(md_path)
    out_dir = Path(out_dir) if out_dir is not None else md_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = md_path.stem.lower()

    print(f"Preprocessing {md_path}...")
    md_no_tables = load_md_no_tables(str(md_path))
    md_tables = load_md_tables_only(str(md_path))

    out_no_tables = out_dir / f"{slug}_no_tables.md"
    out_tables = out_dir / f"{slug}_tables_only.md"
    out_no_tables.write_text(md_no_tables, encoding="utf-8")
    out_tables.write_text(md_tables, encoding="utf-8")

    print(f"    Saved {out_no_tables}")
    print(f"    Saved {out_tables}")
    return out_no_tables, out_tables


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("md_path", nargs="?", default="../mds/EANS.md")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    run(args.md_path, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
