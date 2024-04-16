""" manages a dictionary of system stats """
import os
import time
import platform
import psutil
from dateutil.relativedelta import relativedelta


from .logger import get_logger


class Stats:
    """manages a dictionary of system stats"""

    def __init__(self):
        self.stats = {}
        self.log = get_logger()

    def _refresh_stats(self, fast=False):
        """fetch the system stats"""
        self.stats = {}
        self.stats["uptime"] = {}
        self.stats["cpu"] = {}
        self.stats["mem"] = {}
        self.stats["info"] = {}
        if fast:
            self.stats["info"]["hostname"] = os.uname()[1]
            self.stats["uptime"]["process_seconds"] = self._get_proc_uptime_sec()
            self.stats["uptime"]["process_uptime"] = self._get_uptime_human_readable(
                self.stats["uptime"]["process_seconds"]
            )
            self.stats["uptime"]["system_seconds"] = self._get_sys_uptime_sec()
            self.stats["uptime"]["system_uptime"] = self._get_uptime_human_readable(
                self.stats["uptime"]["system_seconds"]
            )
        else:
            self.stats["uptime"]["process_seconds"] = self._get_proc_uptime_sec()
            self.stats["uptime"]["process_uptime"] = self._get_uptime_human_readable(
                self.stats["uptime"]["process_seconds"]
            )
            self.stats["uptime"]["system_seconds"] = self._get_sys_uptime_sec()
            self.stats["uptime"]["system_uptime"] = self._get_uptime_human_readable(
                self.stats["uptime"]["system_seconds"]
            )

            self.stats["cpu"]["load_1m"] = psutil.getloadavg()[0]
            self.stats["cpu"]["load_5m"] = psutil.getloadavg()[1]
            self.stats["cpu"]["load_15m"] = psutil.getloadavg()[2]
            self.stats["cpu"]["cpu_count_logical"] = psutil.cpu_count(logical=True)
            self.stats["cpu"]["cpu_count"] = psutil.cpu_count(logical=False)
            self.stats["cpu"]["cpu_times"] = str(psutil.cpu_times())
            self.stats["cpu"]["cpu_times_percent"] = str(psutil.cpu_times_percent())
            self.stats["cpu"]["cpu_percent"] = psutil.cpu_percent(interval=1)
            self.stats["cpu"]["cpu_percent_percpu"] = psutil.cpu_percent(
                interval=1, percpu=True
            )
            self.stats["cpu"]["cpu_stats"] = str(psutil.cpu_stats())

            self.stats["mem"]["virtual_memory"] = str(psutil.virtual_memory())
            self.stats["mem"]["swap_memory"] = str(psutil.swap_memory())
            self.stats["mem"]["mem_total_MiB"] = int(
                psutil.virtual_memory()[0] / (1024 * 1024)
            )
            self.stats["mem"]["mem_used_MiB"] = int(
                psutil.virtual_memory()[3] / (1024 * 1024)
            )
            self.stats["mem"]["mem_free_MiB"] = int(
                psutil.virtual_memory()[4] / (1024 * 1024)
            )
            self.stats["mem"]["mem_swap_total_MiB"] = int(
                psutil.virtual_memory()[0] / (1024 * 1024)
            )
            self.stats["mem"]["mem_swap_used_MiB"] = int(
                psutil.virtual_memory()[1] / (1024 * 1024)
            )
            self.stats["mem"]["mem_swap_free_MiB"] = int(
                psutil.virtual_memory()[2] / (1024 * 1024)
            )

            self.stats["info"]["hostname"] = os.uname()[1]
            self.stats["info"]["architecture"] = str(self._get_platform_var(
                platform.architecture
            ))
            self.stats["info"]["machine"] = self._get_platform_var(platform.machine)
            self.stats["info"]["node"] = self._get_platform_var(platform.node)
            self.stats["info"]["platform"] = self._get_platform_var(platform.platform)
            self.stats["info"]["processor"] = self._get_platform_var(platform.processor)
            self.stats["info"]["python_build"] = str(self._get_platform_var(
                platform.python_build
            ))
            self.stats["info"]["python_compiler"] = self._get_platform_var(
                platform.python_compiler
            )
            self.stats["info"]["python_branch"] = self._get_platform_var(
                platform.python_branch
            )
            self.stats["info"]["python_implementation"] = self._get_platform_var(
                platform.python_implementation
            )
            self.stats["info"]["python_revision"] = self._get_platform_var(
                platform.python_revision
            )
            self.stats["info"]["python_version"] = self._get_platform_var(
                platform.python_version
            )
            self.stats["info"]["release"] = self._get_platform_var(platform.release)
            self.stats["info"]["system"] = self._get_platform_var(platform.system)
            self.stats["info"]["version"] = self._get_platform_var(platform.version)
            self.stats["info"]["uname"] = str(self._get_platform_var(platform.uname))
            self.stats["info"]["freedesktop_os_release"] = self._get_platform_var(
                platform.freedesktop_os_release
            )
            self.stats["info"]["system_alias"] = self._get_platform_system_alias()

    def get_stats(self, fast=False):
        """return the stats dictionary"""
        self._refresh_stats(fast)
        return self.stats

    def _get_platform_var(self, func):
        """Some platforms might not have all the platform attributes"""
        try:
            var = func()
        except FileNotFoundError:
            var = None
        return var if var else None

    def _get_platform_system_alias(self):
        """fetch the system alias"""
        try:
            var = platform.system_alias(
                platform.system(), platform.release(), platform.version()
            )
        except FileNotFoundError:
            var = None
        return var if var else None

    def _get_proc_uptime_sec(self):
        return int(time.time()) - int(psutil.Process(os.getpid()).create_time())

    def _get_sys_uptime_sec(self):
        return int(time.time() - psutil.boot_time())

    def _get_uptime_human_readable(self, in_seconds):
        """Takes seconds and turns it into a human readable string"""
        fmt = "{0.days} days {0.hours} hours {0.minutes} minutes {0.seconds} seconds"
        return fmt.format(relativedelta(seconds=in_seconds))
