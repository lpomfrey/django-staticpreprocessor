Examples
========

In all the following examples the settings shown should be used in order to
have the :py:mod:`preprocess_static
<staticpreprocessor.management.commands>` command produce the desired result.

Compiling all sass stylesheets and handlebar templates
------------------------------------------------------

To compile all less files into ``styles.css`` and all handlebars templates
into ``handlebars_templates.js``:
::

    # settings.py
    import os

    STATIC_PREPROCESSOR_ROOT = os.path.join(
        os.path.dirname(__file__), 'processedstatic/')
    STATIC_PREPROCESSOR_FINDERS = [
        'staticpreprocessors.finders.AppDirectoriesFinder',
        'staticpreprocessors.finders.FileSystemFinder',
    ]
    STATIC_PREPROCESSOR_PROCESSORS = [
        'staticpreprocessor.contrib.processors.less.LessProcessor',
        'staticpreprocessor.contrib.processors.handlebars.HandlebarsProcessor',
    ]


Compiling Less files to multiple targets
----------------------------------------

To compile ``less/responsive.less`` to ``css/responsive.css`` and
``less/unresponsive.less`` to ``css/unresponsive.css``:
::

    # settings.py
    import os
    from staticpreprocessor.contrib.processors.less import LessProcessor

    STATIC_PREPROCESSOR_ROOT = os.path.join(
        os.path.dirname(__file__), 'processedstatic/')
    STATIC_PREPROCESSOR_FINDERS = [
        'staticpreprocessors.finders.AppDirectoriesFinder',
        'staticpreprocessors.finders.FileSystemFinder',
    ]
    STATIC_PREPROCESSOR_PROCESSORS = [
        LessProcessor(
            include_match='less/unresponsive.less',
            output='css/unresponsive.less'
        ),
        LessProcessor(
            include_match='less/responsive.less',
            output='css/responsive.css',
        )
    ]

Compiling multiple handlebar template groups
--------------------------------------------
To compile all templates in ``groupa`` directories into ``handlebar_groupa.js``
and all templates in ``groupb`` into ``handlebar_groupb.js``:
::

    # settings.py
    import os
    from staticpreprocessor.contrib.processors.handlebars import HandlebarsProcessor

    STATIC_PREPROCESSOR_ROOT = os.path.join(
        os.path.dirname(__file__), 'processedstatic/')
    STATIC_PREPROCESSOR_FINDERS = [
        'staticpreprocessors.finders.AppDirectoriesFinder',
        'staticpreprocessors.finders.FileSystemFinder',
    ]
    STATIC_PREPROCESSOR_PROCESSORS = [
        HandlebarsProcessor(
            include_regex=r'^groupa/.*',
            output='handlebar_groupa.js',
        ),
        HandlebarsProcessor(
            include_match='groupb/*',
            output='handlebar_groupb.js',
        )
    ]
