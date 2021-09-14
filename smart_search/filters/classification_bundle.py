#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 14:35:41 2021

@author: louis
"""


class ClassificationBundle():
    def __init__(self, filter, name, persist_out_path):
        self.filter = filter
        self.name = name
        self.persist_out_path = persist_out_path
