#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
from .value_definitions import value_definitions


class PrioritySorter():
    def __init__(self, prioritization_rules, log_verbose=False):
        self.prioritization_rules = prioritization_rules
        self.log_verbose = log_verbose

    def sort_analyses(self, analyses):
        sorted_analyses = []
        analyses_copy = []
        for analysis in analyses:
            analyses_copy.append(analysis)
        while len(analyses_copy) > 0:
            next_highest = self.try_find_highest_value_analysis(analyses_copy)
            if not next_highest:
                for i in range(len(analyses_copy)):
                    sorted_analyses.append(analyses_copy.pop(0))
            else:
                index_to_pop = self.get_analysis_index(
                    next_highest.id,
                    analyses_copy)
                sorted_analyses.append(analyses_copy.pop(index_to_pop))

        if self.log_verbose:
            print("Sorted Analyses", len(sorted_analyses))
            for anal in sorted_analyses:
                print("\n Analysis: ")
                for pred in anal.predictions.values():
                    print(f"{pred.name} - {pred.score}")
        return sorted_analyses

    def try_find_highest_value_analysis(self, analyses):
        if len(analyses) == 0:
            raise Exception(
                "Analyses must have at least one entry to find best")
        for rule in self.prioritization_rules:
            if not self.are_all_target_values_same(analyses, rule.category):
                return self.get_winning_value_for_category(
                    analyses,
                    rule.category,
                    rule.value_definition)
        return False

    def get_winning_value_for_category(
            self,
            analyses,
            category_name,
            winning_definition):
        winning_analysis = analyses[0]
        winning_value = self.get_target_value_from_analysis(
            winning_analysis,
            category_name)
        for analysis in analyses:
            next_val = self.get_target_value_from_analysis(
                analysis,
                category_name)
            if winning_definition == value_definitions["highest"]:
                if next_val > winning_value:
                    winning_analysis = analysis
                    winning_value = next_val
            elif winning_definition == value_definitions["lowest"]:
                if next_val < winning_value:
                    winning_analysis = analysis
                    winning_value = next_val

        return winning_analysis

    def are_all_target_values_same(self, analyses, category_name):

        initial_value = self.get_target_value_from_analysis(
            analyses[0],
            category_name)

        for analysis in analyses:
            if (self.get_target_value_from_analysis(analysis, category_name)
                    != initial_value):
                return False

        return True

    def get_target_value_from_analysis(self, analysis, category_name):
        if category_name in analysis.predictions:
            return analysis.predictions[category_name].score
        else:
            return -1

    def get_analysis_index(self, analysis_id, analyses):
        for i in range(len(analyses)):
            if analysis_id == analyses[i].id:
                return i

        raise Exception("Analysis not found!")
