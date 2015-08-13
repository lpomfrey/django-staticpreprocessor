# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch, MagicMock

from staticpreprocessor.conf import StaticPreprocessorAppConf, settings
from staticpreprocessor.contrib.processors import sass, less
from staticpreprocessor.finders import FileSystemFinder, get_finders
from staticpreprocessor.processors import (
    BaseProcessor, BaseListProcessor, BaseFileProcessor, CommandProcessorMixin,
    CommandListProcessor, CommandFileProcessor,
)
from staticpreprocessor.storage import StaticPreprocessorFileStorage


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
    STATIC_PREPROCESSOR_ROOT=os.path.join(TEST_PROJECT, 'processedstatic'),
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
    STATIC_PREPROCESSOR_ROOT=os.path.join(TEST_PROJECT, 'processedstatic'),
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


class TestBaseProcessor(TestCase):

    files = [
        '/path/to/some/file.txt',
        '/some/handlebars/template.handlebars',
        '/lots/of/less/css.less',
        '/and/some/sassy/css.sass',
    ]

    @patch('staticpreprocessor.processors.get_files')
    def test_default_list(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseProcessor()
        self.assertEqual(
            sorted(self.files),
            sorted(list(processor.get_file_list()))
        )

    @patch('staticpreprocessor.processors.get_files')
    def test_extensions(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseProcessor(extensions=['.sass', '.less'])
        self.assertEqual(
            sorted(['/lots/of/less/css.less', '/and/some/sassy/css.sass']),
            sorted(list(processor.get_file_list()))
        )

    @patch('staticpreprocessor.processors.get_files')
    def test_exclude_match(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseProcessor(exclude_match='*.txt')
        self.assertEqual(
            sorted(['/some/handlebars/template.handlebars',
                    '/lots/of/less/css.less',
                    '/and/some/sassy/css.sass']),
            sorted(list(processor.get_file_list()))
        )

    @patch('staticpreprocessor.processors.get_files')
    def test_exclude_regex(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseProcessor(exclude_regex=r'.*\.txt$')
        self.assertEqual(
            sorted(['/some/handlebars/template.handlebars',
                    '/lots/of/less/css.less',
                    '/and/some/sassy/css.sass']),
            sorted(list(processor.get_file_list()))
        )

    @patch('staticpreprocessor.processors.get_files')
    def test_include_match(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseProcessor(include_match='*.txt')
        self.assertEqual(
            ['/path/to/some/file.txt'],
            sorted(list(processor.get_file_list()))
        )

    @patch('staticpreprocessor.processors.get_files')
    def test_include_regex(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseProcessor(include_regex=r'.*\.txt$')
        self.assertEqual(
            ['/path/to/some/file.txt'],
            sorted(list(processor.get_file_list()))
        )


class TestBaseListProcessor(TestCase):

    files = [
        '/path/to/some/file.txt',
        '/some/handlebars/template.handlebars',
        '/lots/of/less/css.less',
        '/and/some/sassy/css.sass',
    ]

    @patch('staticpreprocessor.processors.get_files')
    def test_handle_list(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseListProcessor(remove_processed_files=False)
        with patch.object(processor, 'handle_list') as handle_list:
            processor.handle()
            handle_list.assert_called_with(
                get_files.return_value, **{'remove_processed_files': False})

    @patch('staticpreprocessor.processors.get_files')
    def test_handle_list_deletes(self, get_files):
        get_files.return_value = (f for f in self.files)
        processor = BaseListProcessor(remove_processed_files=True)
        storage = MagicMock()
        processor.storage = storage
        with patch.object(processor, 'handle_list') as handle_list:
            processor.handle()
            handle_list.assert_called_with(
                get_files.return_value, **{'remove_processed_files': True})
            self.assertEqual(storage.delete.call_count, 4)


class TestBaseFileProcessor(TestCase):

    def test_handle_file(self):
        processor = BaseFileProcessor()
        with patch.object(processor, 'handle_file') as handle_file:
            kwargs = {'a': 1, 'b': 2}
            processor.handle_list(['/path/to/file.txt'], **kwargs)
            handle_file.assert_called_with('/path/to/file.txt', **kwargs)


class TestCommandProcessorMixin(TestCase):

    @patch('staticpreprocessor.processors.subprocess')
    def test_bails_on_no_input(self, subprocess):
        mixin = CommandProcessorMixin(require_input=True)
        mixin.run_command('')
        self.assertFalse(subprocess.call.called)

    def test_get_command(self):
        mixin = CommandProcessorMixin()
        mixin.command = 'cat {input} > {output}'
        command = mixin.get_command(
            input='/an/input/file.txt', output='output.txt')
        self.assertEqual(command, 'cat /an/input/file.txt > output.txt')

    @patch('staticpreprocessor.processors.subprocess')
    def test_run_command(self, subprocess):
        subprocess.call.return_value = 0
        storage = MagicMock()
        storage.path.side_effect = lambda f: os.path.join('/prefix/path/', f)
        mixin = CommandProcessorMixin(
            output='js/processed.js',
            command='cat {input} > {output}',
            storage=storage,
        )
        mixin.run_command('input.txt')
        subprocess.call.assert_called_with(
            ['cat', 'input.txt', '>', '/prefix/path/js/processed.js'])

    @patch('staticpreprocessor.processors.subprocess')
    def test_run_command_failure(self, subprocess):
        subprocess.call.return_value = 1
        mixin = CommandProcessorMixin(
            output='js/processed.js',
            command='cat {input} > {output}',
        )
        with self.assertRaises(RuntimeError):
            mixin.run_command('input.txt')


class TestCommandProcessors(TestCase):

    def test_handle_list(self):
        processor = CommandListProcessor()
        with patch.object(processor, 'run_command') as run_command:
            kwargs = {'a': 1, 'b': 2}
            processor.handle_list(['a.txt', 'b.js', 'c.css'], **kwargs)
            run_command.assert_called_with('a.txt b.js c.css', **kwargs)

    def test_handle_file(self):
        processor = CommandFileProcessor()
        with patch.object(processor, 'run_command') as run_command:
            kwargs = {'a': 1, 'b': 2}
            processor.handle_file('a.txt', **kwargs)
            run_command.assert_called_with('a.txt', **kwargs)


class TestStaticPreprocessorStorage(TestCase):

    def test_no_base_url(self):
        storage = StaticPreprocessorFileStorage()
        self.assertEqual(storage.base_url, None)

    def test_get_available_name_existing(self):
        storage = StaticPreprocessorFileStorage()
        with patch.object(storage, 'exists') as exists:
            with patch.object(storage, 'delete') as delete:
                exists.return_value = True
                ret = storage.get_available_name('file.txt')
                self.assertEqual(ret, 'file.txt')
                delete.assert_called_with('file.txt')

    def test_get_available_name_not_existing(self):
        storage = StaticPreprocessorFileStorage()
        with patch.object(storage, 'exists') as exists:
            with patch.object(storage, 'delete') as delete:
                exists.return_value = False
                ret = storage.get_available_name('file.txt')
                self.assertEqual(ret, 'file.txt')
                self.assertFalse(delete.called)


class TestContribProcessors(TestCase):

    def test_sass_get_command(self):
        processor = sass.SassProcessor(compass=True)
        self.assertEqual(
            processor.get_command(input='input', output='output'),
            'sass --no-cache --compass input output',
        )
        processor = sass.SassProcessor(compass=False)
        self.assertEqual(
            processor.get_command(input='input2', output='output2'),
            'sass --no-cache  input2 output2',
        )

    def test_less_get_command(self):
        processor = less.LessProcessor(compress=True)
        self.assertEqual(
            processor.get_command(input='input', output='output'),
            'lessc --compress input output',
        )
        processor = less.LessProcessor(compress=False)
        self.assertEqual(
            processor.get_command(input='input2', output='output2'),
            'lessc  input2 output2',
        )


class TestFindersExceptions(TestCase):

    @override_settings(
        STATIC_PREPROCESSOR_FINDERS=[
            'staticpreprocessor.finders.WrongFinder',
        ]
    )
    def test_wrong_class(self):
        with self.assertRaises(ImproperlyConfigured):
            list(get_finders())

    @override_settings(
        STATIC_PREPROCESSOR_FINDERS=[
            'staticpreprocessor.notfinders.FileSystemFinder',
        ]
    )
    def test_wrong_module(self):
        with self.assertRaises(ImproperlyConfigured):
            list(get_finders())

    @override_settings(
        STATIC_PREPROCESSOR_FINDERS=[
            'staticpreprocessor.processors.BaseProcessor',
        ]
    )
    def test_not_a_finder(self):
        with self.assertRaises(ImproperlyConfigured):
            list(get_finders())
