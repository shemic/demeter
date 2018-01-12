# -*- coding: utf-8 -*-
"""
    demeter web
    name:front.py
"""
from demeter.core import *

# 测试命令行传参 python opt.py -a act
param = {}
param['action'] = 'a'
param['name'] = 'n'
param['param'] = 'p'
Demeter.getopt(param)

Demeter.echo(Demeter.option['action'])