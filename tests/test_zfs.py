"""Test zfs."""

import json
from datetime import UTC, datetime
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from system_tools.zfs.dataset import Dataset, Snapshot, _zfs_list, get_datasets

SAMPLE_SNAPSHOT_DATA = {
    "createtxg": "123",
    "properties": {
        "creation": {"value": "1620000000"},
        "defer_destroy": {"value": "off"},
        "guid": {"value": "456"},
        "objsetid": {"value": "789"},
        "referenced": {"value": "1024"},
        "used": {"value": "512"},
        "userrefs": {"value": "0"},
        "version": {"value": "1"},
        "written": {"value": "2048"},
    },
    "name": "pool/dataset@snap1",
}

SAMPLE_DATASET_DATA = {
    "output_version": {"vers_major": 0, "vers_minor": 1, "command": "zfs list"},
    "datasets": {
        "pool/dataset": {
            "properties": {
                "aclinherit": {"value": "restricted"},
                "aclmode": {"value": "discard"},
                "acltype": {"value": "off"},
                "available": {"value": "1000000"},
                "canmount": {"value": "on"},
                "checksum": {"value": "on"},
                "clones": {"value": ""},
                "compression": {"value": "lz4"},
                "copies": {"value": "1"},
                "createtxg": {"value": "1234"},
                "creation": {"value": "1620000000"},
                "dedup": {"value": "off"},
                "devices": {"value": "on"},
                "encryption": {"value": "off"},
                "exec": {"value": "on"},
                "filesystem_limit": {"value": "none"},
                "guid": {"value": "5678"},
                "keystatus": {"value": "none"},
                "logbias": {"value": "latency"},
                "mlslabel": {"value": "none"},
                "mounted": {"value": "yes"},
                "mountpoint": {"value": "/pool/dataset"},
                "quota": {"value": "0"},
                "readonly": {"value": "off"},
                "recordsize": {"value": "131072"},
                "redundant_metadata": {"value": "all"},
                "referenced": {"value": "512000"},
                "refquota": {"value": "0"},
                "refreservation": {"value": "0"},
                "reservation": {"value": "0"},
                "setuid": {"value": "on"},
                "sharenfs": {"value": "off"},
                "snapdir": {"value": "hidden"},
                "snapshot_limit": {"value": "none"},
                "sync": {"value": "standard"},
                "used": {"value": "1024000"},
                "usedbychildren": {"value": "512000"},
                "usedbydataset": {"value": "256000"},
                "usedbysnapshots": {"value": "256000"},
                "version": {"value": "5"},
                "volmode": {"value": "default"},
                "volsize": {"value": "none"},
                "vscan": {"value": "off"},
                "written": {"value": "4096"},
                "xattr": {"value": "on"},
            }
        }
    },
}


def test_dataset_initialization(mocker: MockerFixture) -> None:
    """Test Dataset class initialization with mocked ZFS data."""
    mock_zfs_list = mocker.patch("system_tools.zfs.dataset._zfs_list")
    mock_zfs_list.return_value = SAMPLE_DATASET_DATA

    dataset = Dataset("pool/dataset")

    assert dataset.__dict__ == {
        "aclinherit": "restricted",
        "aclmode": "discard",
        "acltype": "off",
        "available": 1000000,
        "canmount": "on",
        "checksum": "on",
        "clones": "",
        "compression": "lz4",
        "copies": 1,
        "createtxg": 1234,
        "creation": datetime(2021, 5, 3, 0, 0, tzinfo=UTC),
        "dedup": "off",
        "devices": "on",
        "encryption": "off",
        "exec": "on",
        "filesystem_limit": "none",
        "guid": 5678,
        "keystatus": "none",
        "logbias": "latency",
        "mlslabel": "none",
        "mounted": "yes",
        "mountpoint": "/pool/dataset",
        "name": "pool/dataset",
        "quota": 0,
        "readonly": "off",
        "recordsize": 131072,
        "redundant_metadata": "all",
        "referenced": 512000,
        "refquota": 0,
        "refreservation": 0,
        "reservation": 0,
        "setuid": "on",
        "sharenfs": "off",
        "snapdir": "hidden",
        "snapshot_limit": "none",
        "sync": "standard",
        "used": 1024000,
        "usedbychildren": 512000,
        "usedbydataset": 256000,
        "usedbysnapshots": 256000,
        "version": 5,
        "volmode": "default",
        "volsize": "none",
        "vscan": "off",
        "written": 4096,
        "xattr": "on",
    }


def test_snapshot_initialization() -> None:
    """Test Snapshot class initialization with mocked ZFS data."""
    snapshot = Snapshot(SAMPLE_SNAPSHOT_DATA)
    assert snapshot.__dict__ == {
        "createtxg": 123,
        "creation": datetime(2021, 5, 3, 0, 0, tzinfo=UTC),
        "defer_destroy": "off",
        "guid": 456,
        "name": "snap1",
        "objsetid": 789,
        "referenced": 1024,
        "used": 512,
        "userrefs": 0,
        "version": 1,
        "written": 2048,
    }


def test_zfs_list_version_check(mocker: MockerFixture) -> None:
    """Test version validation in _zfs_list."""
    mock_bash = mocker.patch("system_tools.zfs.dataset.bash_wrapper")
    mock_bash.return_value = (
        json.dumps({"output_version": {"vers_major": 1, "vers_minor": 0, "command": "zfs list"}}),
        0,
    )

    with pytest.raises(RuntimeError) as excinfo:
        _zfs_list("zfs list invalid -pHj -o all")

    assert "Datasets are not in the correct format" in str(excinfo.value)


def test_get_datasets(mocker: MockerFixture) -> None:
    """Test get_datasets."""
    mock_bash = mocker.patch("system_tools.zfs.dataset.bash_wrapper")
    mock_bash.return_value = ("pool/dataset\npool/other\ninvalid", 0)
    mock_dataset = mocker.patch("system_tools.zfs.dataset.Dataset")

    get_datasets()

    mock_bash.assert_called_once_with("zfs list -Hp -t filesystem -o name")

    calls = [call("pool/dataset"), call("pool/other")]

    mock_dataset.assert_has_calls(calls)
