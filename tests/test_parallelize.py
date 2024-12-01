"""test_executors."""

import pytest
from pytest_mock import MockerFixture

from system_tools.common import parallelize_process, parallelize_thread


def add(a: int, b: int) -> int:
    """Add."""
    return a + b


def test_parallelize_thread() -> None:
    """test_parallelize_thread."""
    kwargs_list = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    results = parallelize_thread(func=add, kwargs_list=kwargs_list, progress_tracker=1)
    assert results.results == [3, 7]
    assert not results.exceptions


def test_parallelize_thread_exception() -> None:
    """test_parallelize_thread."""
    kwargs_list: list[dict[str, int | None]] = [{"a": 1, "b": 2}, {"a": 3, "b": None}]
    results = parallelize_thread(func=add, kwargs_list=kwargs_list)
    assert results.results == [3]
    output = """[TypeError("unsupported operand type(s) for +: 'int' and 'NoneType'")]"""
    assert str(results.exceptions) == output


def test_parallelize_process() -> None:
    """test_parallelize_process."""
    kwargs_list = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    results = parallelize_process(func=add, kwargs_list=kwargs_list)
    assert results.results == [3, 7]
    assert not results.exceptions


def test_parallelize_process_to_many_max_workers(mocker: MockerFixture) -> None:
    """test_parallelize_process."""
    mocker.patch(target="system_tools.common.parallelize.cpu_count", return_value=1)

    with pytest.raises(RuntimeError, match="max_workers must be less than or equal to 1"):
        parallelize_process(func=add, kwargs_list=[{"a": 1, "b": 2}], max_workers=8)


def test_executor_results_repr() -> None:
    """test_ExecutorResults_repr."""
    results = parallelize_thread(func=add, kwargs_list=[{"a": 1, "b": 2}])
    assert repr(results) == "results=[3] exceptions=[]"


def test_early_error() -> None:
    """test_early_error."""
    kwargs_list: list[dict[str, int | None]] = [{"a": 1, "b": 2}, {"a": 3, "b": None}]
    with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for \+\: 'int' and 'NoneType'"):
        parallelize_thread(func=add, kwargs_list=kwargs_list, mode="early_error")
