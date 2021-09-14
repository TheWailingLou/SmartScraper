#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import uuid


class Analysis():
    def __init__(self, predictions, url, model_type, model_name):
        self.predictions = {}
        self.id = str(uuid.uuid4())
        self.model_type = model_type
        self.model_name = model_name
        self.url = url
        for prediction in predictions:
            if prediction.name in self.predictions:
                raise Exception(
                    "Should only be one prediction per type, "
                    f"but found multiple! Duplicate key: {prediction.name}")
            else:
                self.predictions[prediction.name] = prediction

    def serialize_self(self):
        serialized_analysis = {}
        serialized_predictions = {}

        for prediction in self.predictions.values():

            serialized_predictions[prediction.name] = \
                prediction.serialize_self()

        serialized_analysis["predictions"] = serialized_predictions
        serialized_analysis["id"] = self.id
        serialized_analysis["model_type"] = self.model_type
        serialized_analysis["model_name"] = self.model_name
        serialized_analysis["url"] = self.url
        return serialized_analysis

    @classmethod
    def deserialize_from_json(self, analysis_json):

        predictions = []
        for prediction_json in analysis_json["predictions"].values():
            predictions.append(InstancePrediction.deserialize_from_json(
                prediction_json))

        return Analysis(
            predictions,
            url=analysis_json["url"],
            model_type=analysis_json["model_type"],
            model_name=analysis_json["model_name"])


class InstancePrediction ():
    def __init__(self, name, separated_instances, has_bbox=True):
        self.name = name  # Name of classified output, e.g. 'dog'
        self.separated = {}  # Instances with score for each instance
        separated_scores = []

        if has_bbox:
            for i in range(0, len(separated_instances)):
                self.separated[str(i)] = {
                    'id': str(i),
                    'score': separated_instances[i]['score'],
                    'bbox': separated_instances[i]['bbox']
                }
                separated_scores.append(separated_instances[i]['score'])
        else:
            for i in range(0, len(separated_instances)):
                self.separated[str(i)] = {
                    'id': str(i),
                    'score': separated_instances[i]['score']
                }
                separated_scores.append(separated_instances[i]['score'])

        hi_score = max(separated_scores)

        self.hi_score = hi_score
        self.lo_score = min(separated_scores)
        self.score = hi_score
        self.quantity = len(separated_scores)

    def serialize_self(self):
        serialized_prediction = {}

        serialized_separated_predictions = {}
        for separated in self.separated.values():
            serialized_separated_prediction = {}

            if "bbox" in separated:
                bbox = {}
                bbox_list = separated["bbox"]
                for i in range(len(bbox_list)):
                    bbox[str(i)] = float(bbox_list[i])

                serialized_separated_prediction["bbox"] = bbox

            serialized_separated_prediction["id"] = separated["id"]
            serialized_separated_prediction["score"] = separated["score"]

            serialized_separated_predictions[separated["id"]] = \
                serialized_separated_prediction

        serialized_prediction["separated"] = serialized_separated_predictions
        serialized_prediction["name"] = self.name

        return serialized_prediction

    @classmethod
    def deserialize_from_json(self, prediction_json):

        formatted_separated = []
        has_bbox = True
        for separated in prediction_json["separated"].values():
            deserialized_separated = {
                'id': separated["id"],
                'score': separated['score']
            }

            if "bbox" in separated:
                deserialized_bbox = []
                for point in separated["bbox"].values():
                    deserialized_bbox.append(point)

                deserialized_separated["bbox"] = deserialized_bbox
            else:
                has_bbox = False

            formatted_separated.append(deserialized_separated)

        return InstancePrediction(
            name=prediction_json["name"],
            separated_instances=formatted_separated,
            has_bbox=has_bbox)
