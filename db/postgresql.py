#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter database
    name:postgresql.py
    author:rabin
"""
import psycopg2

class Postgresql(object):
	instance = None
	def __new__(cls, *args, **kwd):
		if Postgresql.instance is None:
			Postgresql.instance = object.__new__(cls, *args, **kwd)
		return Postgresql.instance
		
	def __init__(self, config):
		self.connect = psycopg2.connect(host=config['host'], port=config['port'], user=config['username'], password=config['password'], database=config['dbname'])

	def get(self):
		return self.connect

	def create(self, name):
		'psql -U postgres'
		sql = 'CREATE DATABASE '+name+' WITH OWNER = postgres ENCODING = "UTF8"'
		return sql