#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""
import os
import io
import uuid
import requests

from PIL import Image  # type: ignore


class ImageDownloader():
    def __init__(
            self,
            temp_out_path,
            persist_out_path,
            temp_out_name="temp.jpg",
            log_verbose=False):
        self.temp_out_path = temp_out_path
        self.temp_out_name = temp_out_name
        self.persist_out_path = persist_out_path
        self.log_verbose = log_verbose

    def persist_temp_img(self, url):
        return self.persist_image(
            url,
            output_path=self.temp_out_path,
            output_name=self.temp_out_name)

    def persist_image(self, url, output_path=None, output_name=None):
        try:
            image_content = requests.get(url).content

        except Exception as e:
            print(f"ERROR: Could not download {url} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')

            if output_name is None:
                output_name = str(uuid.uuid4()) + '.jpg'
            if output_path is None:
                output_path = self.persist_out_path

            file_path = os.path.join(output_path, output_name)

            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)

            return file_path

        except Exception as e:
            if self.log_verbose:
                print(f"ERROR: Could not save image from {url} - {e}")
            return False

    def persist_images(self, image_urls, output_path=None):
        output_paths = []
        if output_path is None:
            output_path = self.persist_out_path
        for url in image_urls:
            new_img_path = self.persist_image(url, output_path)
            output_paths.append(new_img_path)

        print(f"Saved {len(image_urls)} new images.")
        return output_paths
