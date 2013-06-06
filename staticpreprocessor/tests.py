# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from staticpreprocessor.conf import StaticPreprocessorAppConf, settings


class TestConf(TestCase):

    @override_settings(STATIC_PREPROCESSOR_ROOT=None)
    def test_no_root_raises(self):
        conf = StaticPreprocessorAppConf()
        conf._meta.configured_data['ROOT'] = None
        with self.assertRaises(ImproperlyConfigured):
            conf.configure()

    @override_settings(STATIC_PREPROCESSOR_ROOT=settings.STATIC_ROOT)
    def test_root_equal_to_static_root_raises(self):
        conf = StaticPreprocessorAppConf()
        conf._meta.configured_data['ROOT'] = settings.STATIC_ROOT
        with self.assertRaises(ImproperlyConfigured):
            conf.configure()
