"""test_snapshot_manager."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, call

from pytest_mock import MockerFixture

from system_tools.tools.snapshot_manager import delete_snapshots, main
from system_tools.zfs import Dataset, Snapshot

SNAPSHOT_MANAGER = "system_tools.tools.snapshot_manager"


def create_mock_snapshot(name: str) -> MagicMock:
    """create_mock_snapshot."""
    mock_snapshot = MagicMock(spec=Snapshot)
    mock_snapshot.name = name
    return mock_snapshot


def create_mock_dataset(
    name: str = "test_dataset",
    create_snapshot_return_value: str = "snapshot created",
) -> MagicMock:
    """create_mock_dataset."""
    mock_dataset = MagicMock(spec=Dataset)
    mock_dataset.name = name
    mock_dataset.create_snapshot.return_value = create_snapshot_return_value
    return mock_dataset


def test_delete_snapshots() -> None:
    """test_delete_snapshots."""
    mock_dataset = create_mock_dataset()
    mock_dataset.get_snapshots.return_value = [
        create_mock_snapshot(name="auto_202401010000"),
        create_mock_snapshot(name="auto_202401010015"),
        create_mock_snapshot(name="auto_202401010030"),
        create_mock_snapshot(name="auto_202401010045"),
        create_mock_snapshot(name="auto_202401010100"),
        create_mock_snapshot(name="auto_202401010115"),
        create_mock_snapshot(name="auto_202401010130"),
        create_mock_snapshot(name="auto_202401010145"),
        create_mock_snapshot(name="auto_202401010200"),
        create_mock_snapshot(name="auto_202401010300"),
        create_mock_snapshot(name="auto_202401010400"),
        create_mock_snapshot(name="auto_202401010500"),
        create_mock_snapshot(name="auto_202401020000"),
        create_mock_snapshot(name="auto_202401030000"),
        create_mock_snapshot(name="auto_202401040000"),
        create_mock_snapshot(name="auto_202401050000"),
    ]

    delete_snapshots(mock_dataset, {"15_min": 2, "hourly": 1, "daily": 1, "monthly": 1})

    calls = (
        call("auto_202401010015"),
        call("auto_202401010030"),
        call("auto_202401010045"),
        call("auto_202401010100"),
        call("auto_202401010115"),
        call("auto_202401010200"),
        call("auto_202401010300"),
        call("auto_202401010400"),
        call("auto_202401020000"),
        call("auto_202401030000"),
        call("auto_202401040000"),
    )
    mock_dataset.delete_snapshot.assert_has_calls(calls, any_order=True)


def test_delete_snapshots_no_snapshots() -> None:
    """test_delete_snapshots."""
    mock_dataset = MagicMock(spec=Dataset)
    mock_dataset.name = "test_dataset"

    mock_dataset.get_snapshots.return_value = []

    delete_snapshots(mock_dataset, {"15_min": 2, "hourly": 0, "daily": 0, "monthly": 0})

    mock_dataset.delete_snapshot.assert_not_called()


def mock_datetime_now(mocker: MockerFixture, time: datetime) -> None:
    """mock_datetime_now."""
    mock_datetime = mocker.patch(target=f"{SNAPSHOT_MANAGER}.datetime", return_value=mocker.MagicMock)
    mock_datetime.now.return_value = time


def test_main(mocker: MockerFixture) -> None:
    """test_main."""
    mock_dataset = create_mock_dataset(create_snapshot_return_value="snapshot created")

    mock_datetime_now(mocker, datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC))

    mock_delete_snapshots = mocker.patch(f"{SNAPSHOT_MANAGER}.delete_snapshots")
    mocker.patch(f"{SNAPSHOT_MANAGER}.get_time_stamp", return_value="auto_202401010000")
    mocker.patch(f"{SNAPSHOT_MANAGER}.get_datasets", return_value=[mock_dataset])

    main()

    mock_dataset.create_snapshot.assert_called_once_with("auto_202401010000")
    mock_delete_snapshots.assert_called_once_with(
        mock_dataset,
        {"15_min": 4, "hourly": 12, "daily": 0, "monthly": 0},
    )


def test_main_fault(mocker: MockerFixture) -> None:
    """test_main."""
    mock_dataset = create_mock_dataset(create_snapshot_return_value="Failed to create snapshot snapshot for foo")

    mock_datetime_now(mocker, datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC))

    mock_delete_snapshots = mocker.patch(f"{SNAPSHOT_MANAGER}.delete_snapshots")
    mocker.patch(f"{SNAPSHOT_MANAGER}.delete_snapshots")
    mocker.patch(f"{SNAPSHOT_MANAGER}.get_datasets", return_value=[mock_dataset])

    main()

    mock_dataset.create_snapshot.assert_called_once_with("auto_202401010000")
    mock_delete_snapshots.assert_not_called()
