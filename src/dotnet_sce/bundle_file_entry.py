"""Bundle file entry representation and parsing.

Provides the `BundleFileEntry` dataclass and `FileType` enum equivalent to the
original C# implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .binary_reader import BinaryReader


class FileType(IntEnum):
    UNKNOWN = 0
    ASSEMBLY = 1
    NATIVE_BINARY = 2
    DEPS_JSON = 3
    RUNTIME_CONFIG_JSON = 4
    SYMBOLS = 5
    LAST = 6


@dataclass
class BundleFileEntry:
    offset: int
    size: int
    compressed_size: int
    type: FileType
    relative_path: str

    @property
    def is_valid(self) -> bool:
        return self.offset > 0 and self.size > 0 and self.compressed_size >= 0 and self.type != FileType.LAST

    @classmethod
    def from_reader(cls, reader: BinaryReader, major_version: int) -> "BundleFileEntry":
        offset = reader.read_int64()
        size = reader.read_int64()

        compressed = reader.read_int64() if major_version == 6 else -1

        type_byte = reader.read_byte()
        try:
            ftype = FileType(type_byte)
        except ValueError:
            ftype = FileType.UNKNOWN

        relative = reader.read_path_string()

        entry = cls(offset=offset, size=size, compressed_size=compressed, type=ftype, relative_path=relative)

        if not entry.is_valid:
            raise ValueError(
                f"Failed to parse bundle file entry. Offset: {offset} Size: {size} CompressedSize: {compressed} Type: {ftype}"
            )

        return entry
