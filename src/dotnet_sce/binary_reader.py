"""Binary reading helpers mirroring the C# BinaryReaderExtensions behavior.

This module provides a small `BinaryReader` class that wraps a binary
file-like object and provides convenient methods for reading primitives
and the path-string format used in .NET bundles.
"""
from __future__ import annotations

import struct
from io import BufferedReader, BytesIO
from typing import BinaryIO


class BinaryReader:
    """Simple binary reader for little-endian primitives.

    The reader expects the underlying stream to be seekable.
    """

    def __init__(self, stream: BinaryIO) -> None:
        self._stream = stream

    def seek(self, offset: int, whence: int = 0) -> None:
        self._stream.seek(offset, whence)

    def read_bytes(self, size: int) -> bytes:
        data = self._stream.read(size)
        if len(data) != size:
            raise EOFError("Unexpected end of stream")
        return data

    def read_byte(self) -> int:
        data = self.read_bytes(1)
        return data[0]

    def read_int32(self) -> int:
        return struct.unpack("<i", self.read_bytes(4))[0]

    def read_uint32(self) -> int:
        return struct.unpack("<I", self.read_bytes(4))[0]

    def read_int64(self) -> int:
        return struct.unpack("<q", self.read_bytes(8))[0]

    def read_uint64(self) -> int:
        return struct.unpack("<Q", self.read_bytes(8))[0]

    def read_path_length(self) -> int:
        """Read the variable-length path length used by .NET bundle format.

        Implements the same two-byte max-length logic as the original C#.
        """
        first = self.read_byte()
        if (first & 0x80) == 0:
            length = first
        else:
            second = self.read_byte()
            if (second & 0x80) != 0:
                raise ValueError("Bundle path length attempted to read beyond two bytes.")
            length = (second << 7) | (first & 0x7F)

        if length <= 0 or length > 4095:
            raise ValueError("Read invalid path length from bundle.")

        return length

    def read_path_string(self) -> str:
        length = self.read_path_length()
        raw = self.read_bytes(length)
        return raw.decode("utf-8")
