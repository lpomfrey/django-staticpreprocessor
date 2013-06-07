# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from staticpreprocessor.processors import CommandListProcessor


class SassProcessor(CommandListProcessor):

    compass = False
    extensions = ['.sass', '.scss']
    output = 'sass_styles.css'

    def get_command(self, **kwargs):
        return 'sass --no-cache {compass_string} {input} {output}'.format(
            compass_string='--compass' if self.compass else '', **kwargs)
