# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from optparse import make_option

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.core.management.base import CommandError, NoArgsCommand
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_text
from django.utils.importlib import import_module
from django.utils.six import string_types
from django.utils.six.moves import input

from staticpreprocessor import finders, storage, conf, processors


class Command(NoArgsCommand):
    '''
    Command that allows copies static files to be preprocessed from different
    locations to the settings.STATIC_PREPROCESSOR_ROOT and preprocesses them.
    '''

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--noinput',
            action='store_false', dest='interactive', default=True,
            help='Do NOT prompt the user for input of any kind.'),
        make_option(
            '-c', '--clear',
            action='store_true', dest='clear', default=True,
            help='Clear the existing files using the storage '
                 'before trying to copy or link the original file.'),
        make_option(
            '-C', '--no-clear',
            action='store_false', dest='clear', default=True,
            help='DO NOT clear the existing files using the storage '
                 'before trying to copy or link the original file.'),
    )
    help = 'Precompile static files'
    requires_model_validation = True

    def __init__(self, *args, **kwargs):
        super(NoArgsCommand, self).__init__(*args, **kwargs)
        self.copied_files = []
        self.storage = storage.default_storage
        try:
            self.storage.path('')
        except NotImplementedError:
            self.local = False
        else:
            self.local = True

    def set_options(self, **options):
        '''
        Set instance variables based on an options dict
        '''
        self.interactive = options['interactive']
        self.verbosity = int(options.get('verbosity', 1))
        self.clear = options['clear']

    def collect(self):
        '''
        Collects the files into the STATIC_PREPROCESSOR_ROOT directory.
        '''

        if self.clear:
            self.clear_dir('')

        found_files = SortedDict()
        for finder in finders.get_finders():
            for path, storage in finder.list([]):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in found_files:
                    found_files[prefixed_path] = (storage, path)
                    self.copy_file(path, prefixed_path, storage)

        return self.copied_files

    def get_processors(self):
        pre_processors = []
        for processor in conf.settings.STATIC_PREPROCESSOR_PROCESSORS:
            if isinstance(processor, processors.BaseProcessor):
                pre_processors.append(processor)
            elif isinstance(processor, type) and \
                    issubclass(processor, processors.BaseProcessor):
                pre_processors.append(processor())
            elif isinstance(processor, (tuple, list) + string_types):
                try:
                    if isinstance(processor, (tuple, list)):
                        klass, kwargs = processor[0], processor[1]
                    else:
                        klass, kwargs = processor, {}
                    module, attr = klass.rsplit('.', 1)
                    module = import_module(module)
                    pre_processors.append(getattr(module, attr)(**kwargs))
                except (IndexError, TypeError, ValueError,
                        ImportError, AttributeError):
                    raise ImproperlyConfigured(
                        '"{0}" is an invalid preprocessor'.format(processor))
        return pre_processors

    def handle_noargs(self, **options):
        self.set_options(**options)
        # Warn before doing anything more.
        if (isinstance(self.storage, FileSystemStorage) and
                self.storage.location):
            destination_path = self.storage.location
            destination_display = ':\n\n {0}'.format(destination_path)
        else:
            destination_path = None
            destination_display = '.'

        if self.clear:
            clear_display = 'This will DELETE EXISTING FILES!'
        else:
            clear_display = 'This will overwrite existing files!'

        if self.interactive:  # pragma: no cover
            confirm = input('''
You have requested to precompile static files at the
destination location as specified in your settings{0}

{1}
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: '''.format(
                destination_display, clear_display)
            )
            if confirm != 'yes':
                raise CommandError('Collecting static files cancelled.')

        collected = self.collect()
        self.log(
            'Collected {0} file(s) for processing...\n'
            .format(len(collected)),
            level=1
        )
        for processor in self.get_processors():
            self.log(
                'Running processor: {0}\n'.format(
                    processor.__class__.__name__),
                level=1
            )
            processor.handle()
            self.log(
                'Finished running processor: {0}'.format(
                    processor.__class__.__name__),
                level=2
            )
        self.log('Completed pre-processing static files.\n', level=1)
        if destination_path:
            self.log(
                'Results are in{0}'.format(destination_display),
                level=1
            )

    def log(self, msg, level=2):
        '''
        Small log helper
        '''
        if self.verbosity >= level:
            self.stdout.write(msg)

    def clear_dir(self, path):
        '''
        Deletes the given relative path using the destination storage backend.
        '''
        dirs, files = self.storage.listdir(path)
        for f in files:
            fpath = os.path.join(path, f)
            self.log('Deleting "{0}"'.format(smart_text(fpath)), level=1)
            self.storage.delete(fpath)
        for d in dirs:
            self.clear_dir(os.path.join(path, d))

    def copy_file(self, path, prefixed_path, source_storage):
        '''
        Attempt to copy ``path`` with storage
        '''
        if self.storage.exists(prefixed_path):
            self.log('Deleting existing "{0}"'.format(prefixed_path), level=2)
            self.storage.delete(prefixed_path)
        source_path = source_storage.path(path)
        self.log('Copying "{0}"'.format(source_path), level=1)
        if self.local:
            full_path = self.storage.path(prefixed_path)
            try:
                os.makedirs(os.path.dirname(full_path))
            except OSError:
                pass
        with source_storage.open(path) as source_file:
            self.storage.save(prefixed_path, source_file)
        if not prefixed_path in self.copied_files:
            self.copied_files.append(prefixed_path)
