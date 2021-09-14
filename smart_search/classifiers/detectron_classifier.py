#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import torch  # noqa: F401
import torchvision  # noqa: F401
import detectron2  # noqa: F401
import os  # noqa: F401
import json  # noqa: F401
import cv2  # noqa: F401
import numpy as np  # noqa: F401

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog  # noqa: F401

from .classifier import Classifier
from .nn_classifiers import CLASSIFIERS
from .prediction import InstancePrediction, Analysis

detectron_models = {
    "LVIS": "LVISv0.5-InstanceSegmentation/mask_rcnn_R_101_FPN_1x.yaml"
    # could add other models here.
}


class DetectronClassifier(Classifier):
    def __init__(self, model_name="LVIS", display_results=True):
        Classifier.__init__(
            self,
            classifier_type=CLASSIFIERS["DETECTRON2"],
            display_results=display_results)

        if detectron_models[model_name] is None:
            raise Exception(f"Model {model_name} not included in classifier")

        self.config_file = detectron_models[model_name]
        self.model_type = "detectron"
        self.model_name = model_name

        cfg = get_cfg()
        cfg.MODEL.DEVICE = "cpu"  # TODO: make this modifiable
        cfg.merge_from_file(model_zoo.get_config_file(self.config_file))
        # TODO: make this modifiable
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(self.config_file)

        self.config = cfg
        self.predictor = DefaultPredictor(self.config)
        self.settings["image_display_window_name"] = 'Detectron2 Image'

    def classify(self, im_path, origin_url, display_results=None):
        im = cv2.imread(im_path)

        try:
            predictor_outputs = self.predictor(im)
        except Exception as e:
            raise Exception("Could not make predictions for image "
                            f"{im} with path {im_path}:", e)

        should_display_results = self.settings["display_results"] and (
            display_results is True or display_results is None)

        if should_display_results:
            self.draw_result(predictor_outputs, im)

        return self.format_output(predictor_outputs, origin_url)

    def draw_result(self, predictor_outputs, image):
        v = Visualizer(
            image[:, :, ::-1],
            MetadataCatalog.get(
                self.config.DATASETS.TRAIN[0]),
            scale=1.2)

        out = v.draw_instance_predictions(
            predictor_outputs["instances"].to("cpu"))

        # pylint: disable=no-member
        cv2.imshow(
            self.settings["image_display_window_name"],
            out.get_image()[:, :, ::-1])
        # pylint: disable=no-member
        cv2.waitKey(0)
        # pylint: disable=no-member
        cv2.destroyAllWindows()
        return

    def format_output(self, predictor_out, origin_url):
        pre_format = {}
        instances = predictor_out["instances"]
        for i in range(len(instances)):
            converted_label = self.getCategoryName(instances.pred_classes[i])
            # have not seen this with a greater depth
            bbox = instances.pred_boxes[i].tensor.numpy().tolist()[0]
            score = float(instances.scores[i])

            if converted_label in pre_format:
                new_instance = {
                    'score': score,
                    'bbox': bbox
                }
                pre_format[converted_label].append(new_instance)

            else:
                pre_format[converted_label] = [{
                    'score': score,
                    'bbox': bbox
                }]

        predictions = []

        for label in pre_format.keys():
            predictions.append(InstancePrediction(label, pre_format[label]))

        return Analysis(
            predictions,
            url=origin_url,
            model_type=self.model_type,
            model_name=self.model_name)

    def getCategoryName(self, pred_class):
        return MetadataCatalog.get(
            self.config.DATASETS.TRAIN[0]).thing_classes[pred_class]
