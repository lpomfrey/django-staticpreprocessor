# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from staticpreprocessor.processors import CommandListProcessor


class LessProcessor(CommandListProcessor):

    compress = True
    yui_compress = False
    optimization = None
    extensions = ['.less']
    output = 'less_styles.css'

    def get_command(self, **kwargs):
        return 'lessc {compress_string} {input} {output}'.format(
            compress_string='--compress' if self.compress else '',
            **kwargs
        )
