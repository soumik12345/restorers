from typing import Dict, Tuple

import tensorflow as tf

from restorers.losses import SpatialConsistencyLoss
from restorers.losses.zero_reference import (
    color_constancy,
    exposure_control_loss,
    illumination_smoothness_loss,
)

from .dce_layer import DeepCurveEstimationLayer


class ZeroDCE(tf.keras.Model):
    def __init__(
        self, num_intermediate_filters: int, num_iterations: int, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.num_intermediate_filters = num_intermediate_filters
        self.num_iterations = num_iterations

        self.deep_curve_estimation = DeepCurveEstimationLayer(
            num_intermediate_filters=self.num_intermediate_filters,
            num_iterations=self.num_iterations,
        )

    def compile(
        self,
        weight_exposure_loss: float,
        weight_color_constancy_loss: float,
        weight_illumination_smoothness_loss: float,
        *args,
        **kwargs
    ) -> None:
        super().compile(*args, **kwargs)
        self.weight_exposure_loss = weight_exposure_loss
        self.weight_color_constancy_loss = weight_color_constancy_loss
        self.weight_illumination_smoothness_loss = weight_illumination_smoothness_loss
        self.spatial_constancy_loss = SpatialConsistencyLoss()

    def get_enhanced_image(
        self, data: tf.Tensor, output: tf.Tensor
    ) -> Tuple[tf.Tensor]:
        curves = tf.split(output, self.num_iterations, axis=-1)
        enhanced_image, enhanced_images = data, []
        for idx in range(self.num_iterations):
            enhanced_image = enhanced_image + curves[idx] * (
                tf.square(enhanced_image) - enhanced_image
            )
            enhanced_images.append(enhanced_image)
        return enhanced_images[:-1], enhanced_image

    def call(self, data: tf.Tensor, training=None, mask=None) -> Tuple[tf.Tensor]:
        dce_net_output = self.deep_curve_estimation(data)
        return self.get_enhanced_image(data, dce_net_output)

    def compute_losses(
        self, data: tf.Tensor, output: tf.Tensor
    ) -> Dict[str, tf.Tensor]:
        enhanced_image = self.get_enhanced_image(data, output)
        loss_illumination = illumination_smoothness_loss(output)
        loss_spatial_constancy = tf.reduce_mean(
            self.spatial_constancy_loss(enhanced_image, data)
        )
        loss_color_constancy = tf.reduce_mean(color_constancy(enhanced_image))
        loss_exposure = tf.reduce_mean(exposure_control_loss(enhanced_image))
        total_loss = (
            loss_spatial_constancy
            + self.weight_illumination_smoothness_loss * loss_illumination
            + self.weight_color_constancy_loss * loss_color_constancy
            + self.weight_exposure_loss * loss_exposure
        )
        return {
            "total_loss": total_loss,
            "illumination_smoothness_loss": loss_illumination,
            "spatial_constancy_loss": loss_spatial_constancy,
            "color_constancy": loss_color_constancy,
            "exposure_control_loss": loss_exposure,
        }

    def train_step(self, data: tf.Tensor) -> Dict[str, tf.Tensor]:
        with tf.GradientTape() as tape:
            _, output = self.deep_curve_estimation(data)
            losses = self.compute_losses(data, output)
        gradients = tape.gradient(losses["total_loss"], self.trainable_weights)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_weights))
        return losses

    def test_step(self, data: tf.Tensor) -> Dict[str, tf.Tensor]:
        _, output = self.deep_curve_estimation(data)
        return self.compute_losses(data, output)

    def get_config(self) -> Dict:
        return {
            "num_intermediate_filters": self.num_intermediate_filters,
            "num_iterations": self.num_iterations,
        }

    def save(self, filepath: str, *args, **kwargs) -> None:
        input_tensor = tf.keras.Input(shape=[None, None, 3])
        saved_model = tf.keras.Model(
            inputs=input_tensor, outputs=self.call(input_tensor)
        )
        saved_model.save(filepath, *args, **kwargs)
