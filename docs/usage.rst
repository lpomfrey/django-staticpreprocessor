Usage
=====

Add ``staticpreprocessor`` to your ``INSTALLED_APPS``.

Create a directory to hold your pre-compiled static assets, set the
``STATIC_PREPROCESSOR_ROOT`` setting, add add it to ``STATICFILES_DIRS``:

::

    STATIC_PREPROCESSOR_ROOT = '/path/to/processedstatic/'
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

.. py:class:: FileSystemFinder

    Analagous to the similarly-named ``staticfiles`` finder, the
    ``FileSystemFinder`` collects all files from the directories named in the
    ``STATIC_PREPROCESSOR_DIRS`` setting.

.. py:class:: AppDirectoriesFinder

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

Processors are the classes that do the actual work of pre-processing your
static files.

Processors can be specified in the ``STATIC_PREPROCESSORS_PROCESSORS`` setting
as either dotted-paths, or otherwise, e.g.:
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

.. py:class:: BaseProcessor

    This is the base processor implementation that defines the most basic
    functionality of a processor, namely, the following methods:

    .. py:method:: get_file_list(self, \**kwargs)
    
        Returns the list of files to be operated on by the processor.
    
    .. py:method:: handle(self, \**kwargs)
    
        this is the main method that processes the static files.

    And the following attributes:
    
    .. py:attribute:: storage
    
        The storage class to use. Defaults to the default
        staticpreprocessor storage.

    .. py:attribute:: extensions

        The file extensions to target, e.g. ``.txt``, ``.css`` as a ``list`` 
        or ``tuple``. Setting to ``None`` will cause the processor to operate 
        on all file extensions
        
    .. py:attribute:: exclude_match

        A glob-type expression. Any files matching this pattern will be 
        excluded from processing by this processor.

    .. py:attribute:: exclude_regex

        An un-compiled regex string. Any files matching this pattern will be 
        excluded from processing by this processor.
        
    .. py:attribute:: include_match

        A glob-type expression. Any files *NOT* matching this pattern will be 
        excluded from processing by this processor.

    .. py:attribute:: include_regex

        An un-compiled regex string. Any files *NOT* matching this pattern will 
        be excluded from processing by this processor.

.. py:class:: BaseListProcessor

    ``BaseListProcessor`` extends :py:class:`BaseProcessor` and allows the
    entire collected file list to be processed using the ``handle_list``
    method.

    Methods:

    .. py:method:: handle_list(self, file_list, \** kwargs)

        ``file_list`` is the list of all files found to be handled in bulk.

    Attributes:

    .. py:attribute:: remove_processed_files

        If this is ``True`` (the default), the processor will remove the
        processed files after processing.

.. py:class:: BaseFileProcessor

    ``BaseFileProcessor`` extends 
    :py:class:`BaseListProcessor`, with the ``handle_file`` method being called 
    once for every file in the collected file list.

    Methods:

    .. py:method:: handle_file(self, file, \**kwargs)

        Is repeatedly called, with ``file`` being a single file from the
        collected file list.

    Attributes:

    .. py:attribute:: remove_processed_files

        If this is ``True`` (the default), the processor will remove the
        processed files after processing.

.. py:class:: CommandProcessorMixin

    The ``CommandProcessorMixin`` provides command running functionality via
    the `envoy <http://github.com/kennethreitz/envoy>`_ package.

    Methods:

    .. py:method:: get_command(self, \**kwargs)
    
        Returns the command to be run. By default this is 
        the :py:attr:`command` attribute formatted with \**kwargs. \**kwargs 
        contains any keyword arguments passed to the class, along with `input` 
        which is generally the space-separated list of files to be operated on, 
        and `output` which is the :py:attr:`output` attribute passed through 
        the class' storage `path` method.

    .. py:method:: run_command(self, input, \**kwargs)

        Runs the command returned by :py:meth:`get_command`.
        
        `input` should generally be a space separated list of files to be
        processed. 
        If :py:attr:`require_input` is `True`, the default, and input is empty 
        the command will not be run.

        If the return value of the command run is not in the 
        list :py:attr:`expected_return_codes` then this method will raise 
        `RuntimeError`.

    Attributes:

    .. py:attribute:: command

        The command line string to be run. By default this will be formatted by
        the :py:meth:`get_command` method so string formatting sequences can be 
        used, e.g.: ``cat {input} > {output}``.

    .. py:attribute:: output
        
        A path to an output file. This will be passed through ``storage.path`` 
        so it may be relative to ``STATIC_PREPROCESSOR_ROOT``.

    .. py:attribute:: expected_return_codes

        A list of return codes that are acceptable for the run process to
        return. Defaults to ``[0]``.

    .. py:attribute:: require_input

        Whether or not we should require input in order to run the command.
        Defaults to ``True``.

.. py:class:: CommandListProcessor

    Extends :py:class:`BaseListProcessor` and
    :py:class:`CommandProcessorMixin`. The specified command is run with
    `input` being the space-separated list of filenames generated by
    :py:meth:`get_file_list`.


.. py:class:: CommandFileProcessor

    Extends :py:class:`BaseListProcessor` and
    :py:class:`CommandProcessorMixin`. The specified command is run on each
    filename generated by :py:meth:`get_file_list` in turn, with `input` being
    the filename.

All attributes on processor classes are overridden by any keyword arguments
passed to ``__init__``.

Contrib Processors
~~~~~~~~~~~~~~~~~~

There are several processors included in the 
``staticpreprocessor.contrib.processors`` module.

.. py:class:: staticpreprocessor.contrib.processors.handlebars.HandlebarsProcessor

    Processes all ``.handlebars`` files into ``handlebars_templates.js``.
