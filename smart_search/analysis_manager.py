#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import json
import os

from .classifiers.prediction import Analysis
from .image_downloader import ImageDownloader


class AnalysisManager():
    def __init__(
            self,
            persist_path,
            classifier,
            temp_img_path,
            result_img_path):
        self.persist_path = persist_path
        self.analyses = {}
        self.load_analyses()
        self.new_page_analyses = []
        self.current_page_analyses = []
        self.skipped_reanalysis_count = 0

        self.was_last_classification_repeat = False

        self.image_downloader = ImageDownloader(
            temp_out_path=temp_img_path,
            persist_out_path=result_img_path,
            temp_out_name="temp.jpg")

        self.classifier = classifier

    def classify_img_from_url(self, url):
        self.was_last_classification_repeat = False
        persisted_result = self.try_get_analysis_by_url(url)
        if persisted_result:
            self.skipped_reanalysis_count += 1
            self.current_page_analyses.append(persisted_result)
            self.was_last_classification_repeat = True
            return persisted_result
        else:
            temp_img = self.image_downloader.persist_temp_img(url)

            if temp_img:
                print("Record for url did not exist. Analysing image...")
                classifier_results = self.classifier.classify(
                    temp_img,
                    origin_url=url,
                    display_results=False)
                self.add_analysis(classifier_results)
                self.current_page_analyses.append(classifier_results)
                return classifier_results

            else:
                return False

    def is_last_classification_repeat(self):
        return self.was_last_classification_repeat

    def try_get_analysis_by_id(self, id):
        if id not in self.analyses.keys():
            return False
        else:
            return self.analyses[id]

    def get_current_page_analyses(self):
        return self.current_page_analyses

    def reset_current_page_analyses(self):
        self.current_page_analyses = []

    def get_new_page_analyses(self):
        return self.new_page_analyses

    def reset_new_page_analyses(self):
        self.new_page_analyses = []

    def add_analysis(self, analysis):
        self.analyses[analysis.id] = analysis
        self.new_page_analyses.append(analysis)

    def get_new_page_analyses_count(self):
        return len(self.new_page_analyses)

    def try_get_analysis_by_url(self, url):
        result = None
        for analysis in self.analyses.values():
            if analysis.url == url:
                if result is None:
                    result = analysis

                else:
                    raise Exception(f"Tried to get analysis with url {url}, "
                                    "but multiple were found!",
                                    f"url: {url}",
                                    f"analyses: {self.analyses.values}")
        if result is None:
            return False
        else:
            return result

    def load_analyses(self):
        if os.path.isfile(self.persist_path):
            f = open(self.persist_path)
            json_unformatted = json.load(f)
            for analysis_json in json_unformatted.values():
                self.analyses[analysis_json["id"]] = \
                    Analysis.deserialize_from_json(analysis_json)
        else:
            print("No analysis manager found. Initializing.")

    def persist_analyses(self):
        formatted_json = {}
        for analysis in self.analyses.values():
            formatted_json[analysis.id] = analysis.serialize_self()

        with open(self.persist_path, 'w') as f:
            json.dump(formatted_json, f)
