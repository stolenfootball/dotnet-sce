"""Command-line interface for the dotnet_sce package.

Provides a simple `main` function that mirrors the original program's
behaviour: detect or accept a bundle offset and extract files.
"""
from __future__ import annotations

import argparse
import sys

from .bundle import Bundle


def parse_offset(value: str) -> int:
    """Parse an integer offset string in decimal or hex (0x) format."""
    try:
        if value.startswith(("0x", "0X")):
            return int(value, 16)
        return int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Invalid offset value") from exc


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(prog="dotnet-sce", description="Extract files from a self-contained .NET bundle")
    parser.add_argument("file", help="Path to self-contained executable")
    parser.add_argument("output_dir", help="Directory to extract files into")
    parser.add_argument("--offset", type=parse_offset, help="Bundle offset (decimal or 0xHEX)")

    args = parser.parse_args(argv)

    offset = args.offset
    if offset is None:
        found = Bundle.find_bundle_offset(args.input_path)
        if found is None:
            print("Failed to automatically locate bundle offset.")
            return 2
        offset = found

    bundle = Bundle(args.input_path, offset)
    if not bundle.read_bundle():
        return 1

    bundle.extract_files(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
