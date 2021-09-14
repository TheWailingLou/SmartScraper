#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
from smart_search.filters.prioritization_rule import PrioritizationRule

COMMON_PRIORITIZATIONS = {
    "test_dog": [
        PrioritizationRule("dog", "highest"),
        PrioritizationRule("cat", "lowest")
    ],
    "test_cat": [
        PrioritizationRule("dog", "lowest"),
        PrioritizationRule("cat", "highest")
    ],
}
