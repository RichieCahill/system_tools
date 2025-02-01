"""test_server_validate_scripts."""

import pytest
from pytest_mock import MockerFixture

from system_tools.system_tests.validate_system import main

SCRIPT_PATH = "system_tools.system_tests.validate_system"


def test_validate_system(mocker: MockerFixture) -> None:
    """test_validate_system."""
    mocker.patch(f"{SCRIPT_PATH}.ArgumentParser")
    mocker.patch(
        f"{SCRIPT_PATH}.load_config_data",
        return_value={
            "zpools": ["media", "storage"],
            "services": ["docker"],
        },
    )
    mock_discord_notification = mocker.patch(f"{SCRIPT_PATH}.discord_notification", return_value=None)

    mocker.patch(f"{SCRIPT_PATH}.systemd_tests", return_value=None)
    mocker.patch(f"{SCRIPT_PATH}.zpool_tests", return_value=None)

    main()

    assert mock_discord_notification.call_count == 0


def test_validate_system_errors(mocker: MockerFixture) -> None:
    """test_validate_system_errors."""
    mocker.patch(f"{SCRIPT_PATH}.ArgumentParser")
    mocker.patch(
        f"{SCRIPT_PATH}.load_config_data",
        return_value={
            "zpools": ["media", "storage"],
            "services": ["docker"],
        },
    )
    mock_discord_notification = mocker.patch(f"{SCRIPT_PATH}.discord_notification", return_value=None)
    mocker.patch(f"{SCRIPT_PATH}.systemd_tests", return_value=["systemd_tests error"])
    mocker.patch(f"{SCRIPT_PATH}.zpool_tests", return_value=["zpool_tests error"])

    with pytest.raises(SystemExit) as exception_info:
        main()

    assert exception_info.value.code == 1

    assert mock_discord_notification.call_count == 1


def test_validate_system_execution(mocker: MockerFixture) -> None:
    """test_validate_system_execution."""
    mocker.patch(f"{SCRIPT_PATH}.ArgumentParser")
    mocker.patch(
        f"{SCRIPT_PATH}.load_config_data",
        return_value={
            "zpools": ["media", "storage"],
            "services": ["docker"],
        },
    )
    mock_discord_notification = mocker.patch(f"{SCRIPT_PATH}.discord_notification", return_value=None)
    mocker.patch(f"{SCRIPT_PATH}.zpool_tests", side_effect=RuntimeError("zpool_tests error"))

    with pytest.raises(SystemExit) as exception_info:
        main()

    assert exception_info.value.code == 1

    assert mock_discord_notification.call_count == 1


def test_validate_system_no_config_file() -> None:
    """test_validate_system_execution."""
    with pytest.raises(FileNotFoundError) as exception_info:
        main()

    assert exception_info.value.args[0] == "Config file config.toml does not exist"
