#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sun Sep 12 14:54:01 2021

@author: louis
"""
import os
import json


class SessionManager():
    def __init__(self, persist_path):
        self.session = dict()
        self.persist_path = persist_path

    def add_image(self, image_path, classification):
        if classification in self.session.keys():
            self.session[classification].append(image_path)
        else:
            self.session[classification] = [image_path]

    def log_session(self):
        print("Now logging session x")
        for key in self.session:
            print(f"{key}:")
            for path in self.session[key]:
                print(f"\t{path}")

    def load_manager(self):
        if os.path.isfile(self.persist_path):
            f = open(self.persist_path)
            json_unformatted = json.load(f)

            print(f"Sessions: {json_unformatted}")
            return json_unformatted

        else:
            print("No session manager data found. Initializing.")
            return []

    def persist_manager(self):
        formatted_json = self.load_manager()
        new_index = len(formatted_json)
        formatted_json.append({})
        for classification_name in self.session.keys():
            formatted_json[new_index][classification_name] = self.session[
                classification_name]

        with open(self.persist_path, 'w') as f:
            json.dump(formatted_json, f)
