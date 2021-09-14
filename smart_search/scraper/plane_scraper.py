#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import time

from .selenium_scraper import SeleniumScraper


# Plane scraper uses x,y (batch_size, depth)  to scrape. Very simple scraping.
class PlaneScraper(SeleniumScraper):
    def __init__(
            self,
            incognito=True,
            headless=True,
            log_verbose=False):
        SeleniumScraper.__init__(self, incognito, headless, log_verbose)

    def dive_scrape_img_urls(
            self,
            search_term,
            batch_size=10,
            safe_search=False,
            site="",
            max_depth=0):
        # if (max_depth > 0):
        #     batch_per_layer = int(batch_size/max_depth)
        # else:
        #     batch_per_layer = batch_size

        thumbnail_results = self.get_thumb_results(
            search_term,
            safe_search,
            site)

        thumbnail_index = 0

        new_urls = self.dive(
            thumbnail_results,
            thumbnail_index,
            batch_size,
            0,
            max_depth)

        for url in new_urls:
            self.extracted_urls.add(url)

        # skipped_urls_count comes from parent, and linter doesn't understand.
        print(f"Skipped {self.skipped_urls_count} total urls")  # pylint: disable=E0203 # noqa: 501
        self.skipped_urls_count = 0
        return new_urls

    def dive(
            self,
            thumbnail_results,
            thumbnail_index,
            batch_size,
            cur_depth,
            max_depth):

        number_thumbnails = len(thumbnail_results)

        new_urls = set()

        while (len(new_urls) < batch_size
                and thumbnail_index < number_thumbnails):
            thumb_el = thumbnail_results[thumbnail_index]
            actual_urls = self.extract_image_url_from_thumb(thumb_el)
            for actual_url in actual_urls:
                if actual_url not in self.extracted_urls:
                    new_urls.add(actual_url)
                else:
                    self.skipped_urls_count += 1

            thumbnail_index += 1

        if cur_depth < max_depth:
            see_more_clicked = False
            while not see_more_clicked:
                time.sleep(0.3)  # give element time to load
                see_more = self.wd.find_elements_by_css_selector("a.So4Urb")
                if len(see_more) > 0:
                    see_more[0].click()
                    see_more_clicked = True

                    new_thumbnail_results = \
                        self.wd.find_elements_by_css_selector("img.Q4LuWd")

                    urls_from_dive = self.dive(
                        new_thumbnail_results,
                        0,
                        batch_size,
                        cur_depth+1,
                        max_depth)
                    for dive_url in urls_from_dive:
                        new_urls.add(dive_url)

                else:
                    if thumbnail_index >= number_thumbnails:
                        reget_thumbnail_results = \
                            self.wd.find_elements_by_css_selector("img.Q4LuWd")
                        if(len(reget_thumbnail_results) > number_thumbnails):
                            thumbnail_results = reget_thumbnail_results
                            number_thumbnails = len(reget_thumbnail_results)
                        else:
                            print("Ran out of images... finishing.")
                            see_more_clicked = True
                    else:
                        thumb_el = thumbnail_results[thumbnail_index]
                        try:
                            thumb_el.click()
                        except Exception:
                            print("Next image could not be clicked, "
                                  "continuing..")

                        thumbnail_index += 1

        return new_urls

    def get_thumb_results(self, search_term, safe_search, site):
        if safe_search:
            safe_search_str = "on"
        else:
            safe_search_str = "off"

        google_search_url = f"https://www.google.com/search?safe={safe_search_str}&site={site}&tbm=isch&source=hp&q={search_term}&oq={search_term}&gs_l=img"  # noqa: E501

        self.wd.get(google_search_url)

        thumbnail_results = self.wd.find_elements_by_css_selector("img.Q4LuWd")
        return thumbnail_results

    def extract_image_url_from_thumb(self, thumb_img):
        try:
            thumb_img.click()
        except Exception as e:
            if self.log_verbose:
                print("Error caught extracting images. ",
                      "Continuing extraction. Message: ", e)
            else:
                print("Error caught. Continuing extraction. ",
                      "Set logging to verbose for more information")
        time.sleep(0.2)
        actual_images = self.wd.find_elements_by_css_selector('img.n3VNCb')

        actual_img_urls = set()

        for actual_image in actual_images:
            is_url_extractable = (
                actual_image.get_attribute('src') and
                'http' in actual_image.get_attribute('src'))
            if is_url_extractable:
                actual_img_urls.add(actual_image.get_attribute('src'))

        if self.log_verbose:
            # pylint: disable=no-member
            print("Image urls size: ", len(self.image_urls))

        return actual_img_urls
