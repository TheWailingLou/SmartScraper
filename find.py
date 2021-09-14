#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
from smart_search.filters.priority_sorter import PrioritySorter
from smart_search.classifiers.detectron_classifier import DetectronClassifier
from smart_search.neural_scraper import NeuralScraper


def search(search_config, prioritization_rules, classification_bundles):

    priority_sorter = PrioritySorter(prioritization_rules)

    neural_scraper = NeuralScraper(
        priority_sorter,
        classification_bundles=classification_bundles,
        classifier=DetectronClassifier(),
        close_driver_when_finished=search_config.close_browser_when_done,
        headless_browsing=search_config.headless_browsing,
        side_panel_max_depth=search_config.side_panel_max_depth,
        side_panel_max_siblings_to_check=search_config
        .side_panel_max_siblings_to_check,
        root_checks_before_side_dive=search_config
        .root_checks_before_side_dive)
    neural_scraper.neural_scrape(
        search_config.search_term,
        images_to_scrape=search_config.images_to_scrape,
        batch_size=search_config.batch_size,
        max_depth=search_config.max_depth,
        site=search_config.site,
        allowed_reanalysis_count=search_config.allowed_reanalysis_count,
        close_browser_when_done=search_config.close_browser_when_done)
