"""snapshot_manager."""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime
from functools import cache
from re import compile as re_compile
from re import search
from tomllib import load as toml_load
from typing import TYPE_CHECKING

import typer

from system_tools.common import configure_logger, signal_alert
from system_tools.zfs import Dataset, get_datasets

if TYPE_CHECKING:
    from pathlib import Path


def main(config_file: Path) -> None:
    """Main."""
    configure_logger(level="DEBUG")
    logging.info("Starting snapshot_manager")

    try:
        config_data = load_config_data(config_file)
        logging.debug(f"{config_data=}")

        time_stamp = get_time_stamp()

        default_config = config_data.get(
            "default",
            {"15_min": 4, "hourly": 12, "daily": 0, "monthly": 0},
        )

        for dataset in get_datasets():
            dataset_name = dataset.name
            status = dataset.create_snapshot(time_stamp)
            logging.debug(f"{status=}")
            if status != "snapshot created":
                msg = f"{dataset_name} failed to create snapshot {time_stamp}"
                logging.error(msg)
                signal_alert(msg)
                continue

            count_lookup = config_data.get(dataset_name, default_config)

            get_snapshots_to_delete(dataset, count_lookup)
    except Exception:
        logging.exception("snapshot_manager failed")
        signal_alert("snapshot_manager failed")
        sys.exit(1)
    else:
        logging.info("snapshot_manager completed")


@cache
def load_config_data(config_file: Path) -> dict[str, dict[str, int]]:
    """Load a TOML configuration file.

    Args:
        config_file (Path): The path to the configuration file.

    Returns:
        dict: The configuration data.
    """
    if config_file.exists():
        with config_file.open("rb") as file:
            return toml_load(file)
    return {}


def get_snapshots_to_delete(
    dataset: Dataset,
    count_lookup: dict[str, int],
) -> None:
    """Get snapshots to delete.

    Args:
        dataset (Dataset): the dataset
        count_lookup (dict[str, int]): the count lookup
    """
    snapshots = dataset.get_snapshots()

    if not snapshots:
        logging.info(f"{dataset.name} has no snapshots")
        return

    filters = (
        ("15_min", re_compile(r"auto_\d{10}(?:15|30|45)")),
        ("hourly", re_compile(r"auto_\d{8}(?!00)\d{2}00")),
        ("daily", re_compile(r"auto_\d{6}(?!01)\d{2}0000")),
        ("monthly", re_compile(r"auto_\d{6}010000")),
    )

    for filter_name, snapshot_filter in filters:
        logging.debug(f"{filter_name=}\n{snapshot_filter=}")

        filtered_snapshots = sorted(snapshot.name for snapshot in snapshots if search(snapshot_filter, snapshot.name))

        logging.debug(f"{filtered_snapshots=}")

        snapshots_wanted = count_lookup[filter_name]
        snapshots_being_deleted = filtered_snapshots[:-snapshots_wanted] if snapshots_wanted > 0 else filtered_snapshots

        logging.info(f"{snapshots_being_deleted} are being deleted")
        for snapshot in snapshots_being_deleted:
            if error := dataset.delete_snapshot(snapshot):
                error_message = f"{dataset.name}@{snapshot} failed to delete: {error}"
                signal_alert(error_message)
                logging.error(error_message)


def get_time_stamp() -> str:
    """Get the time stamp."""
    now = datetime.now(tz=UTC)
    nearest_15_min = now.replace(minute=(now.minute - (now.minute % 15)))
    return nearest_15_min.strftime("auto_%Y%m%d%H%M")


if __name__ == "__main__":
    typer.run(main)
