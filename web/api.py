#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter init
    author:rabin
"""
import os
from demeter.core import *

def loadFile(path):
	files = os.listdir(path)
	result = []
	for key in files:
		if '.DS_Store' not in key and  '__' not in key and 'pyc' not in key:
			key = key.replace('.py', '')
			result.append(key)
	return result

def loadUrl(module, key, url):
	str = dir(module)
	for i in str:
		act = ''
		if '_path' in i:
			act = i.replace('_path', '')
		if '_html' in i:
			act = i.replace('_html', '.html')
		if act:
			attr = getattr(module, i)
			if key == 'main' and act == 'index':
				url.append((r'/', attr))
			elif key == act:
				url.append((r'/'+act, attr))
			url.append((r'/'+key+'/'+act, attr))
	return url