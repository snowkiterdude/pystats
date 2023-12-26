#!/usr/bin/env python3
""" outputs system stats html """

from jinja2 import Template
from src.stats import Stats


class StatsHtml(Stats):
    """outputs system stats html"""

    def __init__(self):
        Stats.__init__(self)

    def get_html(self):
        """return the html for the home page"""
        self.refresh_stats()
        with open("src/home.html.j2", encoding="utf-8") as file:
            template = Template(file.read())
        return template.render(self.stats)
