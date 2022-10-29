import unittest

import tensorflow as tf

from mirnetv2.model.downsample import DownBlock, DownSampleBlock
from mirnetv2.model.rcb import ContextBlock, ResidualContextBlock
from mirnetv2.model.skff import SelectiveKernelFeatureFusion
from mirnetv2.model.upsample import UpBlock, UpSampleBlock
from mirnetv2.model.mrb import MultiScaleResidualBlock


class ModelTester(unittest.TestCase):
    def test_skff(self):
        x = tf.ones((1, 256, 256, 120))
        y = SelectiveKernelFeatureFusion(channels=120)([x, x])
        self.assertEqual(y.shape, (1, 256, 256, 120))

    def test_context_block(self):
        x = tf.ones((1, 512, 512, 80))
        y = ContextBlock(channels=80)(x)
        self.assertEqual(y.shape, (1, 512, 512, 80))

    def test_residual_context_block(self):
        x = tf.ones((1, 512, 512, 80))
        y = ResidualContextBlock(channels=80, groups=1)(x)
        self.assertEqual(y.shape, (1, 512, 512, 80))
        y = ResidualContextBlock(channels=80, groups=2)(x)
        self.assertEqual(y.shape, (1, 512, 512, 80))

    def test_down_block(self):
        x = tf.ones((1, 512, 512, 80))
        y = DownBlock(channels=80, channel_factor=1.5)(x)
        self.assertEqual(y.shape, (1, 256, 256, 120))

    def test_downsample_block(self):
        x = tf.ones((1, 512, 512, 80))
        y = DownSampleBlock(channels=80, scale_factor=2, channel_factor=1.5)(x)
        self.assertEqual(y.shape, (1, 256, 256, 120))

    def test_up_block(self):
        x = tf.ones((1, 128, 128, 180))
        y = UpBlock(channels=180, channel_factor=1.5)(x)
        self.assertEqual(y.shape, (1, 256, 256, 120))

    def test_upsample_block(self):
        x = tf.ones((1, 128, 128, 180))
        y = UpSampleBlock(channels=180, scale_factor=2, channel_factor=1.5)(x)
        self.assertEqual(y.shape, (1, 256, 256, 120))

    def test_mrb(self):
        x = tf.ones((1, 512, 512, 80))
        y = MultiScaleResidualBlock(channels=80, channel_factor=1.5, groups=1)(x)
        self.assertEqual(y.shape, (1, 512, 512, 80))
