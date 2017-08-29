#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter mqtt
    name:sub.py
    author:rabin
"""
from connect import Connect

class Sub(object):

	def __init__(self):
		Connect(self)

	def __del__(self):
		pass

	def message(self, client, userdata, msg):
		#print(msg.topic+" "+str(msg.payload))
		self.connect.handle(msg.topic, str(msg.payload))