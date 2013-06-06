# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from appconf import AppConf
from django.conf import settings  # noqa
from django.core.exceptions import ImproperlyConfigured


log = logging.getLogger(__name__)


class StaticPreprocessorAppConf(AppConf):

    ROOT = None
    STORAGE = 'staticpreprocessor.storage.StaticPreprocessorFileStorage'
    FINDERS = []
    PROCESSORS = []
    DIRS = []

    class Meta:
        prefix = 'static_preprocessor'

    def configure(self):
        root = self.configured_data.get('ROOT')
        if not root:
            raise ImproperlyConfigured(
                'You must set a STATIC_PREPROCESSOR_ROOT')
        if root == settings.STATIC_ROOT:
            raise ImproperlyConfigured(
                'STATIC_PREPROCESSOR_ROOT cannot be the same as '
                'STATIC_ROOT')
        return self.configured_data
