#!/usr/bin/env python

"""
__version__ = '2.0.0'
__date__ = '2019-12-31'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

from modules.views import app
from modules import config

host = config.get_value_str('blockchain', 'host')
port = config.get_value_int('blockchain', 'port')


if __name__ == '__main__':
    app.run(host, port)
