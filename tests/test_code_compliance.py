"""Test code compliance."""

from re import match

from system_tools.common import bash_wrapper


def test_ruff_check() -> None:
    """Test ruff check."""
    stdout, returncode = bash_wrapper("poetry run ruff check .")
    assert stdout == "All checks passed!\n"
    assert returncode == 0


def test_ruff_format() -> None:
    """Test ruff format."""
    stdout, returncode = bash_wrapper("poetry run ruff format --check .")
    test = stdout.strip()
    assert match(r"[\d]* files already formatted", test)
    assert returncode == 0


def test_mypy_check() -> None:
    """Test mypy check."""
    stdout, returncode = bash_wrapper("poetry run mypy .")
    test = stdout.strip()
    assert match(r"Success: no issues found in [\d]* source files", test)
    assert returncode == 0
