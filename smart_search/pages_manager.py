#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import uuid
import json
import os


class PagesManager():
    """Pages Manager."""

    def __init__(self, persist_path):
        """Init."""
        self.pages = {}
        self.persist_path = persist_path
        self.current_page_id = None
        self.load_manager()

    def get_all_pages(self):
        return self.pages

    def get_current_page(self):
        if self.current_page_id is None:
            raise Exception("No page initialized yet!")
        else:
            return self.pages[self.current_page_id]

    def initialize_page(self, url):
        existing_page = self.try_get_page_from_url(url)
        if existing_page is None:
            page = Page(url, 0, 0)
            self.pages[page.id] = page
            self.current_page_id = page.id
            return existing_page
        else:
            self.current_page_id = existing_page.id
            return existing_page

    def uptick_current_page_good_count(self):
        self.pages[self.current_page_id].good_thumbnail_count += 1

    def uptick_current_thumbnails_checked_count(self):
        self.pages[self.current_page_id].thumbnails_checked += 1

    def try_get_page_from_url(self, url):
        found_page = None
        for page in self.pages.values():
            if page.url == url:
                if found_page is not None:
                    raise Exception("Multiple pages found with same url!")
                else:
                    found_page = page
        return found_page

    def persist_manager(self):
        formatted_json = {}
        for page in self.pages.values():
            formatted_json[page.id] = {
                "id": page.id,
                "url": page.url,
                "good_thumbnail_count": page.good_thumbnail_count,
                "thumbnails_checked": page.thumbnails_checked
            }
        with open(self.persist_path, 'w') as f:
            json.dump(formatted_json, f)

    def load_manager(self):
        if os.path.isfile(self.persist_path):
            f = open(self.persist_path)
            json_unformatted = json.load(f)
            for page in json_unformatted.values():
                self.pages[page["id"]] = Page(
                    page["url"],
                    page["good_thumbnail_count"],
                    page["thumbnails_checked"],
                    page["id"])

        else:
            print("No page manager data found. Initializing.")


class Page():
    def __init__(
            self,
            page_url,
            good_thumbnail_count,
            thumbnails_checked,
            page_id=None):
        if page_id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = page_id
        self.url = page_url
        self.good_thumbnail_count = good_thumbnail_count
        self.thumbnails_checked = thumbnails_checked
