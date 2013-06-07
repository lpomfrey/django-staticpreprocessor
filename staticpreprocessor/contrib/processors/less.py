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
        return 'lessc --silent {compress_string} {yui_compress_string} '\
            '{optimization_string} {input} {output}'.format(
                compress_string='--compress' if self.compress else '',
                yui_compress_string='--yui-compress'
                if self.yui_compress else '',
                optimization_string='-O{0}'.format(self.optimization)
                if self.optimization is not None else '',
                **kwargs
            )
