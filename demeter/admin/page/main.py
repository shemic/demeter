# -*- coding: utf-8 -*-
"""
    demeter web page
    name:main.py
    author:rabin
"""
from .__load__ import *

class index_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.view("index.html")

class main_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.view("main.html")