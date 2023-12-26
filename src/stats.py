#!/usr/bin/env python
""" manages a dictionary of system stats """
import os
import time
import psutil
from dateutil.relativedelta import relativedelta


class Stats:
    """manages a dictionary of system stats"""

    def __init__(self):
        self.stats = {}
        self.refresh_stats()

    def refresh_stats(self):
        """fetch the system stats"""
        self.stats = {}
        self.stats["hostname"] = os.uname()[1]
        self.stats["uptime"] = {}
        self.stats["uptime"]["epoch"] = self._get_uptime_epoch()
        self.stats["uptime"]["datetime"] = self._get_uptime_human_readable()
        self.stats["system"] = {}
        self.stats["system"]["cpu"] = {}
        self.stats["system"]["cpu"]["load"] = {}
        self.stats["system"]["cpu"]["load"]["1m"] = 0.8
        self.stats["system"]["cpu"]["load"]["5m"] = 2.3
        self.stats["system"]["cpu"]["load"]["15m"] = 4.7
        self.stats["system"]["cpu"]["speed"] = "900mhz"
        self.stats["system"]["cpu"]["arc"] = "amd64"
        self.stats["system"]["type"] = "BSD"

    def get_stats(self):
        """return the stats dictionary"""
        self.refresh_stats()
        return self.stats

    def _get_uptime_epoch(self):
        """_get_uptime_epoch"""
        return int(time.time()) - int(psutil.Process(os.getpid()).create_time())

    def _get_uptime_human_readable(self):
        """_get_uptime_human_readable"""
        fmt = "{0.days} days {0.hours} hours {0.minutes} minutes {0.seconds} seconds"
        return fmt.format(relativedelta(self._get_uptime_epoch()))
