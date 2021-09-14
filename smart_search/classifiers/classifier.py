#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
from .nn_classifiers import CLASSIFIERS


class Classifier():
    def __init__(self, classifier_type, display_results):

        if CLASSIFIERS[classifier_type] is None:
            raise Exception(f"Classifier {classifier_type} not found!")

        self.classification_strategy = classifier_type
        self.settings = {
            "display_results": display_results,
            "image_display_window_name": "Image Default"
        }

    def classify(self, img):
        raise NotImplementedError(
            "Base class does not have a classifier implementation")
