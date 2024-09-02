"""test."""

from system_tools.common import bash_wrapper


class Zpool:
    """Zpool."""

    def __init__(
        self,
        name: str,
    ) -> None:
        """__init__."""
        options = (
            "allocated",
            "altroot",
            "ashift",
            "autoexpand",
            "autoreplace",
            "autotrim",
            "capacity",
            "comment",
            "dedupratio",
            "delegation",
            "expandsize",
            "failmode",
            "fragmentation",
            "free",
            "freeing",
            "guid",
            "health",
            "leaked",
            "readonly",
            "size",
        )

        raw_pool_data, _ = bash_wrapper(f"zpool list {name} -pH -o {','.join(options)}")

        pool_data = {option: raw_pool_data.strip().split("\t")[index] for index, option in enumerate(options)}

        self.name = name

        self.allocated = int(pool_data["allocated"])
        self.altroot = pool_data["altroot"]
        self.ashift = int(pool_data["ashift"])
        self.autoexpand = pool_data["autoexpand"]
        self.autoreplace = pool_data["autoreplace"]
        self.autotrim = pool_data["autotrim"]
        self.capacity = int(pool_data["capacity"])
        self.comment = pool_data["comment"]
        self.dedupratio = pool_data["dedupratio"]
        self.delegation = pool_data["delegation"]
        self.expandsize = pool_data["expandsize"]
        self.failmode = pool_data["failmode"]
        self.fragmentation = int(pool_data["fragmentation"])
        self.free = pool_data["free"]
        self.freeing = int(pool_data["freeing"])
        self.guid = int(pool_data["guid"])
        self.health = pool_data["health"]
        self.leaked = int(pool_data["leaked"])
        self.readonly = pool_data["readonly"]
        self.size = int(pool_data["size"])

    def __repr__(self) -> str:
        """__repr__."""
        return (
            f"{self.name=}\n"
            f"{self.allocated=}\n"
            f"{self.altroot=}\n"
            f"{self.ashift=}\n"
            f"{self.autoexpand=}\n"
            f"{self.autoreplace=}\n"
            f"{self.autotrim=}\n"
            f"{self.capacity=}\n"
            f"{self.comment=}\n"
            f"{self.dedupratio=}\n"
            f"{self.delegation=}\n"
            f"{self.expandsize=}\n"
            f"{self.failmode=}\n"
            f"{self.fragmentation=}\n"
            f"{self.freeing=}\n"
            f"{self.guid=}\n"
            f"{self.health=}\n"
            f"{self.leaked=}\n"
            f"{self.readonly=}\n"
            f"{self.size=}"
        )
