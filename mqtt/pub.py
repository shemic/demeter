#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter mqtt
    name:pub.py
    author:rabin
"""
from connect import Connect

class Pub(object):

	def __init__(self):
		Connect(self)

	def __del__(self):
		pass

	def push(self, key, msg):
		self.connect.getClient().publish(key,msg)