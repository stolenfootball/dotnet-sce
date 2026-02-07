# dotnet-sce

Extract assemblies and resources from self-contained .NET 5+ executables.

This is a Python conversion of the [SelfContainedExtractor](https://github.com/LukeFZ/SelfContainedExtractor) project, providing cross-platform bundle extraction with a simple command-line interface.

## Features

- **Automatic bundle detection**: Scans executable PE headers to locate the embedded bundle
- **Optional manual offset**: Provide the bundle offset explicitly if needed
- **Transparent decompression**: Automatically handles compressed (zlib) and uncompressed files
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Single-file extraction**: Extract individual files without extracting the entire bundle

## How It Works

Self-contained .NET executables (.NET 5+) bundle all required runtime files and dependencies into a single executable file. This tool locates and parses the internal bundle structure to extract:

- Application assemblies (.dll files)
- Runtime configuration files (.runtimeconfig.json, .deps.json)
- System libraries and dependencies
- Supporting native binaries

The extraction process:
1. Scans the PE (Portable Executable) header to locate the bundle signature
2. Reads the bundle header to determine format version and file count
3. Parses individual file entries (offset, size, compression status, type)
4. Decompresses files as needed using zlib
5. Writes extracted files to the output directory, preserving structure

## Installation

### Via PyPI (recommended)

Install the latest released version from [PyPI](https://pypi.org/project/dotnet-sce/):

```bash
pip install dotnet-sce
```

Or with `uv`:

```bash
uv pip install dotnet-sce
```

After installation, the `dotnet-sce` command will be available globally:

```bash
dotnet-sce --help
```

### From source (development)

#### Requirements

- Python 3.8 or later
- `uv` package manager (or `pip`)

#### Installation

```bash
git clone https://github.com/yourusername/dotnet-sce.git
cd dotnet-sce
uv pip install -e .
```

Or with development dependencies:

```bash
uv pip install -e ".[dev]"
```

With `pip`:

```bash
pip install -e .
```

## Usage

### Basic usage (auto-detect bundle offset)

```bash
dotnet-sce <executable> <output-directory>
```

Example:
```bash
dotnet-sce MyApp.exe ./extracted_files
```

### Specify bundle offset manually

If auto-detection fails, you can provide the offset explicitly (in decimal or hex):

```bash
# Decimal offset
dotnet-sce MyApp.exe ./extracted_files --offset 1048576

# Hexadecimal offset
dotnet-sce MyApp.exe ./extracted_files --offset 0x100000
```

### Display help

```bash
dotnet-sce -h
```

## Example Output

```
$ dotnet-sce samples/WinChatClient.exe samples_out

Bundle details:
Bundle ID: wA4enLQ_7Ls8
Version: 6.0
Embedded files count: 171

Embedded file info: Name: WinChatClient.dll, Size: 14848, Type: 1
Embedded file info: Name: WinChatClient.runtimeconfig.json, Size: 372, Type: 4
...
Successfully extracted file WinChatClient.dll.
Successfully extracted file WinChatClient.runtimeconfig.json.
...
```

## Architecture

The project follows a modular design:

- `binary_reader.py` — Low-level binary I/O with variable-length encoding support
- `bundle_header.py` — Bundle header parsing and validation
- `bundle_file_entry.py` — File entry metadata and type enumeration
- `bundle.py` — Core extraction logic
- `cli.py` — Command-line argument parsing and orchestration

All modules follow Google Python style conventions and include comprehensive docstrings.

## Testing

Run the included test suite:

```bash
uv run pytest
```

Test the tool with the sample bundle:

```bash
uv run dotnet-sce samples/WinChatClient.exe samples_out
```

## Limitations

- Only supports .NET 5+ self-contained executables (versions 2.x and 6.x bundles)
- Does not support bundled native executables or platform-specific resources
- Offset auto-detection works best on unmodified official .NET self-contained builds

## Attribution

This project is a Python conversion of [SelfContainedExtractor](https://github.com/LukeFZ/SelfContainedExtractor) by [LukeFZ](https://github.com/LukeFZ).

The original C# implementation was reverse-engineered from the [.NET Runtime source code](https://github.com/dotnet/runtime/tree/main/src/native/corehost/bundle) and ported to Python for broader compatibility and ease of use.

The Python version maintains feature parity with the original while providing improved usability through:
- A simpler installation process
- Better error messages with contextual help
- Cross-platform compatibility without .NET dependencies
- Type hints and improved code documentation

## License

This project is provided as-is for educational and practical use. Refer to the original [SelfContainedExtractor repository](https://github.com/LukeFZ/SelfContainedExtractor) for licensing details.
