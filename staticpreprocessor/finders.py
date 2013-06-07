# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import SortedDict
from django.utils.functional import memoize
from django.utils.importlib import import_module
from django.utils._os import safe_join

from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import (
    BaseFinder, AppDirectoriesFinder as BaseAppDirectoriesFinder
)

from .storage import StaticPreprocessorAppStorage


_finders = SortedDict()


class FileSystemFinder(BaseFinder):
    '''
    A static files finder that uses the ``STATIC_PREPROCESSOR_DIRS`` setting
    to locate files.
    '''
    def __init__(self, apps=None, *args, **kwargs):
        # List of locations with static files
        self.locations = []
        # Maps dir paths to an appropriate storage instance
        self.storages = SortedDict()
        if not isinstance(settings.STATIC_PREPROCESSOR_DIRS, (list, tuple)):
            raise ImproperlyConfigured(
                'Your STATIC_PREPROCESSOR_DIRS setting is not a tuple or '
                'list; perhaps you forgot a trailing comma?')
        for root in settings.STATIC_PREPROCESSOR_DIRS:
            if isinstance(root, (list, tuple)):
                prefix, root = root
            else:
                prefix = ''
            if os.path.abspath(settings.STATIC_PREPROCESSOR_ROOT) == \
                    os.path.abspath(root):
                raise ImproperlyConfigured(
                    'The STATIC_PREPROCESSOR_DIRS setting should '
                    'not contain the STATIC_PREPROCESSOR_ROOT setting')
            if (prefix, root) not in self.locations:
                self.locations.append((prefix, root))
        for prefix, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage
        super(FileSystemFinder, self).__init__(*args, **kwargs)

    def find(self, path, all=False):
        '''
        Looks for files in the extra locations
        as defined in ``STATIC_PREPROCESSOR_DIRS``.
        '''
        matches = []
        for prefix, root in self.locations:
            matched_path = self.find_location(root, path, prefix)
            if matched_path:
                if not all:
                    return matched_path
                matches.append(matched_path)
        return matches

    def find_location(self, root, path, prefix=None):
        '''
        Finds a requested static file in a location, returning the found
        absolute path (or ``None`` if no match).
        '''
        if prefix:
            prefix = '%s%s' % (prefix, os.sep)
            if not path.startswith(prefix):
                return None
            path = path[len(prefix):]
        path = safe_join(root, path)
        if os.path.exists(path):
            return path

    def list(self, ignore_patterns):
        '''
        List all files in all locations.
        '''
        for prefix, root in self.locations:
            storage = self.storages[root]
            for path in utils.get_files(storage, ignore_patterns):
                yield path, storage


class AppDirectoriesFinder(BaseAppDirectoriesFinder):
    '''
    A static files finder that looks in the directory of each app as
    specified in the source_dir attribute of the given storage class.
    '''
    storage_class = StaticPreprocessorAppStorage


def find(path, all=False):
    '''
    Find a static file with the given path using all enabled finders.

    If ``all`` is ``False`` (default), return the first matching
    absolute path (or ``None`` if no match). Otherwise return a list.
    '''
    matches = []
    for finder in get_finders():
        result = finder.find(path, all=all)
        if not all and result:
            return result
        if not isinstance(result, (list, tuple)):
            result = [result]
        matches.extend(result)
    if matches:
        return matches
    # No match.
    return all and [] or None


def get_finders():
    for finder_path in settings.STATIC_PREPROCESSOR_FINDERS:
        yield get_finder(finder_path)


def _get_finder(import_path):
    '''
    Imports the staticpreprocessor finder class described by import_path, where
    import_path is the full Python path to the class.
    '''
    module, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured(
            'Error importing module {0}: "{1}"'.format(module, e))
    try:
        Finder = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            'Module "{0}" does not define a "{1}" class.'.format(module, attr))
    if not issubclass(Finder, BaseFinder):
        raise ImproperlyConfigured(
            'Finder "{0}" is not a subclass of "{1}"'
            .format(Finder, BaseFinder))
    return Finder()
get_finder = memoize(_get_finder, _finders, 1)
