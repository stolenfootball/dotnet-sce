"""Core bundle parsing and extraction logic.

This module implements `Bundle` which can locate a .NET self-contained
bundle within an executable, parse the header and entries, and extract
embedded files to disk.
"""
from __future__ import annotations

import os
import struct
import zlib
from io import BytesIO
from typing import List, Optional

from .binary_reader import BinaryReader
from .bundle_header import BundleHeader
from .bundle_file_entry import BundleFileEntry


class Bundle:
    """Represents a parsed self-contained .NET bundle.

    Attributes:
        bundle_path: Path to the executable containing the bundle.
        bundle_offset: Offset where the bundle header starts.
        embedded_files: Parsed list of BundleFileEntry objects.
    """

    def __init__(self, bundle_path: str, bundle_offset: int) -> None:
        self._bundle_path = bundle_path
        self._bundle_offset = bundle_offset
        self.embedded_files: List[BundleFileEntry] = []
        self.header: Optional[BundleHeader] = None

    @staticmethod
    def find_bundle_offset(bundle_path: str) -> Optional[int]:
        """Locate the bundle offset inside a self-contained executable.

        Returns the offset (int) if found, otherwise None.
        """
        test_guid_bytes = bytes(
            [
                0x33, 0x38, 0x63, 0x63, 0x38, 0x32, 0x37, 0x2d, 0x65, 0x33, 0x34, 0x66,
                0x2d, 0x34, 0x34, 0x35, 0x33, 0x2d, 0x39, 0x64, 0x66, 0x34, 0x2d, 0x31,
                0x65, 0x37, 0x39, 0x36, 0x65, 0x39, 0x66, 0x31, 0x64, 0x30, 0x37,
            ]
        )

        with open(bundle_path, "rb") as fh:
            data = fh.read()

        # PE header location at 0x3c
        if len(data) < 0x40:
            return None

        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        pe_machine_type = struct.unpack_from("<H", data, pe_offset + 4)[0]

        guid_bundle_offset = (
            (0x1 + 0x8 + 0x20 + 0x8) if pe_machine_type == 0x14C else (0x1 + 0x10 + 0x20 + 0x8)
        )

        idx = data.find(test_guid_bytes)
        if idx == -1:
            return None

        # Read little-endian 32-bit integer at the computed location
        target_index = idx - guid_bundle_offset
        if target_index < 0 or target_index + 4 > len(data):
            return None

        bundle_offset = struct.unpack_from("<i", data, target_index)[0]
        return bundle_offset

    def read_bundle(self) -> bool:
        """Parse the bundle header and entries. Returns True on success."""
        with open(self._bundle_path, "rb") as fh:
            data = fh.read()

        stream = BytesIO(data)
        reader = BinaryReader(stream)
        reader.seek(self._bundle_offset)

        try:
            self.header = BundleHeader.from_reader(reader)
        except Exception as exc:  # pylint: disable=broad-except
            print("Error while parsing bundle header.")
            print(str(exc))
            return False

        print(f"Bundle details:")
        print(f"Bundle ID: {self.header.bundle_id}")
        print(f"Version: {self.header.major_version}.{self.header.minor_version}")
        print(f"Embedded files count: {self.header.embedded_files_count}")

        try:
            for _ in range(self.header.embedded_files_count):
                entry = BundleFileEntry.from_reader(reader, self.header.major_version)
                print(f"Embedded file info: Name: {entry.relative_path}, Size: {entry.size}, Type: {entry.type}")
                self.embedded_files.append(entry)
        except Exception as exc:  # pylint: disable=broad-except
            print("Error while parsing embedded bundle files.")
            print(str(exc))
            return False

        return True

    def extract_files(self, output_directory: str) -> None:
        """Extract all parsed embedded files into `output_directory`."""
        os.makedirs(output_directory, exist_ok=True)

        with open(self._bundle_path, "rb") as fh:
            for entry in self.embedded_files:
                out_path = os.path.join(output_directory, entry.relative_path)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                fh.seek(entry.offset)
                if entry.compressed_size and entry.compressed_size != 0:
                    compressed = fh.read(entry.compressed_size)
                    # zlib headerless stream may be used in some bundles; the C# code
                    # uses a ZLibStream wrapper that expects zlib-wrapped data.
                    try:
                        decompressed = zlib.decompress(compressed)
                    except zlib.error:
                        # Try raw DEFLATE stream
                        decompressed = zlib.decompress(compressed, -zlib.MAX_WBITS)

                    with open(out_path, "wb") as out_fh:
                        out_fh.write(decompressed)
                else:
                    data = fh.read(entry.size)
                    with open(out_path, "wb") as out_fh:
                        out_fh.write(data)

                print(f"Successfully extracted file {entry.relative_path}.")
