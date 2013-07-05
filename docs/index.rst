.. django-staticpreprocessor documentation master file, created by
    sphinx-quickstart on Thu Jun  6 13:48:05 2013.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

django-staticpreprocessor
=========================

django-staticpreprocessor is a Django app to simplify the pre-processing of
static assets.

staticpreprocessor can be used for building assets such as less/sass/scss
files, and handlebars and other JS templates.

Static files needing pre-processing are collected, in a similar manner to 
Django's staticfiles collection process, into a pre-selected directory. They 
are then operated on by processors to generate the required files which will 
then be collected by collectstatic.

Contents
--------
.. toctree::
    :maxdepth: 2

    installation
    usage
    examples
