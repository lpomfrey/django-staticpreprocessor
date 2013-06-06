# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from staticpreprocessor.processors import CommandListProcessor


class HandlebarsProcessor(CommandListProcessor):

    command = 'handlebars {input} --output {output} '\
              '--known each --known if --known unless'
    extensions = ['.handlebars']
    output = 'handlebars_templates.js'
