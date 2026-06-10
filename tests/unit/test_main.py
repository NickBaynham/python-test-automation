"""Unit tests for the command-line entry point."""

import pytest

from testplatform import __version__
from testplatform.__main__ import main


def test_main_reports_name_and_version(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    assert capsys.readouterr().out == f"testplatform {__version__}\n"
