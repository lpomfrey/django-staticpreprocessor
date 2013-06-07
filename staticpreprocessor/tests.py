# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from staticpreprocessor.conf import StaticPreprocessorAppConf, settings
from staticpreprocessor.finders import FileSystemFinder


TEST_PROJECT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../test_project/')
)


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


class TestFileSystemFinderExceptions(TestCase):

    @override_settings(STATIC_PREPROCESSOR_DIRS='me-broken')
    def test_broken_dirs_setting(self):
        with self.assertRaises(ImproperlyConfigured):
            FileSystemFinder()

    @override_settings(
        STATIC_PREPROCESSOR_DIRS=['/rootdir/'],
        STATIC_PREPROCESSOR_ROOT='/rootdir/',
    )
    def test_invalid_dirs_setting(self):
        with self.assertRaises(ImproperlyConfigured):
            FileSystemFinder()


@override_settings(
    STATIC_PREPROCESSOR_DIRS=[
        ('some-prefix', os.path.join(TEST_PROJECT, 'rawstaticprefixed')),
        os.path.join(TEST_PROJECT, 'rawstatic'),
    ],
    STATIC_PREPROCESSOR_ROOT=
    os.path.join(TEST_PROJECT, 'processedstatic'),
    STATIC_PREPROCESSOR_FINDERS=[
        'staticpreprocessor.finders.FileSystemFinder',
    ]
)
class TestFileSystemFinderCollection(TestCase):

    def setUp(self):
        pre_prefixed = os.path.join(TEST_PROJECT, 'rawstaticprefixed')
        pre_unprefixed = os.path.join(TEST_PROJECT, 'rawstatic')
        post = os.path.join(TEST_PROJECT, 'processedstatic')
        for dir in (pre_prefixed, pre_unprefixed, post):
            if os.path.exists(dir):
                shutil.rmtree(dir, ignore_errors=True)
            os.makedirs(dir)
        self.pre_prefixed, self.pre_unprefixed, self.post = \
            pre_prefixed, pre_unprefixed, post

    def tearDown(self):
        for dir in (self.pre_prefixed, self.pre_unprefixed, self.post):
            shutil.rmtree(dir, ignore_errors=True)

    def test_prefixed(self):
        FILE = os.path.join(self.pre_prefixed, 'testfile.txt')
        with open(FILE, 'w') as f:
            f.write('This is a test file')
        call_command('preprocess_static', interactive=False, clear=True)
        with open(os.path.join(
                self.post, 'some-prefix/testfile.txt'), 'r') as f:
            self.assertEqual(f.read().strip(), 'This is a test file')

    def test_unprefixed(self):
        FILE = os.path.join(self.pre_unprefixed, 'testfile.txt')
        with open(FILE, 'w') as f:
            f.write('This is a test file')
        call_command('preprocess_static', interactive=False, clear=True)
        with open(os.path.join(self.post, 'testfile.txt'), 'r') as f:
            self.assertEqual(f.read().strip(), 'This is a test file')


@override_settings(
    STATIC_PREPROCESSOR_ROOT=
    os.path.join(TEST_PROJECT, 'processedstatic'),
    STATIC_PREPROCESSOR_FINDERS=[
        'staticpreprocessor.finders.AppDirectoriesFinder',
    ],
    INSTALLED_APPS=['test_app', 'staticpreprocessor'],
)
class TestAppDirectoriesFinder(TestCase):

    def test_collection(self):
        call_command('preprocess_static', interactive=False, clear=False)
        with open(os.path.join(
                TEST_PROJECT, 'processedstatic', 'testappfile.txt'), 'r') as f:
            self.assertEqual(f.read().strip(), 'I am an application test file')
