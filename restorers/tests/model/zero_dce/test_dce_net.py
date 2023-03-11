import unittest

import tensorflow as tf

from restorers.model.zero_dce import DeepCurveEstimationLayer, ZeroDCE


class ZeroDCETest(unittest.TestCase):
    def test_dce_layer(self) -> None:
        x = tf.ones((1, 256, 256, 3))
        dce_layer = DeepCurveEstimationLayer(filters=32, num_iterations=8)
        y = dce_layer(x)
        self.assertEqual(y.shape, (1, 256, 256, 3 * dce_layer.num_iterations))

    def test_zero_dce(self) -> None:
        x = tf.ones((1, 256, 256, 3))
        model = ZeroDCE(filters=32, num_iterations=8)
        output = model(x)
        self.assertEqual(output.shape, (1, 256, 256, 3))
