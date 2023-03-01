import os
from glob import glob
from typing import Union

from .base import LowLightDatasetFactory, UnsupervisedDatasetFactory
from ..utils import fetch_wandb_artifact


class LOLDataLoader(LowLightDatasetFactory):
    def __init__(
        self,
        image_size: int,
        bit_depth: int,
        val_split: float,
        visualize_on_wandb: bool,
        dataset_artifact_address: Union[str, None] = None,
        dataset_url: Union[str, None] = None,
    ):
        super().__init__(
            image_size,
            bit_depth,
            val_split,
            visualize_on_wandb,
            dataset_artifact_address,
            dataset_url,
        )

    def define_dataset_structure(self, dataset_path, val_split):
        low_light_images = sorted(glob(os.path.join(dataset_path, "our485/low/*")))
        enhanced_images = sorted(glob(os.path.join(dataset_path, "our485/high/*")))
        self.test_low_light_images = sorted(
            glob(os.path.join(dataset_path, "eval15/low/*"))
        )
        self.test_enhanced_images = sorted(
            glob(os.path.join(dataset_path, "eval15/high/*"))
        )
        self.num_data_points = len(low_light_images)
        num_train_images = int(self.num_data_points * (1 - val_split))
        self.train_input_images = low_light_images[:num_train_images]
        self.train_enhanced_images = enhanced_images[:num_train_images]
        self.val_input_images = low_light_images[num_train_images:]
        self.val_enhanced_images = enhanced_images[num_train_images:]


class UnsupervisedLoLDataloader(UnsupervisedDatasetFactory):
    def __init__(
        self,
        image_size: int,
        bit_depth: int,
        val_split: float,
        use_low_light_images_only: bool = True,
        dataset_artifact_address: str = None,
    ) -> None:
        super().__init__(image_size, bit_depth, val_split)
        self.use_low_light_images_only = use_low_light_images_only
        self.dataset_artifact_address = dataset_artifact_address
        self.fetch_dataset(self.val_split, self.dataset_artifact_address)

    def fetch_dataset(self, val_split: float, dataset_artifact_address: str):
        artifact_dir = fetch_wandb_artifact(
            artifact_address=dataset_artifact_address, artifact_type="dataset"
        )
        low_light_images = sorted(glob(os.path.join(artifact_dir, "our485/low/*")))
        enhanced_images = sorted(glob(os.path.join(artifact_dir, "our485/high/*")))
        self.test_low_light_images = sorted(
            glob(os.path.join(artifact_dir, "eval15/low/*"))
        )
        self.test_enhanced_images = sorted(
            glob(os.path.join(artifact_dir, "eval15/high/*"))
        )
        self.num_data_points = len(low_light_images)
        num_train_images = int(self.num_data_points * (1 - val_split))
        self.train_low_light_images = low_light_images[:num_train_images]
        self.train_enhanced_images = enhanced_images[:num_train_images]
        self.val_low_light_images = low_light_images[num_train_images:]
        self.val_enhanced_images = enhanced_images[num_train_images:]

        self.train_input_images = (
            self.train_low_light_images
            if self.use_low_light_images_only
            else self.train_low_light_images + self.train_enhanced_images
        )
        self.val_input_images = (
            self.val_low_light_images
            if self.use_low_light_images_only
            else self.val_low_light_images + self.val_enhanced_images
        )
