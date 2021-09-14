#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import os
import json

from selenium import webdriver  # type: ignore


class SeleniumScraper():
    def __init__(
            self,
            incognito=True,
            headless=True,
            close_driver_when_finished=True,
            log_verbose=False):

        DRIVER_PATH = os.path.join(
            os.path.dirname(__file__),
            "chrome_driver/chromedriver")

        options = webdriver.ChromeOptions()
        if incognito:
            options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
        if not close_driver_when_finished:
            options.add_experimental_option("detach", True)

        capabilities = options.to_capabilities()

        self.persisted_urls_path = os.path.join(
            os.path.dirname(__file__),
            "persisted_urls.json")
        self.extracted_urls = set()
        self.wd = webdriver.Chrome(
            executable_path=DRIVER_PATH,
            desired_capabilities=capabilities)
        self.log_verbose = log_verbose
        self.skipped_urls_count = 0
        self.load_previous_urls()

    def load_previous_urls(self):
        if os.path.isfile(self.persisted_urls_path):
            f = open(self.persisted_urls_path)
            prev_checks = json.load(f)
            for url in prev_checks['urls']:
                self.extracted_urls.add(url)
        else:
            if self.log_verbose:
                print("No previous urls found. Continuing...")

    def close_driver(self):
        try:
            self.wd.quit()
        except (Exception):
            pass

    def wipe_extracted_urls(self):
        self.extracted_urls = set()

    def store_previous_urls(self):
        formatted_json = {
            'urls': []
        }
        for url in self.extracted_urls:
            formatted_json['urls'].append(url)

        with open(self.persisted_urls_path, 'w') as f:
            json.dump(formatted_json, f)

    def cleanup(self):
        if self.log_verbose:
            print("Cleaning up driver...")
        self.close_driver()
        self.store_previous_urls()
