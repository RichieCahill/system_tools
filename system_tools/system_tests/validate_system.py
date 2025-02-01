"""Validate Jeeves."""

import logging
import sys
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from tomllib import load as toml_load

from system_tools.common import configure_logger
from system_tools.system_tests.components import discord_notification, systemd_tests, zpool_tests


def load_config_data(config_file: str) -> dict[str, list[str]]:
    """Load a TOML configuration file.

    Args:
        config_file (Path): The path to the configuration file.

    Returns:
        dict: The configuration data.
    """
    with Path(config_file).open("rb") as file:
        return toml_load(file)


def main() -> None:
    """Main."""
    configure_logger(level=environ.get("LOG_LEVEL", "INFO"))
    logging.info("Starting jeeves validation")

    parser = ArgumentParser()
    parser.add_argument("--config-file", help="Path to the config file", default="config.toml", type=Path)
    args = parser.parse_args()

    if not args.config_file.exists():
        error = f"Config file {args.config_file} does not exist"
        raise FileNotFoundError(error)

    config_data = load_config_data(args.config_file)

    errors: list[str] = []
    try:
        if config_data.get("zpools") and (zpool_errors := zpool_tests(config_data["zpools"])):
            errors.extend(zpool_errors)

        if config_data.get("services") and (systemd_errors := systemd_tests(config_data["services"])):
            errors.extend(systemd_errors)

    except Exception as error:
        logging.exception("Jeeves validation failed")
        errors.append(f"Jeeves validation failed: {error}")

    if errors:
        logging.error(f"Jeeves validation failed: \n{'\n'.join(errors)}")
        discord_notification("jeeves", errors)

        sys.exit(1)

    logging.info("Jeeves validation passed")


if __name__ == "__main__":
    main()
