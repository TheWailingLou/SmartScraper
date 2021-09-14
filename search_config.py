#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import math


class SearchConfig():
    def __init__(
            self,
            search_term,
            images_to_scrape,
            batch_size=5,
            max_depth=5,
            site="",
            allowed_reanalysis_count=math.inf,
            close_browser_when_done=True,
            headless_browsing=False,
            side_panel_max_depth=3,
            side_panel_max_siblings_to_check=4,
            root_checks_before_side_dive=4):
        self.search_term = search_term
        self.images_to_scrape = images_to_scrape
        self.batch_size = batch_size
        self.max_depth = max_depth
        self.site = site
        self.allowed_reanalysis_count = allowed_reanalysis_count
        self.close_browser_when_done = close_browser_when_done
        self.headless_browsing = headless_browsing
        self.side_panel_max_depth = side_panel_max_depth
        self.side_panel_max_siblings_to_check = \
            side_panel_max_siblings_to_check
        self.root_checks_before_side_dive = root_checks_before_side_dive
