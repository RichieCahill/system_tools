"""Validate Jeevesjr."""

import logging
import sys
from os import environ

from system_tools.common import configure_logger
from system_tools.system_tests.components import discord_notification, systemd_tests, zpool_tests


def main() -> None:
    """Main."""
    configure_logger(level=environ.get("LOG_LEVEL", "INFO"))
    logging.info("Starting Jeevesjr validation")

    errors: list[str] = []
    try:
        if zpool_errors := zpool_tests(("Main",)):
            errors.extend(zpool_errors)

        services = (
            "docker-cloud_flare_tunnel",
            "docker-haproxy",
            "docker-uptime_kuma",
        )

        if systemd_errors := systemd_tests(services):
            errors.extend(systemd_errors)

    except Exception as error:
        logging.exception("Jeevesjr validation failed")
        errors.append(f"Jeevesjr validation failed: {error}")

    if errors:
        logging.error(f"Jeevesjr validation failed: \n{"\n".join(errors)}")
        discord_notification("Jeevesjr validation", errors)

        sys.exit(1)

    logging.info("Jeevesjr validation passed")


if __name__ == "__main__":
    main()
