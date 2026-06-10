"""Command-line entry point."""

from testplatform import __version__


def main() -> None:
    """Report the platform name and version."""
    print(f"testplatform {__version__}")


if __name__ == "__main__":
    main()
