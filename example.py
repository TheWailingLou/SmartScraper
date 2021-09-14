#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import os

from find import search
from common_prioritizations import COMMON_PRIORITIZATIONS
from common_filters import COMMON_FILTERS
from search_config import SearchConfig
from smart_search.filters.classification_filter import ClassificationFilter
from smart_search.filters.classification_bundle import ClassificationBundle

prioritization_rules = COMMON_PRIORITIZATIONS["test_dog"]

cur_dir_abspath = os.path.dirname(os.path.abspath(__file__))

dog_filter = ClassificationFilter(COMMON_FILTERS["test_dog"])
dog_path = os.path.abspath(cur_dir_abspath + "/results/test/dog")

cat_filter = ClassificationFilter(COMMON_FILTERS["test_cat"])
cat_path = os.path.abspath(cur_dir_abspath + "/results/test/cat")

all_filter = ClassificationFilter(COMMON_FILTERS["control"])
all_path = os.path.abspath(cur_dir_abspath + "/results/test/all_images")

classification_bundles = [
    ClassificationBundle(dog_filter, "dog", dog_path),
    ClassificationBundle(cat_filter, "cat", cat_path),
    ClassificationBundle(all_filter, "all", all_path),
]

search(SearchConfig(search_term="dog", images_to_scrape=2),
       prioritization_rules, classification_bundles)
