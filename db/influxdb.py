#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter database
    name:influxdb.py
    author:rabin
"""
from influxdb import InfluxDBClient

class Influxdb(object):
	instance = None
	def __new__(cls, *args, **kwd):
		if Influxdb.instance is None:
			Influxdb.instance = object.__new__(cls, *args, **kwd)
		return Influxdb.instance

	def __init__(self, config):
		self.connect = InfluxDBClient(config['host'], config['port'], config['username'], config['password'], config['dbname'])
		self.create(config['dbname'])

	def get(self):
		return self.connect

	def create(self, name):
		database = self.connect.get_list_database()
		self.connect.create_database(name)