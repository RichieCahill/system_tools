"""snapshot_manager."""

import logging
import logging.config
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from re import compile as re_compile
from re import search
from tomllib import load as toml_load

from system_tools.common import configure_logger
from system_tools.zfs import Dataset


def load_config_data(config_file: str) -> dict[str, dict[str, int]]:
    """Load a TOML configuration file.

    Args:
        config_file (Path): The path to the configuration file.

    Returns:
        dict: The configuration data.
    """
    with Path(config_file).open("rb") as file:
        return toml_load(file)


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

    snapshots_names = {snapshot.name for snapshot in snapshots}

    filters = (
        ("15_min", re_compile(r"auto_\d{10}(?:15|30|45)"), 6),
        ("hourly", re_compile(r"auto_\d{8}(?!00)\d{2}00"), 24),
        ("daily", re_compile(r"auto_\d{6}(?!01)\d{2}0000"), 31),
        ("monthly", re_compile(r"auto_\d{6}010000"), 12),
    )

    for filter_name, snapshot_filter, default in filters:
        logging.debug(f"{filter_name=}\n{snapshot_filter=}\n{default=}")

        filtered_snapshots = [
            snapshots_name for snapshots_name in snapshots_names if search(snapshot_filter, snapshots_name)
        ]
        filtered_snapshots.sort()

        logging.debug(f"{filtered_snapshots=}")

        snapshots_wanted = count_lookup.get(filter_name, default)
        snapshots_being_deleted = filtered_snapshots[:-snapshots_wanted] if snapshots_wanted > 0 else filtered_snapshots

        logging.info(f"{snapshots_being_deleted} are being deleted")
        for snapshot in snapshots_being_deleted:
            dataset.delete_snapshot(snapshot)


def main() -> None:
    """Main."""
    configure_logger(level="DEBUG")
    logging.info("Starting snapshot_manager")

    parser = ArgumentParser()
    parser.add_argument("--config-file", help="Path to the config file", default="config.toml", type=Path)
    args = parser.parse_args()

    config_data = load_config_data(args.config_file)
    logging.debug(f"{config_data=}")

    now = datetime.now(tz=UTC)
    nearest_15_min = now.replace(minute=(now.minute - (now.minute % 15)))
    time_stamp = nearest_15_min.strftime("auto_%Y%m%d%H%M")

    for dataset_name, count_lookup in config_data.items():
        dataset = Dataset(dataset_name)

        status = dataset.create_snapshot(time_stamp)
        logging.debug(f"{status=}")
        if status != "snapshot created":
            msg = f"{dataset_name} failed to create snapshot {time_stamp}"
            logging.error(msg)
            continue

        get_snapshots_to_delete(dataset, count_lookup)

    logging.info("snapshot_manager completed")


if __name__ == "__main__":
    main()
