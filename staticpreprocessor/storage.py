# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.staticfiles.storage import AppStaticStorage
from django.core.files.storage import FileSystemStorage, get_storage_class
from django.utils.functional import LazyObject

from staticpreprocessor.conf import settings


class StaticPreprocessorAppStorage(AppStaticStorage):

    source_dir = 'rawstatic'


class StaticPreprocessorFileStorage(FileSystemStorage):

    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_PREPROCESSOR_ROOT
        super(StaticPreprocessorFileStorage, self).__init__(
            location, None, *args, **kwargs)
        self.base_url = None

    def get_available_name(self, name):
        '''
        Deletes the given file if it exists.
        '''
        if self.exists(name):
            self.delete(name)
        return name


class DefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(
            settings.STATIC_PREPROCESSOR_STORAGE)()

default_storage = DefaultStorage()
