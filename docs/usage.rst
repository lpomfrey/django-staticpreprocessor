Usage
=====

Add ``staticpreprocessor`` to your ``INSTALLED_APPS``.

Create a directory to hold your pre-compiled static assets, set the
``STATIC_PREPROCESSOR_ROOT`` setting, add add it to ``STATICFILES_DIRS``:

::

    STATIC_PREPROCESSOR_ROOT = '/path/to/rawstatic/'
    STATICFILES_DIRS = (
        ...
        STATIC_PREPROCESSOR_ROOT,
        ...
    )


Finders
-------
.. py:module:: staticpreprocessor.finders

Finders are exactly the same in concept as staticfiles finders.
``staticpreprocessor`` comes with several.

.. py:class:: staticpreprocessor.finders.FileSystemFinder

    Analagous to the similarly-named ``staticfiles`` finder, the
    ``FileSystemFinder`` collects all files from the directories named in the
    ``STATIC_PREPROCESSOR_DIRS`` setting.

.. py:class:: staticpreprocessor.finders.AppDirectoriesFinder

    Again, this is analagous to the ``AppDirectoriesFinder`` in staticfiles, 
    with the exception that rather than collecting files from the ``/static/``
    directory under each app, files are collected from ``/rawstatic/``.

In order to use the finders they should be added to the
``STATIC_PREPROCESSOR_FINDERS`` setting, e.g.:
::

    STATIC_PREPROCESSOR_DIRS = \
        os.path.join(os.path.dirname(__file__), 'rawstatic/')
    STATIC_PREPROCESSOR_FINDERS = (
        'staticpreprocessor.finders.FileSystemFinder',
        'staticpreprocessor.finders.AppDirectoriesFinder',
    )


Processors
----------
.. py:module:: staticpreprocessor.processors
.. py:module:: staticpreprocessor.contrib.processors

Processors are the classes that do the actual work of pre-processing your
static files.

Processors can be specified in the ``STATIC_PREPROCESSORS_PROCESSORS`` setting
as either dotted-paths, bare class, or instances classes. If specified as a
class instance variables can be passed in as arguments to the class, e.g.:
::

    from staticpreprocessor.contrib.processors.less import LessProcessor
    from staticpreprocessor.contrib.processors.sass import SassProcessor
    from staticpreprocessor.processors import CommandListProcessor
    STATIC_PREPROCESSOR_PROCESSORS = (
        'staticpreprocessor.contrib.processors.HandlebarsProcessor',
        LessProcessor,
        SassProcessor(),
        CommandListProcessor(
            extensions=['.txt'], command='echo {input} > {output}'),
    )


There are several base processor classes that can be extended and used:

.. py:class:: staticpreprocessor.processors.BaseProcessor

    This is the base processor implementation that defines the most basic
    functionality of a processor, namely, the following methods:

    .. py:method:: staticpreprocessor.processors.BaseProcessor.get_file_list(self, **kwargs)
    
        Returns the list of files to be operated on by the processor.
    
    .. py:method:: staticpreprocessor.processors.BaseProcessor.handle(self, **kwargs)
    
        this is the main method that processes the static files.

    And the following attributes:
    
    .. py:attribute:: staticpreprocessor.processors.BaseProcessor.storage
    
        The storage class to use. Defaults to the default
        staticpreprocessor storage.

:``extensions``: The file extensions to target, e.g. ``.txt``, ``.css`` as a
                 ``list`` or ``tuple``. Setting to ``None`` will cause the
                 processor to operate on all file extensions
:``exclude_match``: A glob-type expression. Any files matching this pattern
                    will be excluded from processing by this processor.
:``exclude_regex``: An un-compiled regex string. Any files matching this
                    pattern will be excluded from processing by this
                    processor.
:``include_match``: A glob-type expression. Any files *NOT* matching this 
                    pattern will be excluded from processing by this processor.
:``include_regex``: An un-compiled regex string. Any files *NOT* matching this
                    pattern will be excluded from processing by this
                    processor.

Included processors are in the ``staticpreprocessor.contrib.processors``
module.

.. py:class:: staticpreprocessor.contrib.processors.handlebars.HandlebarsProcessor

    This processor 
