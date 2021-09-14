#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
from smart_search.filters.classification_filter import FilterRule

COMMON_FILTERS = {
    "test_dog": {
        FilterRule("dog", ">", 0.7),
        FilterRule("cat", "<", 0.5, q_compare='=', expected_quantity=0)},
    "test_cat": {
        FilterRule("cat", ">", 0.7),
        FilterRule("dog", "<", 0.5, q_compare='=', expected_quantity=0)},
    "control": {
        FilterRule("dog", "<", 1.0, q_compare='>=', expected_quantity=0)},
}
