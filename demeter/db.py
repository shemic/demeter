# -*- coding: utf-8 -*-
"""
    demeter
    name:db.py
    author:rabin
"""
from demeter.core import *
class Influxdb(object):
	"""
	instance = None
	def __new__(cls, *args, **kwd):
		if Influxdb.instance is None:
			Influxdb.instance = object.__new__(cls, *args, **kwd)
		return Influxdb.instance
	"""

	def __init__(self, config):
		influxdb = __import__('influxdb')
		InfluxDBClient = getattr(influxdb, 'InfluxDBClient')
		self.connect = InfluxDBClient(config['host'], config['port'], config['username'], config['password'], config['dbname'])
		self.create(config['dbname'])

	def get(self):
		return self.connect

	def create(self, name):
		database = self.connect.get_list_database()
		self.connect.create_database(name)


class Postgresql(object):
	"""
	instance = None
	def __new__(cls, *args, **kwd):
		if Postgresql.instance is None:
			Postgresql.instance = object.__new__(cls, *args, **kwd)
		return Postgresql.instance
	"""
	def __init__(self, config):
		psycopg2 = __import__('psycopg2')
		self.create(config['dbname'])
		self.connect = psycopg2.connect(host=config['host'], port=config['port'], user=config['username'], password=config['password'], database=config['dbname'])

	def get(self):
		return self.connect

	def create(self, name):
		'psql -U postgres'
		sql = 'CREATE DATABASE '+name+' WITH OWNER = postgres ENCODING = "UTF8"'

		if Demeter.runtime('postgresql', name, sql):
			Shell.popen('createdb -h localhost -p 5432 -U postgres ' + name)
		return True

class Mysql(object):
	"""
	instance = None
	def __new__(cls, *args, **kwd):
		if Mysql.instance is None:
			Mysql.instance = object.__new__(cls, *args, **kwd)
		return Mysql.instance
	"""
	def __init__(self, config):
		pymysql = __import__('pymysql')
		self.connect = pymysql.connect(host=config['host'], port=int(config['port']), user=config['username'], password=config['password'], database=config['dbname'], charset=config['charset'])

	def get(self):
		return self.connect

	def create(self, name):
		sql = 'CREATE DATABASE IF NOT EXISTS '+name+' DEFAULT CHARSET utf8 COLLATE utf8_general_ci'
		if not Demeter.runtime('mysql', name, sql):
			self.connect.cursor().execute(sql)
		return sql

class Sqlite(object):
	"""
	instance = None
	def __new__(cls, *args, **kwd):
		if Sqlite.instance is None:
			Sqlite.instance = object.__new__(cls, *args, **kwd)
		return Sqlite.instance
	"""
	def __init__(self, config):
		sqlite3 = __import__('sqlite3')
		self.connect = sqlite3.connect(config['file'])
		# 插入中文问题
		self.connect.text_factory = str

	def get(self):
		return self.connect

	def create(self, name):
		sql = 'CREATE DATABASE IF NOT EXISTS '+name+' DEFAULT CHARSET utf8 COLLATE utf8_general_ci'
		if not Demeter.runtime('sqlite', name, sql):
			self.connect.cursor().execute(sql)
		return sql