import logging

from pyudev import Context, Monitor, MonitorObserver
from pyudev.device._device import Device

from system_tools.common import configure_logger


# Monitor UDEV for drive insertion / removal
def disk_monitor_thread():
    context = Context()
    monitor = Monitor.from_netlink(context)
    monitor.filter_by("block")

    def print_device_event(action: str, device: Device) -> None:
        """print_device_event."""
        logging.info(f"{action=}")
        for key, value in device.items():
            logging.info(f"{key} = {value}")
        logging.info(f"{device.get('ID_FS_UUID')=}")

    logging.info("Starting Disk Monitor...")
    observer = MonitorObserver(monitor, print_device_event, name="monitor-observer")
    logging.info("Disk Monitor Started")
    observer.daemon = False
    observer.start()


configure_logger(level="DEBUG")
disk_monitor_thread()
