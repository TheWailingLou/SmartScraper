#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import time

from .selenium_scraper import SeleniumScraper
from selenium.common.exceptions import StaleElementReferenceException  # type: ignore # noqa: E501


class ABScraper(SeleniumScraper):
    def __init__(self,
                 incognito=True,
                 headless=True,
                 close_driver_when_finished=True,
                 log_verbose=False,
                 urls_to_avoid=[
                     "dreamstime",
                     "123rf.com",
                     "people.desktopnexus"]):
        SeleniumScraper.__init__(
            self,
            incognito,
            headless,
            close_driver_when_finished,
            log_verbose)
        self.current_element = None
        self.urls_to_avoid = urls_to_avoid

    def start_session(self, search_term, safe_search=False, site=""):
        if safe_search:
            safe_search_str = "on"
        else:
            safe_search_str = "off"

        if site != "":
            search_term = search_term + " site:" + site

        google_search_url = \
            f"https://www.google.com/search?safe={safe_search_str}&site={site}&tbm=isch&source=hp&q={search_term}&oq={search_term}&gs_l=img"  # noqa: E501

        self.wd.get(google_search_url)

    def get_side_panel_thumbnails(self):
        side_panel_thumbnails = self.wd.find_elements_by_css_selector(
            "div.l7VXJc img.Q4LuWd")
        return side_panel_thumbnails

    def get_page_thumbnails(self):
        thumbnail_results = self.wd.find_elements_by_css_selector("img.Q4LuWd")
        return thumbnail_results

    def get_current_page_url(self):
        return self.wd.current_url

    def click_see_more(self):
        time.sleep(0.4)
        see_more = self.wd.find_elements_by_css_selector("a.So4Urb")
        if len(see_more) > 0:
            see_more[0].click()
        else:
            raise Exception("Could not click see more! Link not present.")

    def navigate_to_thumb(self, thumb_el):
        if self.current_element != thumb_el:
            thumb_el.click()
            self.current_element = thumb_el
            time.sleep(0.3)

    def navigate_to_location_by_path(
            self,
            thumbnail_location_path,
            sleep_between_navs=1):
        if len(thumbnail_location_path) == 0:
            raise Exception("Cannot navigate to path with 0 elements!")

        while len(thumbnail_location_path) > 0:
            next_location = thumbnail_location_path.pop(0)
            try:
                time.sleep(sleep_between_navs)
                self.navigate_to_thumb(next_location.element)
            except StaleElementReferenceException as staleElementException:
                if self.log_verbose:
                    print("Stale element reference thrown: "
                          f"{staleElementException} \n Continuing.")
                time.sleep(sleep_between_navs)
                side_panel_thumbnails = self.get_side_panel_thumbnails()
                index_of_thumb = next_location.index
                try:
                    self.navigate_to_thumb(
                        side_panel_thumbnails[index_of_thumb])
                except Exception as e:
                    if self.log_verbose:
                        print(
                            f"Index: {next_location.index}, "
                            f"side thumbs: {len(side_panel_thumbnails)}")
                        raise Exception("Error caught, logged and rethrowing",
                                        type(e),
                                        e)
                    raise Exception("Error caught. Turn on verbose logging "
                                    "for more information", e)

    def get_img_urls_from_thumb_path(
            self,
            thumb_path,
            max_attempts=3,
            wait_between_attempts=0.5):
        unchecked_urls = []
        attempts = 0

        while len(unchecked_urls) == 0 and attempts < max_attempts:
            if self.log_verbose:
                print(f"Fetching urls. Attempt {attempts+1}")
            try:
                self.navigate_to_location_by_path(thumb_path)

                time.sleep(wait_between_attempts)

                actual_images = self.wd.find_elements_by_css_selector(
                    'img.n3VNCb')

                for actual_image in actual_images:
                    is_url_extractable = (
                        actual_image.get_attribute('src') and
                        'http' in actual_image.get_attribute('src'))
                    if is_url_extractable:
                        url = actual_image.get_attribute('src')
                        unchecked_urls.append(url)

                attempts += 1
            except Exception as e:
                attempts = max_attempts + 1

                if self.log_verbose:
                    print("Error caught extracting images. "
                          "Continuing extraction. Message: ", type(e), e)
                    print("thumbnail element:", thumb_path)
                    print(f"At attempt {attempts} of {max_attempts}")
                else:
                    print("Error caught. Continuing extraction. "
                          "Set logging to verbose for more information")

        thumbnail_filtered_urls = []
        for url in unchecked_urls:
            if url.find("https://encrypted-tbn0.gstatic.com") == -1:
                thumbnail_filtered_urls.append(url)

        filtered_urls = []
        for url in thumbnail_filtered_urls:
            add_url = True
            for avoid_url in self.urls_to_avoid:
                if url.find(avoid_url) != -1:
                    add_url = False

            if add_url:
                filtered_urls.append(url)

        if self.log_verbose:
            print(f"Finished. Got {len(filtered_urls)} unchecked urls")
            for url in filtered_urls:
                print("\t", url)

        return filtered_urls
