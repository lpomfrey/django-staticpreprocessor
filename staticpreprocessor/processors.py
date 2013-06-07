# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import fnmatch
import itertools
import os
import re

import envoy
from django.contrib.staticfiles.utils import get_files

from .conf import settings
from .storage import default_storage


class BaseProcessor(object):

    storage = default_storage
    exclude_match = ''
    exclude_regex = ''
    include_match = ''
    include_regex = ''
    extensions = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for k, v in self.kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def get_file_list(self, **kwargs):
        file_list = get_files(
            self.storage, location=settings.STATIC_PREPROCESSOR_ROOT)
        if self.extensions is not None:
            file_list = itertools.ifilter(
                lambda f: os.path.splitext(f)[1] in self.extensions, file_list)
        if self.exclude_match:
            file_list = itertools.ifilter(
                lambda f: not fnmatch.fnmatch(f, self.exclude_match),
                file_list
            )
        if self.exclude_regex:
            exclude_regex = re.compile(self.exclude_regex)
            file_list = itertools.ifilter(
                lambda f: not bool(exclude_regex.search(f)), file_list)
        if self.include_match:
            file_list = itertools.ifilter(
                lambda f: fnmatch.fnmatch(f, self.include_match),
                file_list
            )
        if self.include_regex:
            include_regex = re.compile(self.include_regex)
            file_list = itertools.ifilter(
                lambda f: bool(include_regex.search(f)), file_list)
        return file_list

    def handle(self, **kwargs):
        raise NotImplementedError()


class BaseListProcessor(BaseProcessor):

    remove_processed_files = True

    def handle_list(self, file_list, **kwargs):
        raise NotImplementedError()

    def handle(self, **kwargs):
        kwargs.update(self.kwargs)
        self.handle_list(self.get_file_list(**kwargs), **kwargs)
        if self.remove_processed_files:
            for file in self.get_file_list(**kwargs):
                self.storage.delete(file)


class BaseFileProcessor(BaseListProcessor):

    def handle_file(self, file, **kwargs):
        raise NotImplementedError()

    def handle_list(self, file_list, **kwargs):
        for file in file_list:
            self.handle_file(file, **kwargs)


class CommandProcessorMixin(BaseListProcessor):

    command = ''
    output = ''
    expected_return_codes = [0]
    require_input = True

    def get_command(self, **kwargs):
        return self.command.format(**kwargs)

    def run_command(self, input, **kwargs):
        if not input and self.require_input:
            return
        kwargs.update({
            'input': input,
            'output': self.storage.path(self.output),
        })
        command = self.get_command(input=input, **kwargs)
        r = envoy.run(command)
        if not r.status_code in self.expected_return_codes:
            raise RuntimeError(
                'Static preprocessor command returned an unexpected return '
                'code. Got: {0} Expected one of: {1}'
                .format(r.status_code, self.expected_return_codes))


class CommandListProcessor(CommandProcessorMixin, BaseListProcessor):

    def handle_list(self, file_list, **kwargs):
        self.run_command(' '.join(file_list), **kwargs)


class CommandFileProcessor(CommandProcessorMixin, BaseFileProcessor):

    def handle_file(self, file, **kwargs):
        self.run_command(file, **kwargs)
