"""Arch Mirror."""

import logging
from contextlib import suppress
from os import environ

import polars as pl
from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore[import]
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore[import]
from requests import get

from system_tools.common import bash_wrapper


def rsync_command(source_url: str, mirror_dir: str) -> bool:
    """Rsync command.

    Args:
        source_url (str): Source URL.
        mirror_dir (str): Target dir.
        bwlimit (int, optional): KBytes bandwidth limit. Defaults to 0.
    """
    rsync = "rsync -rlptH --safe-links --delete-delay --delay-updates --timeout=600 --contimeout=60 --no-motd"

    rsync += f" {source_url} {mirror_dir}"

    rsync += " -v"

    stdout, returncode = bash_wrapper(rsync)

    if returncode != 0:
        logging.warning(f"rsync failed with return code {returncode} and message {stdout}")
        return False

    return True


def get_mirror_list() -> pl.DataFrame:
    """Get mirror list.

    Returns:
        pl.DataFrame: Mirror list.
    """
    logging.info("Getting mirror list")

    mirror_list = "https://archlinux.org/mirrors/status/tier/1/json/"
    response = get(mirror_list, timeout=5)

    mirror_urls = response.json()["urls"]
    logging.debug(f"{mirror_urls=}")

    return pl.DataFrame(mirror_urls)


def get_rsync_urls(data_frame: pl.DataFrame) -> list[str]:
    """Get rsync URLs.

    Args:
        data_frame (pl.DataFrame): Data frame.

    Returns:
        list[str]: Rsync URLs.
    """
    logging.info("Getting rsync URLs")

    seconds = 1 * 60 * 60
    completion_percentage = 0.7
    us_data_frame = data_frame.filter(
        (data_frame["country_code"] == "US")
        & (data_frame["protocol"] == "rsync")
        & (data_frame["completion_pct"] > completion_percentage)
        & (data_frame["delay"] < seconds)
    )
    rsync_urls = list(us_data_frame.sort("delay").head(5).select("url").to_series())
    logging.debug(f"{rsync_urls=}")

    return rsync_urls


def rsync(source_url: str, mirror_dir: str, attempts: int) -> bool:
    """Run rsync attempts number of times.

    Args:
        source_url (str): Source URL.
        mirror_dir (str): Target dir.
        attempts (int): Number of attempts.

    Returns:
        bool: Success.
    """
    logging.info(f"Syncing {source_url}")

    for attempt in range(1, attempts):
        if rsync_command(source_url=source_url, mirror_dir=mirror_dir):
            return True
        logging.error(f"{source_url} Attempt {attempt} failed")

    logging.error(f"{source_url} failed after 3 attempts")
    return False


def sync_mirror() -> None:
    """Sync mirror.

    Args:
        rsync_urls (list[str]): Rsync URLs.
    """
    logging.info("Syncing mirror")

    data_frame = get_mirror_list()

    rsync_urls = get_rsync_urls(data_frame)
    mirror_dir = environ["MIRROR_DIR"]
    for rsync_url in rsync_urls:
        if rsync(rsync_url, mirror_dir, 3):
            logging.info(f"Sync completed with {rsync_url}")
            return

    logging.error("All rsync URLs failed")


def main() -> None:
    """Main."""
    logging.basicConfig(level="INFO")

    logging.info("Starting arch_mirror scheduler")

    sync_mirror_trigger = IntervalTrigger(minutes=5)
    with suppress(KeyboardInterrupt, SystemExit):
        scheduler = BlockingScheduler()
        scheduler.add_job(sync_mirror, trigger=sync_mirror_trigger)
        scheduler.start()


if __name__ == "__main__":
    main()
