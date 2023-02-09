import os
from glob import glob
from typing import List, Dict, Callable, Optional

import numpy as np
import tensorflow as tf

from .base import BaseEvaluator
from ..dataloader.base.commons import read_image
from ..utils import scale_tensor, fetch_wandb_artifact


class LoLEvaluator(BaseEvaluator):
    def __init__(
        self,
        metrics: List[tf.keras.metrics.Metric],
        model: Optional[tf.keras.Model] = None,
        input_size: Optional[List[int]] = None,
        bit_depth: float = 8,
        benchmark_against_input: bool = False,
    ):
        """Evaluator for the LoL dataset.

        Args:
            metrics List[tf.keras.metrics.Metric]: A dictionary of metrics.
            model (Optional[tf.keras.Model]): The `tf.keras.Model` to be evaluated.
            input_size (Optional[List[int]]): input size for the model. This is an optional parameter which if
                specified will enable GFLOPs calculation.
            bit_depth (float): bit depth of the input and ground truth images.
            benchmark_against_input (bool): If True, the model output will be evaluated against the input image.
        """
        self.normalization_factor = (2**bit_depth) - 1
        self.dataset_artifact_address = "ml-colabs/dataset/LoL:v0"
        self.benchmark_against_input = benchmark_against_input
        super().__init__(metrics, model, input_size)

    def preprocess(self, image_path):
        return tf.expand_dims(read_image(image_path, self.normalization_factor), axis=0)

    def postprocess(self, input_tensor):
        return np.squeeze(scale_tensor(input_tensor))

    def populate_image_paths(self):
        dataset_path = fetch_wandb_artifact(
            self.dataset_artifact_address, artifact_type="dataset"
        )
        train_low_light_images = sorted(
            glob(os.path.join(dataset_path, "our485", "low", "*"))
        )
        train_enhanced_images = sorted(
            glob(os.path.join(dataset_path, "our485", "high", "*"))
        )
        test_low_light_images = sorted(
            glob(os.path.join(dataset_path, "eval15", "low", "*"))
        )
        test_enhanced_images = sorted(
            glob(os.path.join(dataset_path, "eval15", "high", "*"))
        )
        return (
            {
                "train": (train_low_light_images, train_enhanced_images),
                "eval15": (test_low_light_images, test_enhanced_images),
            }
            if not self.benchmark_against_input
            else {
                "train": (train_low_light_images, train_low_light_images),
                "eval15": (test_low_light_images, test_low_light_images),
            }
        )
