"""common."""

import logging
import sys
from subprocess import PIPE, Popen


def configure_logger(level: str = "INFO") -> None:
    """Configure the logger.

    Args:
        level (str, optional): The logging level. Defaults to "INFO".
    """
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def bash_wrapper(command: str) -> tuple[str, int]:
    """Execute a bash command and capture the output.

    Args:
        command (str): The bash command to be executed.

    Returns:
        Tuple[str, int]: A tuple containing the output of the command (stdout) as a string,
        the error output (stderr) as a string (optional), and the return code as an integer.
    """
    # This is a acceptable risk
    process = Popen(command.split(), stdout=PIPE, stderr=PIPE)  # noqa: S603
    output, _ = process.communicate()

    return output.decode(), process.returncode
