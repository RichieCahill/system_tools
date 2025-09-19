from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from system_tools.tools.snapshot_manager import main
from system_tools.zfs.dataset import Dataset

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

SNAPSHOT_MANAGER = "system_tools.tools.snapshot_manager"


def test_main(mocker: MockerFixture, fs: FakeFilesystem) -> None:
    """Test main."""
    mocker.patch(f"{SNAPSHOT_MANAGER}.get_time_stamp", return_value="2023-01-01T00:00:00")

    mock_dataset = mocker.MagicMock(spec=Dataset)
    mock_dataset.name = "test_dataset"
    mock_dataset.create_snapshot.return_value = "snapshot created"
    mock_get_datasets = mocker.patch(f"{SNAPSHOT_MANAGER}.get_datasets", return_value=(mock_dataset,))

    mock_get_snapshots_to_delete = mocker.patch(f"{SNAPSHOT_MANAGER}.get_snapshots_to_delete")
    mock_signal_alert = mocker.patch(f"{SNAPSHOT_MANAGER}.signal_alert")
    mock_snapshot_config_toml = '["default"]\n15_min = 8\nhourly = 24\ndaily = 0\nmonthly = 0\n'
    fs.create_file("/mock_snapshot_config.toml", contents=mock_snapshot_config_toml)
    main(Path("/mock_snapshot_config.toml"))

    mock_signal_alert.assert_not_called()
    mock_get_datasets.assert_called_once()
    mock_get_snapshots_to_delete.assert_called_once_with(
        mock_dataset,
        {
            "15_min": 8,
            "hourly": 24,
            "daily": 0,
            "monthly": 0,
        },
    )
