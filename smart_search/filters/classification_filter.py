#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""


class ClassificationFilter():
    def __init__(self, filter_rules, match_all=True):
        self.rules = filter_rules
        self.match_all = match_all

    def evaluate(self, predictions):
        for rule in self.rules:
            result = rule.apply(predictions)
            if self.match_all and not result:
                return False
            if not self.match_all and result:
                return True

        if self.match_all:
            return True
        else:
            return False


class FilterRule():
    def __init__(
            self,
            category,
            comparator,
            score,
            autoscore=0.,
            q_compare='>=',
            expected_quantity=1):
        self.category = category
        accepted_comparators = {'>': self.greater_than,
                                '<': self.less_than,
                                '>=': self.greater_e_than,
                                '<=': self.less_e_than,
                                '=': self.equal_to}
        if comparator in accepted_comparators.keys():
            self.comparator = accepted_comparators[comparator]
        else:
            raise Exception(
                "Invalid comparator. "
                "Please select from: '>','<','>=', '<=', '='")
        if q_compare in accepted_comparators.keys():
            self.q_compare = accepted_comparators[q_compare]
        else:
            raise Exception(
                "Invalid q_compare. "
                "Please select from: '>','<','>=', '<=', '=")
        if score < 1. or score > 0.:
            self.score = score
        else:
            raise Exception(
                "Invalid score. "
                "Please select a value between 0 and 1 (exclusive)")
        self.expected_quantity = expected_quantity
        self.autoscore = autoscore
        self.log_verbose = False

    def apply(self, analysis):
        try:
            prediction = analysis.predictions[self.category]
            actual_score = prediction.score
            verification_result = self.comparator(actual_score,  self.score)
            quantity = prediction.quantity
            q_verification_result = self.q_compare(
                quantity,
                self.expected_quantity)

            if self.log_verbose:
                print("{self.category} verification result: "
                      f"{verification_result and q_verification_result}")
                print(f"\tVerification for {self.category}: "
                      f"{verification_result}")
                print(f"\tQuantity verification: {q_verification_result}")

            return verification_result and q_verification_result
        except KeyError:
            q_verification_result = self.q_compare(0, self.expected_quantity)

            if self.log_verbose:
                print(f"{self.category} verification result: "
                      f"{q_verification_result}")
                print(f"\tKey '{self.category}' not found, "
                      "assuming quantity is 0. Q Result: "
                      f"{q_verification_result}")

            return q_verification_result

    def greater_than(self, actual, expected):
        return actual > expected

    def less_than(self, actual, expected):
        return actual < expected

    def greater_e_than(self, actual, expected):
        return actual >= expected

    def less_e_than(self, actual, expected):
        return actual <= expected

    def equal_to(self, actual, expected):
        return actual == expected
