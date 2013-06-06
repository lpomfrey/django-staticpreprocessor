Installation
============

You can grab django-staticpreprocessor from PyPI:

::

    $ pip install django-staticpreprocessor

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
