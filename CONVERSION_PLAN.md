# .NET -> Python Conversion Plan

Project: SelfContainedExtractor (DotNetSelfContainedExtractor)

Date: 2026-02-06

Author: GitHub Copilot (assistant)

## Overview

This document defines a step-by-step plan to convert the C# project `SelfContainedExtractor/DotNetSelfContainedExtractor` into Python, implementing the main module under `src/dotnet_sce` in this repository. The C# project reads .NET self-contained bundle files, parses headers/entries, optionally decompresses assets, and writes contained files to an output folder. The Python port will replicate this behavior and provide a CLI-compatible entrypoint.

## Scope

- Convert all C# source files in `SelfContainedExtractor/DotNetSelfContainedExtractor` to Python equivalents.
- Preserve command-line usage: `DotNetSelfContainedExtractor.exe <self-contained app> <output dir> [bundle file offset]` → Python CLI `python -m dotnet_sce <app> <out> [--offset HEX]`.
- Provide unit/integration tests for core parsing and extraction logic.
- Keep the Python package structure under `src/dotnet_sce` and make it importable as `dotnet_sce`.

## Files to convert and target mapping

- `BinaryReaderExtensions.cs` → `src/dotnet_sce/binary_reader.py`
  - Implement helper functions for reading primitives, endianness, and any extension methods used by the C# BinaryReader code.
  - Provide a small wrapper around `io.BytesIO` / `struct` for convenient reading.

- `BundleHeader.cs` → `src/dotnet_sce/bundle_header.py`
  - Implement `BundleHeader` dataclass with parsing methods to read header fields from a bytes stream.

- `BundleFileEntry.cs` → `src/dotnet_sce/bundle_file_entry.py`
  - Implement `BundleFileEntry` dataclass with fields for name, offset, size, compressed flag, and parsing logic.

- `Bundle.cs` → `src/dotnet_sce/bundle.py`
  - Implement `Bundle` class that opens the executable, seeks to the bundle, reads header and entries, handles decompression (zlib), and exposes extraction API.

- `Program.cs` → `src/dotnet_sce/__main__.py` and `src/dotnet_sce/cli.py`
  - Implement CLI parsing with `argparse` and invoke `Bundle` extraction logic. Support optional `--offset` in hex or decimal.

- `.csproj` / `.sln` files → Document any .NET-specific behavior in `CONVERSION_PLAN.md` and `README.md`; no direct conversion.

## Detailed Conversion Steps

1. Prepare workspace
   - Ensure Python virtual environment and project dependencies (none external required beyond standard library; `zlib` is stdlib). If asynchronous file IO or performance libs are desired, consider optional dependencies later.

2. Inventory C# source and behavior
   - Read each C# file and note public APIs, helper methods, and any platform-specific calls (file maps, runtime calls, etc.).

3. Design Python package layout
   - `src/dotnet_sce/__init__.py` — package exports and version
   - `src/dotnet_sce/cli.py` — CLI logic
   - `src/dotnet_sce/__main__.py` — module entrypoint
   - `src/dotnet_sce/binary_reader.py` — binary helpers
   - `src/dotnet_sce/bundle_header.py` — header dataclass
   - `src/dotnet_sce/bundle_file_entry.py` — entry dataclass
   - `src/dotnet_sce/bundle.py` — core bundle parsing/extraction
   - `tests/` — unit and integration tests (pytest)

4. Implement binary reading helpers
   - Provide functions: `read_uint32`, `read_uint64`, `read_int32`, `read_bytes`, `read_cstring` (null-terminated), and helpers to parse variable-length integers if used.
   - Use `struct.unpack_from` and `memoryview` to avoid copies where needed.

5. Implement `BundleHeader` and `BundleFileEntry`
   - Translate struct layouts from C# to Python parsing logic.
   - Represent them as `@dataclass` with `from_stream(stream)` classmethods.

6. Implement `Bundle` class
   - Responsibilities:
     - Find and validate the bundle start (use provided offset or autodetect by scanning expected signature and header layout).
     - Read header and the number of files.
     - Read each entry metadata, track offsets/sizes.
     - For compressed entries, use `zlib.decompress` to decompress data before writing.
     - Expose `extract_all(output_dir)` and `extract_entry(entry, out_path)` functions.
   - Verify file offsets are read and applied consistently (note: consider that offsets in bundle may be relative to bundle start or absolute—mirror C# logic).

7. Implement CLI
   - Use `argparse`.
   - Accept `input_path`, `output_dir`, `--offset` (hex literal with 0x prefix or decimal), `--dry-run`, and `--verbose` flags.
   - Map behavior to C# program: if offset omitted, attempt autodetection.

8. Tests
   - Unit tests for binary helpers, header parsing, and entry parsing.
   - Integration test: run extraction on a small known bundle (include a tiny synthetic test fixture) and verify files are extracted and decompressed where expected.

9. Documentation and examples
   - Update `README.md` at repo root with Python usage examples and requirements (Python version).
   - Add `CONVERSION_PLAN.md` into repo root (this file).

10. Packaging & distribution
   - Ensure `pyproject.toml` already present; update with any optional dependencies and set `project.scripts` or `console_scripts` entry for CLI if desired.

## Risks & Notes

- Endianness and signed/unsigned differences: confirm same behavior as C# `BinaryReader` (little-endian typical for PE files).
- File offsets: must confirm whether offsets in entries are absolute or relative to the bundle start; preserve logic from C# `Bundle` implementation.
- Compression: the C# code references zlib; Python's `zlib` module will be used.
- Performance: for very large bundles, streaming decompression and incremental writes are preferred.

## Work plan (phases & checkpoints)

- Phase 1: Readme + inventory (complete).
- Phase 2: Package skeleton + binary helpers.
- Phase 3: Header/entry parsing + unit tests.
- Phase 4: Bundle parsing + extraction + integration tests.
- Phase 5: CLI, docs, and final polishing.

## Estimated time (rough)

- Phase 1: 0.5–1 hour
- Phase 2: 1–2 hours
- Phase 3: 1–3 hours
- Phase 4: 2–4 hours
- Phase 5: 1–2 hours

## Next immediate actions

1. Inventory C# source files and open each to map exact parsing logic.
2. Create Python package skeleton files under `src/dotnet_sce`.
3. Implement `binary_reader.py` and add unit tests.

---

If you want, I can now inventory the C# files in `SelfContainedExtractor/DotNetSelfContainedExtractor`, then scaffold the Python package skeleton and convert `BinaryReaderExtensions.cs` first. Tell me which step to start with, or I can proceed autonomously.

## Progress updates

- 2026-02-06: Inventory of C# files completed; README reviewed.
- 2026-02-06: Scaffolding: created package skeleton files under `src/dotnet_sce`:
   - `__init__.py`, `__main__.py`, `cli.py`, `binary_reader.py`, `bundle_header.py`, `bundle_file_entry.py`, `bundle.py`.

Next: implement unit tests for `binary_reader` and parsing logic, then translate remaining fine-grained behaviors and edge cases from the C# implementation into tests and code.
