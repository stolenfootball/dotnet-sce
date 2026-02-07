"""Module entrypoint for `python -m dotnet_sce`.

Delegates to `cli.main`.
"""
from dotnet_sce.cli import main


def _run() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    _run()
