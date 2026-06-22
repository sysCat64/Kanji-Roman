from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from kanji_roman_generator.curation import load_curation
from kanji_roman_generator.internal_json import (
    generate_internal_group,
    write_internal_group,
)
from kanji_roman_generator.radicals import (
    find_radical_definition,
    load_radical_definitions,
)
from kanji_roman_generator.site_json import (
    public_radical_from_internal_group,
    write_public_radical,
)
from kanji_roman_generator.unihan import load_krsunicode_from_zip


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    radical_definitions = load_radical_definitions(args.radicals)
    radical_numbers_by_char = load_krsunicode_from_zip(args.unihan)
    radical_ids = _target_radical_ids(args, radical_definitions)

    out_dir = Path(args.out_dir)
    for radical_id in radical_ids:
        curation_by_char = _load_curation_for_radical(args.curation_dir, radical_id)
        group = generate_internal_group(
            radical_id,
            radical_definitions,
            radical_numbers_by_char,
            sort_order=args.sort,
            unihan_source_file=str(args.unihan),
            curation_by_char=curation_by_char,
        )
        for warning in group.get("warnings", []):
            print(warning["message"], file=sys.stderr)
        write_internal_group(out_dir / f"{radical_id}.json", group)
        if args.site_data_dir is not None:
            radical = find_radical_definition(radical_definitions, radical_id)
            public_radical = public_radical_from_internal_group(
                group,
                radical,
                reviewed_only=args.reviewed_only,
            )
            write_public_radical(
                Path(args.site_data_dir) / "radicals" / f"{radical_id}.json",
                public_radical,
            )

    return 0


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Kanji-Roman internal radical JSON."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--radical", help="Generate one radical id.")
    target.add_argument("--all", action="store_true", help="Generate all radicals.")
    parser.add_argument("--radicals", required=True, type=Path)
    parser.add_argument("--unihan", required=True, type=Path)
    parser.add_argument("--curation-dir", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--site-data-dir", type=Path)
    parser.add_argument("--default-radical")
    parser.add_argument("--sort", choices=("jis", "unicode"), default="jis")
    parser.add_argument(
        "--include-unreviewed",
        action="store_true",
        default=True,
        help="Accepted for Phase 3; unreviewed items are included by default.",
    )
    parser.add_argument(
        "--reviewed-only",
        action="store_true",
        help="Accepted for future curation filtering.",
    )
    return parser.parse_args(argv)


def _target_radical_ids(
    args: argparse.Namespace,
    radical_definitions: Sequence[dict],
) -> list[str]:
    if args.all:
        return [str(radical["id"]) for radical in radical_definitions]
    return [str(args.radical)]


def _load_curation_for_radical(
    curation_dir: Path | None,
    radical_id: str,
) -> dict:
    if curation_dir is None:
        return {}
    return load_curation(curation_dir / f"{radical_id}.json")


if __name__ == "__main__":
    raise SystemExit(main())
