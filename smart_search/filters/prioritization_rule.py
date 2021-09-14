#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
from .value_definitions import value_definitions


class PrioritizationRule():
    def __init__(
            self,
            category,
            value_definition=value_definitions["highest"]):
        if value_definition not in value_definitions.keys():
            print("Please set value definition to one of: ",
                  value_definitions.keys())
            raise Exception("value_definition selection not found!")

        self.category = category
        self.value_definition = value_definitions[value_definition]
