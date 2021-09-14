#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import os
import time
import math

from .scraper.ab_scraper import ABScraper
from .classifiers.detectron_classifier import DetectronClassifier
from .analysis_manager import AnalysisManager
from .image_downloader import ImageDownloader
from .pages_manager import PagesManager
from .thumbnail_manager import ThumbnailManager
from .session_manager import SessionManager

# Necessary for classification libraries to work correctly.
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class NeuralScraper():
    def __init__(
        self,
        priority_sorter,
        classification_filter=None,
        classification_bundles=None,
        classifier=DetectronClassifier(),
        close_driver_when_finished=True,
        headless_browsing=False,
        side_panel_max_depth=3,
        side_panel_max_siblings_to_check=4,
        root_checks_before_side_dive=4,
        log_verbose=False
    ):

        if ((classification_filter is None and classification_bundles is None)
                or (classification_filter is not None
                    and classification_bundles is not None)):
            raise Exception("Must either provide classification filter"
                            "or bundle, but not both!")

        self.vetted_image_urls = set()

        self.priority_sorter = priority_sorter

        self.side_panel_max_depth = side_panel_max_depth
        self.side_panel_max_siblings_to_check = \
            side_panel_max_siblings_to_check
        self.root_checks_before_side_dive = root_checks_before_side_dive

        self.abscraper = ABScraper(
            headless=headless_browsing,
            close_driver_when_finished=close_driver_when_finished,
            log_verbose=log_verbose)

        cur_dir_abspath = os.path.dirname(os.path.abspath(__file__))

        session_persist_path = os.path.join(
            cur_dir_abspath,
            "session_manager.json")
        self.session_manager = SessionManager(session_persist_path)

        temp_path = os.path.abspath(cur_dir_abspath + "/.temp")
        persist_out_path = os.path.abspath(cur_dir_abspath + "/results")

        self.classification_bundles = []
        if classification_bundles is None:
            self.classification_bundles.append({
                "filter": classification_filter,
                "downloader": ImageDownloader(
                    temp_out_path=temp_path,
                    persist_out_path=persist_out_path,
                    temp_out_name="temp.jpg")
            })

        else:
            for i in range(0, len(classification_bundles)):
                current_bundle = classification_bundles[i]
                current_class_filter = current_bundle.filter
                current_out_path = current_bundle.persist_out_path
                self.classification_bundles.append({
                    "filter": current_class_filter,
                    "name": current_bundle.name,
                    "downloader": ImageDownloader(
                        temp_out_path=temp_path,
                        persist_out_path=current_out_path,
                        temp_out_name="temp.jpg")
                })

        self.thumbnail_manager = None

        self.images_scraped = 0
        self.reanalysis_count = 0
        self.allowed_reanalysis_count = max

        pages_manager_path = os.path.join(cur_dir_abspath, "page_manager.json")
        self.pages_manager = PagesManager(pages_manager_path)

        analysis_persist_path = os.path.join(
            cur_dir_abspath,
            "analysis_manager.json")
        self.analysis_manager = AnalysisManager(
            analysis_persist_path,
            classifier,
            temp_img_path=temp_path,
            result_img_path=persist_out_path)

        self.log_verbose = log_verbose

        self.side_panel_depth = 0
        self.side_panel_siblings_checked = 0
        self.root_checks = 0

    def neural_scrape(
            self,
            search_term,
            images_to_scrape=10,
            batch_size=5,
            batch_nohit_tolerance=0.5,
            max_depth=5,
            site="",
            allowed_reanalysis_count=math.inf,
            close_browser_when_done=True):
        self.allowed_reanalysis_count = allowed_reanalysis_count
        self.abscraper.start_session(search_term, site=site)
        self.images_to_scrape = images_to_scrape
        cur_url = self.abscraper.get_current_page_url()
        self.pages_manager.initialize_page(cur_url)
        self.thumbnail_manager = ThumbnailManager(
            self.abscraper.get_page_thumbnails())

        self.scrape_from_current_page(batch_size, batch_nohit_tolerance)

        depth = 0
        while (depth < max_depth and
                self.images_scraped < self.images_to_scrape):
            self.manage_navigation_to_new_page(
                batch_size,
                batch_nohit_tolerance)
            depth += 1
            print("Current depth is ", depth)

        if self.images_to_scrape < self.images_scraped:
            print("Failed to scrape requested images, max depth reached.")

        print("Scraping Complete.")
        print(f"Found {self.images_scraped} of "
              f"{self.images_to_scrape} requested")

        self.pages_manager.persist_manager()
        self.analysis_manager.persist_analyses()
        self.session_manager.persist_manager()
        if close_browser_when_done:
            self.abscraper.cleanup()

    def scrape_from_current_page(self,
                                 batch_size,
                                 percent_wrong_tolerance):
        continue_scraping_page = True
        while (continue_scraping_page and
                self.images_scraped < self.images_to_scrape):
            good_thumbnails_added = self.evaluate_next_batch(batch_size)

            if self.log_verbose:
                print(
                    f"Evaluated {batch_size} thumbnails, "
                    "found {good_thumbnails_added} new images")

            if (float(good_thumbnails_added)/float(batch_size)
                    > percent_wrong_tolerance):
                if self.log_verbose:
                    print(
                        "Found enough successful images for for tolerance. "
                        "\nStaying on page.")
            else:
                continue_scraping_page = False
                if self.log_verbose:
                    print("Not successful on page, "
                          "continuing to next step in procedure")

        return

    def manage_navigation_to_new_page(
            self,
            batch_size,
            percent_wrong_tolerance):
        navigated_successfully = False

        current_page_analyses = \
            self.analysis_manager.get_current_page_analyses()

        sorted_analyses = \
            self.priority_sorter.sort_analyses(current_page_analyses)

        allowed_sort_image_selections = 10

        sorted_anal_attempts = []
        while (len(sorted_analyses) > 0
                and len(sorted_anal_attempts) < allowed_sort_image_selections):
            sorted_anal_attempts.append(sorted_analyses.pop(0))

        if self.log_verbose:
            print("Sorted Analysis attempts:", len(sorted_anal_attempts))
            for anal in sorted_anal_attempts:
                print("\nAnalyses:")
                for prediction in anal.predictions.values():
                    print(f"\t{prediction.name} - {prediction.score}")

        max_attempts = 10
        attempt = 0
        while attempt < max_attempts and (not navigated_successfully):
            if self.thumbnail_manager.good_thumbnails_left():
                if self.log_verbose:
                    print("Navigating to first good thumbnail...")
                try:
                    self.navigate_to_new_page(
                        self.thumbnail_manager.
                        get_next_good_thumbnail_location())
                    navigated_successfully = True
                    if self.log_verbose:
                        print("\n\nHit Navigation success\n\n")
                    self.scrape_from_current_page(
                        batch_size,
                        percent_wrong_tolerance)
                except Exception as e:
                    time.sleep(0.5)
                    if self.log_verbose:
                        print("Exception occurred in navigation, "
                              "selecting another thumbnail:", e)

            elif (self.thumbnail_manager.analyzed_thumbnails_left() and
                  len(sorted_anal_attempts) > 0 and
                  not self.thumbnail_manager.good_thumbnails_left()):

                if self.log_verbose:
                    print("Navigating to highest scored thumbnail...")
                try:
                    next_analyses = sorted_anal_attempts.pop(0)
                    if self.log_verbose:
                        print(f"Next analyses: {next_analyses.id} "
                              f"{len(next_analyses.predictions)}")
                        for prediction in next_analyses.predictions.values():
                            print(f"\t{prediction.name} -  {prediction.score}")
                    self.navigate_to_new_page(
                        self.thumbnail_manager.
                        get_thumbnail_location_with_analysis_id(
                            next_analyses.id))
                    navigated_successfully = True
                    print("\n\nPrioritized Navigation success\n\n")
                    self.scrape_from_current_page(
                        batch_size,
                        percent_wrong_tolerance)
                except Exception as e:
                    time.sleep(0.5)
                    print(
                        "Exception occurred in priority navigation, "
                        "selecting another thumbnail. "
                        "Set logging to verbose for more information.")
                    if self.log_verbose:
                        print(
                            "Exception occurred in priority navigation, "
                            "selecting another thumbnail. Message:", e)

            else:
                if self.log_verbose:
                    print("No good thumbnails to navigate to found, "
                          "selecting randomly")
                try:
                    time.sleep(0.5)
                    self.navigate_to_new_page(
                        self.thumbnail_manager.get_random_thumbnail_location())
                    navigated_successfully = True
                    print("\n\nRandom Navigation success\n\n")
                    self.scrape_from_current_page(
                        batch_size,
                        percent_wrong_tolerance)
                except Exception as e:
                    time.sleep(0.5)
                    print(
                        "Exception occurred in random navigation, "
                        "selecting another thumbnail. "
                        "Set logging to verbose for more information.")
                    if self.log_verbose:
                        print("Exception occurred in random navigation, "
                              "selecting another thumbnail. Message:", e)

    def evaluate_next_batch(self, batch_size):
        good_thumbnails_added = 0
        while (self.analysis_manager.get_new_page_analyses_count() < batch_size
               and self.thumbnail_manager.root_thumbnails_left()
               and self.images_scraped < self.images_to_scrape
               and self.reanalysis_count < self.allowed_reanalysis_count):

            url = self.try_get_url_from_current_thumbnail()

            if url:
                classification = \
                    self.analysis_manager.classify_img_from_url(url)
                self.analysis_manager.is_last_classification_repeat()

                if self.analysis_manager.is_last_classification_repeat():
                    self.reanalysis_count += 1
                    if self.log_verbose:
                        print(
                            f"Reanalysis {self.reanalysis_count} of "
                            f"{self.allowed_reanalysis_count}")
                else:
                    #
                    print(
                        f"\nAnalyzed "
                        f"{self.analysis_manager.get_new_page_analyses_count()}"  # noqa: E501
                        f" of {batch_size} for current batch")
                    self.reanalysis_count = 0

                if classification:
                    primary_is_good = self.handle_analysis(classification, url)

                else:
                    primary_is_good = False

                if primary_is_good:
                    self.pages_manager.uptick_current_page_good_count()
                    self.images_scraped += 1
                    good_thumbnails_added += 1
                    self.thumbnail_manager.current_thumbnail_good()
                    print("Found good image. "
                          f"Current good image count is {self.images_scraped}")

            self.set_next_thumbnail()
        return good_thumbnails_added

    def handle_analysis(self, classification, url):
        number_of_bundles = len(self.classification_bundles)
        if number_of_bundles > 1:
            for i in range(1, number_of_bundles):
                bundle = self.classification_bundles[i]
                filter = bundle["filter"]
                image_is_good = filter.evaluate(classification)
                if image_is_good:
                    downloader = bundle["downloader"]
                    path = downloader.persist_image(url)
                    bundle_name = bundle["name"]
                    self.session_manager.add_image(path, bundle_name)
                    self.session_manager.log_session()

        self.thumbnail_manager.attach_analysis_id_to_thumbnail(
            classification.id)
        primary_bundle = self.classification_bundles[0]
        primary_filter = primary_bundle["filter"]
        primary_is_good = primary_filter.evaluate(classification)
        if primary_is_good:
            primary_downloader = primary_bundle["downloader"]
            path = primary_downloader.persist_image(url)
            primary_name = primary_bundle["name"]
            self.session_manager.add_image(path, primary_name)
            self.session_manager.log_session()
            print(f"Saved primary image ({primary_name})")

        current_page_analyses = \
            self.analysis_manager.get_current_page_analyses()
        sorted_analyses = self.priority_sorter.sort_analyses(
            current_page_analyses)
        highest_anal = sorted_analyses.pop(0)

        if highest_anal.id == classification.id and self.log_verbose:
            print("Last image is the current target")
            print("id: ", classification.id)
            print(f"URL: \n\n{url}\n\n")
            for prediction in highest_anal.predictions.values():
                print(f"\t{prediction.name} -  {prediction.score}")
        return primary_is_good

    def set_next_thumbnail(self):
        if self.root_checks < (self.root_checks_before_side_dive):
            self.thumbnail_manager.try_get_next_root()
            self.root_checks += 1
        else:
            if self.root_checks < (self.root_checks_before_side_dive+1):
                current_page_analyses = \
                    self.analysis_manager.get_current_page_analyses()
                sorted_analyses = self.priority_sorter.sort_analyses(
                    current_page_analyses)
                if len(sorted_analyses) > 0:
                    analysis = sorted_analyses.pop(0)
                    if self.log_verbose:
                        print("Sorted analysis ids: ")
                        for anlss in sorted_analyses:
                            print(f"\t{anlss.id}")
                        print("Analysis id: ", analysis.id)
                    self.thumbnail_manager.\
                        try_set_current_location_by_analysis_id(analysis.id)
                self.root_checks += 1
            else:
                self.handle_side_dive()

    def handle_side_dive(self):
        if (self.side_panel_siblings_checked <
                self.side_panel_max_siblings_to_check and
                self.side_panel_depth > 0):
            self.thumbnail_manager.try_get_next_sibling()
            self.side_panel_siblings_checked += 1
        else:
            if self.side_panel_depth < self.side_panel_max_depth:
                if self.thumbnail_manager.has_parent():
                    sorted_analyses = self.try_get_sorted_sibling_analyses()
                    if sorted_analyses:
                        analysis = sorted_analyses.pop(0)
                        self.thumbnail_manager.\
                            try_set_current_location_by_analysis_id(
                                analysis.id)
                        if self.log_verbose:
                            print("Sorted analysis ids: ")
                            for anlss in sorted_analyses:
                                print(f"\t{anlss.id}")
                            print("Analysis id: ", analysis.id)
                    self.handle_get_first_child()
                else:
                    self.handle_get_first_child()
            else:
                self.side_panel_siblings_checked = 0
                self.side_panel_depth = 0
                self.root_checks = 0
                self.thumbnail_manager.try_get_next_root()

    def handle_get_first_child(self):
        if not self.thumbnail_manager.try_get_first_child_location():
            self.side_panel_siblings_checked = \
                self.side_panel_max_siblings_to_check
            self.side_panel_depth = self.side_panel_max_depth
        else:
            self.side_panel_siblings_checked = 0
            self.side_panel_depth += 1

    def try_get_sorted_root_analyses(self):
        analysis_ids = \
            self.thumbnail_manager.try_get_analyzed_parent_analysis_ids()
        if not analysis_ids:
            return False

        root_analyses = []
        for id in analysis_ids:
            analysis = self.analysis_manager.try_get_analysis_by_id(id)
            if analysis:
                root_analyses.append(analysis)

        if len(root_analyses) == 0:
            return False

        return self.priority_sorter.sort_analyses(root_analyses)

    def try_get_sorted_sibling_analyses(self):
        analysis_ids = \
            self.thumbnail_manager.try_get_analyzed_sibling_analysis_ids()
        if not analysis_ids:
            return False

        sibling_analyses = []
        for id in analysis_ids:
            analysis = self.analysis_manager.try_get_analysis_by_id(id)
            if analysis:
                sibling_analyses.append(analysis)

        if len(sibling_analyses) == 0:
            return False

        return self.priority_sorter.sort_analyses(sibling_analyses)

    def navigate_to_new_page(self, thumbnail_location):
        print("Navigating to thumbnail with side depth of ",
              len(thumbnail_location))
        self.abscraper.navigate_to_location_by_path(thumbnail_location)

        self.abscraper.click_see_more()

        self.side_panel_depth = 0
        self.side_panel_siblings_checked = 0
        self.root_checks = 0
        self.reanalysis_count = 0
        self.analysis_manager.reset_new_page_analyses()
        self.analysis_manager.reset_current_page_analyses()
        self.thumbnail_manager = ThumbnailManager(
            self.abscraper.get_page_thumbnails())
        return

    def try_get_url_from_current_thumbnail(self):
        if self.log_verbose:
            print("Resetting actual image urls.")

        self.current_urls = []
        self.pages_manager.uptick_current_thumbnails_checked_count()

        current_thumb_path = \
            self.thumbnail_manager.try_get_current_thumbnail_path()

        unchecked_urls = self.abscraper.get_img_urls_from_thumb_path(
            current_thumb_path,
            max_attempts=2,
            wait_between_attempts=3)

        if len(unchecked_urls) > 0:
            side_panel_thumbnails = self.abscraper.get_side_panel_thumbnails()
            self.thumbnail_manager.set_child_thumbs(side_panel_thumbnails)
            return unchecked_urls[0]
        else:
            return False
