#!/usr/bin/env python

"""
__version__ = '1.0.0'
__date__ = '2020-01-01'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import configparser
from pathlib import Path

blockchain_conf = Path(__file__).parent.parent.joinpath('config/blockchain.conf')


def get_value_str(section, option):
    config = configparser.ConfigParser()
    config.read(blockchain_conf)
    value = config.get(section, option)
    return value


def get_value_int(section, option):
    config = configparser.ConfigParser()
    config.read(blockchain_conf)
    value = config.getint(section, option)
    return value
