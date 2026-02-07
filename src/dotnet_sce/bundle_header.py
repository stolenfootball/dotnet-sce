"""Bundle header parsing and dataclasses.

This module provides a dataclass representation of the bundle header and
its substructures. Parsing is performed from a `BinaryReader` instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

from .binary_reader import BinaryReader


@dataclass
class Location:
    offset: int
    size: int

    @property
    def is_valid(self) -> bool:
        return self.offset != 0

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> "Location":
        return cls(offset=reader.read_int64(), size=reader.read_int64())


@dataclass
class BundleHeader:
    major_version: int
    minor_version: int
    embedded_files_count: int
    bundle_id: str
    deps_json_location: Location
    runtime_config_json_location: Location
    flags: int

    @property
    def is_valid(self) -> bool:
        return (
            self.embedded_files_count > 0
            and self.minor_version == 0
            and self.major_version in (6, 2)
        )

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> "BundleHeader":
        major = reader.read_uint32()
        minor = reader.read_uint32()
        embedded = reader.read_int32()

        header = cls(
            major_version=major,
            minor_version=minor,
            embedded_files_count=embedded,
            bundle_id="",
            deps_json_location=Location(0, 0),
            runtime_config_json_location=Location(0, 0),
            flags=0,
        )

        if not header.is_valid:
            raise ValueError(
                f"Failed to parse bundle. Parsed data: Version: {major}.{minor}, Embedded file count: {embedded}"
            )

        bundle_id = reader.read_path_string()
        deps = Location.from_reader(reader)
        runtime_cfg = Location.from_reader(reader)
        flags = reader.read_uint64()

        return cls(
            major_version=major,
            minor_version=minor,
            embedded_files_count=embedded,
            bundle_id=bundle_id,
            deps_json_location=deps,
            runtime_config_json_location=runtime_cfg,
            flags=flags,
        )
