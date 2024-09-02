"""dataset."""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from system_tools.common import bash_wrapper


class Snapshot:
    """Snapshot."""

    def __init__(self, data: str, options: Sequence[str]) -> None:
        """__init__."""
        snapshot_data = {option: data.split("\t")[index] for index, option in enumerate(options)}

        self.createtxg = int(snapshot_data["createtxg"])
        self.creation = datetime.fromtimestamp(int(snapshot_data["creation"]), tz=UTC)
        self.defer_destroy = snapshot_data["defer_destroy"]
        self.guid = int(snapshot_data["guid"])
        self.name = snapshot_data["name"]
        self.objsetid = int(snapshot_data["objsetid"])
        self.ratio = snapshot_data["ratio"]
        self.refer = int(snapshot_data["refer"])
        self.used = int(snapshot_data["used"])
        self.userrefs = int(snapshot_data["userrefs"])
        self.version = int(snapshot_data["version"])
        self.written = int(snapshot_data["written"])

    def __repr__(self) -> str:
        """__repr__."""
        return f"name={self.name} used={self.used} refer={self.refer}"


class Dataset:
    """Dataset."""

    def __init__(self, name: str) -> None:
        """__init__."""
        options = (
            "aclinherit",
            "aclmode",
            "acltype",
            "available",
            "canmount",
            "checksum",
            "clones",
            "compression",
            "copies",
            "createtxg",
            "creation",
            "dedup",
            "devices",
            "encryption",
            "exec",
            "filesystem_limit",
            "guid",
            "keystatus",
            "logbias",
            "mlslabel",
            "mounted",
            "mountpoint",
            "name",
            "quota",
            "readonly",
            "recordsize",
            "redundant_metadata",
            "referenced",
            "refquota",
            "refreservation",
            "reservation",
            "setuid",
            "sharenfs",
            "snapdir",
            "snapshot_limit",
            "sync",
            "used",
            "usedbychildren",
            "usedbydataset",
            "usedbysnapshots",
            "version",
            "volmode",
            "volsize",
            "vscan",
            "written",
            "xattr",
        )

        raw_dataset_data, _ = bash_wrapper(f"zfs list {name} -pH -o {','.join(options)}")

        dataset_data = {option: raw_dataset_data.strip().split("\t")[index] for index, option in enumerate(options)}

        self.aclinherit = dataset_data["aclinherit"]
        self.aclmode = dataset_data["aclmode"]
        self.acltype = dataset_data["acltype"]
        self.available = int(dataset_data["available"])
        self.canmount = dataset_data["canmount"]
        self.checksum = dataset_data["checksum"]
        self.clones = dataset_data["clones"]
        self.compression = dataset_data["compression"]
        self.copies = int(dataset_data["copies"])
        self.createtxg = int(dataset_data["createtxg"])
        self.creation = datetime.fromtimestamp(int(dataset_data["creation"]), tz=UTC)
        self.dedup = dataset_data["dedup"]
        self.devices = dataset_data["devices"]
        self.encryption = dataset_data["encryption"]
        self.exec = dataset_data["exec"]
        self.filesystem_limit = dataset_data["filesystem_limit"]
        self.guid = int(dataset_data["guid"])
        self.keystatus = dataset_data["keystatus"]
        self.logbias = dataset_data["logbias"]
        self.mlslabel = dataset_data["mlslabel"]
        self.mounted = dataset_data["mounted"]
        self.mountpoint = dataset_data["mountpoint"]
        self.name = dataset_data["name"]
        self.quota = int(dataset_data["quota"])
        self.readonly = dataset_data["readonly"]
        self.recordsize = int(dataset_data["recordsize"])
        self.redundant_metadata = dataset_data["redundant_metadata"]
        self.referenced = int(dataset_data["referenced"])
        self.refquota = int(dataset_data["refquota"])
        self.refreservation = int(dataset_data["refreservation"])
        self.reservation = int(dataset_data["reservation"])
        self.setuid = dataset_data["setuid"]
        self.sharenfs = dataset_data["sharenfs"]
        self.snapdir = dataset_data["snapdir"]
        self.snapshot_limit = dataset_data["snapshot_limit"]
        self.sync = dataset_data["sync"]
        self.used = int(dataset_data["used"])
        self.usedbychildren = int(dataset_data["usedbychildren"])
        self.usedbydataset = int(dataset_data["usedbydataset"])
        self.usedbysnapshots = int(dataset_data["usedbysnapshots"])
        self.version = int(dataset_data["version"])
        self.volmode = dataset_data["volmode"]
        self.volsize = dataset_data["volsize"]
        self.vscan = dataset_data["vscan"]
        self.written = int(dataset_data["written"])
        self.xattr = dataset_data["xattr"]

    def get_snapshots(self) -> list[Snapshot] | None:
        """Get all snapshots from zfs and process then is test dicts of sets."""
        options = (
            "createtxg",
            "creation",
            "defer_destroy",
            "guid",
            "name",
            "objsetid",
            "ratio",
            "refer",
            "used",
            "userrefs",
            "version",
            "written",
        )

        raw_snapshots, _ = bash_wrapper(f"zfs list -t snapshot -pH -o {','.join(options)}")

        if raw_snapshots == "":
            return None

        return [Snapshot(raw_snapshot, options) for raw_snapshot in raw_snapshots.strip().split("\n")]

    def create_snapshot(self, snapshot_name: str) -> str:
        """Creates a zfs snapshot.

        Args:
            dataset_name (str): a dataset name
            snapshot_name (str): a snapshot name
        """
        logging.debug(f"Creating {self.name}@{snapshot_name}")
        _, return_code = bash_wrapper(f"zfs snapshot {self.name}@{snapshot_name}")
        if return_code == 0:
            return "snapshot created"

        if snapshots := self.get_snapshots():
            snapshot_names = {snapshot.name for snapshot in snapshots}
            if snapshot_name in snapshot_names:
                return f"Snapshot {snapshot_name} already exists for {self.name}"

        return f"Failed to create snapshot {snapshot_name} for {self.name}"

    def delete_snapshot(self, snapshot_name: str) -> None:
        """Deletes a zfs snapshot.

        Args:
            dataset_name (str): a dataset name
            snapshot_name (str): a snapshot name
        """
        logging.debug(f"deleting {self.name}@{snapshot_name}")
        bash_wrapper(f"zfs destroy {self.name}@{snapshot_name}")

    def __repr__(self) -> str:
        """__repr__."""
        return (
            f"{self.aclinherit=}\n"
            f"{self.aclmode=}\n"
            f"{self.acltype=}\n"
            f"{self.available=}\n"
            f"{self.canmount=}\n"
            f"{self.checksum=}\n"
            f"{self.clones=}\n"
            f"{self.compression=}\n"
            f"{self.copies=}\n"
            f"{self.createtxg=}\n"
            f"{self.creation=}\n"
            f"{self.dedup=}\n"
            f"{self.devices=}\n"
            f"{self.encryption=}\n"
            f"{self.exec=}\n"
            f"{self.filesystem_limit=}\n"
            f"{self.guid=}\n"
            f"{self.keystatus=}\n"
            f"{self.logbias=}\n"
            f"{self.mlslabel=}\n"
            f"{self.mounted=}\n"
            f"{self.mountpoint=}\n"
            f"{self.name=}\n"
            f"{self.quota=}\n"
            f"{self.readonly=}\n"
            f"{self.recordsize=}\n"
            f"{self.redundant_metadata=}\n"
            f"{self.referenced=}\n"
            f"{self.refquota=}\n"
            f"{self.refreservation=}\n"
            f"{self.reservation=}\n"
            f"{self.setuid=}\n"
            f"{self.sharenfs=}\n"
            f"{self.snapdir=}\n"
            f"{self.snapshot_limit=}\n"
            f"{self.sync=}\n"
            f"{self.used=}\n"
            f"{self.usedbychildren=}\n"
            f"{self.usedbydataset=}\n"
            f"{self.usedbysnapshots=}\n"
            f"{self.version=}\n"
            f"{self.volmode=}\n"
            f"{self.volsize=}\n"
            f"{self.vscan=}\n"
            f"{self.written=}\n"
            f"{self.xattr=}\n"
        )
