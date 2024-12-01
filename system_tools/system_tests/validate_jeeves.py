"""Validate Jeeves."""

import logging
import sys
from os import environ

from system_tools.common import configure_logger
from system_tools.system_tests.components import discord_notification, systemd_tests, zpool_tests


def main() -> None:
    """Main."""
    configure_logger(level=environ.get("LOG_LEVEL", "INFO"))
    logging.info("Starting jeeves validation")

    errors: list[str] = []
    try:
        if zpool_errors := zpool_tests(("media", "storage", "torrenting")):
            errors.extend(zpool_errors)

        services = (
            "docker-arch_mirror",
            "docker-cloud_flare_tunnel",
            "docker-filebrowser",
            "docker-grafana",
            "docker-haproxy",
            "docker-qbit",
            "docker-qbitvpn",
            "docker-uptime_kuma",
            "docker",
            "plex",
            "sync_mirror",
        )
        if systemd_errors := systemd_tests(services):
            errors.extend(systemd_errors)

    except Exception as error:
        logging.exception("Jeeves validation failed")
        errors.append(f"Jeeves validation failed: {error}")

    if errors:
        logging.error(f"Jeeves validation failed: \n{"\n".join(errors)}")
        discord_notification("jeeves", errors)

        sys.exit(1)

    logging.info("Jeeves validation passed")


if __name__ == "__main__":
    main()
