"""test_executors."""

from __future__ import annotations

from concurrent.futures import Executor
from typing import TYPE_CHECKING, Any

import pytest

from system_tools.common import parallelize_process, parallelize_thread
from system_tools.common.parallelize import _parallelize_base

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_mock import MockerFixture


class MockFuture:
    """MockFuture."""

    def __init__(self, result: Any) -> None:  # noqa: ANN401
        """Init."""
        self._result = result
        self._exception: Exception | None = None

    def exception(self) -> Exception | None:
        """Exception."""
        return self._exception

    def result(self) -> Any:  # noqa: ANN401
        """Result."""
        return self._result


class MockPoolExecutor(Executor):
    """MockPoolExecutor."""

    def __init__(
        self,
        max_workers: int | None = None,
        thread_name_prefix: str = "",
        initializer: Callable[..., None] | None = None,
        initargs: tuple[Any, ...] = (),
    ) -> None:
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pass to the initializer.
        """
        self._max_workers = max_workers
        self._thread_name_prefix = thread_name_prefix
        self._initializer = initializer
        self._initargs = initargs

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> MockFuture:  # noqa: ANN401
        """Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        Args:
            fn: The callable to execute.
            *args: The positional arguments to pass to the callable.
            **kwargs: The keyword arguments to pass to the callable.

        Returns:
            A Future instance representing the execution of the callable.
        """
        result = fn(*args, **kwargs)

        return MockFuture(result)


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


def test_mock_pool_executor() -> None:
    """test_mock_pool_executor."""
    results = _parallelize_base(
        executor_type=MockPoolExecutor,
        func=add,
        kwargs_list=[{"a": 1, "b": 2}, {"a": 3, "b": 4}],
        max_workers=None,
        progress_tracker=None,
        mode="normal",
    )
    assert repr(results) == "results=[3, 7] exceptions=[]"
