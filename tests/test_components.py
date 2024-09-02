"""test_components."""

from os import environ

from pytest_mock import MockerFixture

from system_tools.components import discord_notification, systemd_tests, zpool_tests
from system_tools.zfs import Zpool

temp = "Every feature flags pool has all supported and requested features enabled.\n"


def test_zpool_tests(mocker: MockerFixture) -> None:
    """test_zpool_tests."""
    mock_zpool = mocker.MagicMock(spec=Zpool)
    mock_zpool.health = "ONLINE"
    mock_zpool.capacity = 70
    mock_zpool.name = "Main"
    mocker.patch("system_tools.components.Zpool", return_value=mock_zpool)
    mocker.patch("system_tools.components.bash_wrapper", return_value=(temp, ""))
    errors = zpool_tests(("Main",))
    assert errors == []


def test_zpool_tests_out_of_date(mocker: MockerFixture) -> None:
    """test_zpool_tests_out_of_date."""
    mock_zpool = mocker.MagicMock(spec=Zpool)
    mock_zpool.health = "ONLINE"
    mock_zpool.capacity = 70
    mock_zpool.name = "Main"
    mocker.patch("system_tools.components.Zpool", return_value=mock_zpool)
    mocker.patch("system_tools.components.bash_wrapper", return_value=("", ""))
    errors = zpool_tests(("Main",))
    assert errors == ["ZPool out of date"]


def test_zpool_tests_out_of_space(mocker: MockerFixture) -> None:
    """test_zpool_tests_out_of_space."""
    mock_zpool = mocker.MagicMock(spec=Zpool)
    mock_zpool.health = "ONLINE"
    mock_zpool.capacity = 100
    mock_zpool.name = "Main"
    mocker.patch("system_tools.components.Zpool", return_value=mock_zpool)
    mocker.patch("system_tools.components.bash_wrapper", return_value=(temp, ""))
    errors = zpool_tests(("Main",))
    assert errors == ["Main is low on space"]


def test_zpool_tests_offline(mocker: MockerFixture) -> None:
    """test_zpool_tests_offline."""
    mock_zpool = mocker.MagicMock(spec=Zpool)
    mock_zpool.health = "OFFLINE"
    mock_zpool.capacity = 70
    mock_zpool.name = "Main"
    mocker.patch("system_tools.components.Zpool", return_value=mock_zpool)
    mocker.patch("system_tools.components.bash_wrapper", return_value=(temp, ""))
    errors = zpool_tests(("Main",))
    assert errors == ["Main is OFFLINE"]


def test_systemd_tests() -> None:
    """test_systemd_tests."""
    errors = systemd_tests(("docker",))
    assert errors == []


def test_systemd_tests_multiple_negative_retries() -> None:
    """test_systemd_tests_fail."""
    errors = systemd_tests(("docker",), max_retries=-1, retry_delay_secs=-1)
    assert errors == []


def test_systemd_tests_multiple_pass(mocker: MockerFixture) -> None:
    """test_systemd_tests_fail."""
    mocker.patch(
        "system_tools.components.bash_wrapper",
        side_effect=[
            ("inactive\n", ""),
            ("activating\n", ""),
            ("active\n", ""),
        ],
    )
    errors = systemd_tests(
        ("docker",),
        retryable_statuses=("inactive\n", "activating\n"),
        valid_statuses=("active\n",),
    )
    assert errors == []


def test_systemd_tests_fail(mocker: MockerFixture) -> None:
    """test_systemd_tests_fail."""
    mocker.patch("system_tools.components.bash_wrapper", return_value=("inactive\n", ""))
    errors = systemd_tests(("docker",), max_retries=5)
    assert errors == ["docker is inactive"]


def test_discord_notification(mocker: MockerFixture) -> None:
    """test_discord_notification."""
    environ["WEBHOOK_URL"] = "https://discord.com/api/webhooks/test"
    mocker.patch("system_tools.components.post", return_value=None)
    discord_notification("username", ["error1", "error2"])
