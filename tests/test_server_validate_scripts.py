"""test_server_validate_scripts."""

import pytest
from pytest_mock import MockerFixture

from system_tools.system_tests import validate_jeeves, validate_jeevesjr


class TestJeeves:
    """Jeeves."""

    script_path = "system_tools.system_tests.validate_jeeves"

    def test_validate_jeeves(self, mocker: MockerFixture) -> None:
        """test_validate_jeeves."""
        mock_discord_notification = mocker.patch(f"{self.script_path}.discord_notification", return_value=None)
        mocker.patch(f"{self.script_path}.systemd_tests", return_value=None)
        mocker.patch(f"{self.script_path}.zpool_tests", return_value=None)

        validate_jeeves.main()

        assert mock_discord_notification.call_count == 0

    def test_validate_jeeves_errors(self, mocker: MockerFixture) -> None:
        """test_validate_jeeves_errors."""
        mock_discord_notification = mocker.patch(f"{self.script_path}.discord_notification", return_value=None)
        mocker.patch(f"{self.script_path}.systemd_tests", return_value=["systemd_tests error"])
        mocker.patch(f"{self.script_path}.zpool_tests", return_value=["zpool_tests error"])

        with pytest.raises(SystemExit) as exception_info:
            validate_jeeves.main()

        assert exception_info.value.code == 1

        assert mock_discord_notification.call_count == 1

    def test_validate_jeeves_execution(self, mocker: MockerFixture) -> None:
        """test_validate_jeeves_execution."""
        mock_discord_notification = mocker.patch(f"{self.script_path}.discord_notification", return_value=None)
        mocker.patch(f"{self.script_path}.zpool_tests", side_effect=RuntimeError("zpool_tests error"))

        with pytest.raises(SystemExit) as exception_info:
            validate_jeeves.main()

        assert exception_info.value.code == 1

        assert mock_discord_notification.call_count == 1


class TestJeevesjr:
    """Jeevesjr."""

    script_path = "system_tools.system_tests.validate_jeevesjr"

    def test_validate_jeevesjr(self, mocker: MockerFixture) -> None:
        """test_validate_jeevesjr."""
        mock_discord_notification = mocker.patch(f"{self.script_path}.discord_notification", return_value=None)
        mocker.patch(f"{self.script_path}.systemd_tests", return_value=None)
        mocker.patch(f"{self.script_path}.zpool_tests", return_value=None)

        validate_jeevesjr.main()

        assert mock_discord_notification.call_count == 0

    def test_validate_jeevesjr_errors(self, mocker: MockerFixture) -> None:
        """test_validate_jeevesjr_errors."""
        mock_discord_notification = mocker.patch(f"{self.script_path}.discord_notification", return_value=None)
        mocker.patch(f"{self.script_path}.systemd_tests", return_value=["systemd_tests error"])
        mocker.patch(f"{self.script_path}.zpool_tests", return_value=["zpool_tests error"])

        with pytest.raises(SystemExit) as exception_info:
            validate_jeevesjr.main()

        assert exception_info.value.code == 1

        assert mock_discord_notification.call_count == 1

    def test_validate_jeevesjr_execution(self, mocker: MockerFixture) -> None:
        """test_validate_jeevesjr_execution."""
        mock_discord_notification = mocker.patch(f"{self.script_path}.discord_notification", return_value=None)
        mocker.patch(f"{self.script_path}.zpool_tests", side_effect=RuntimeError("zpool_tests error"))

        with pytest.raises(SystemExit) as exception_info:
            validate_jeevesjr.main()

        assert exception_info.value.code == 1

        assert mock_discord_notification.call_count == 1
