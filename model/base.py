#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter database
    name:__base__.py
    author:rabin
"""
import os
import uuid
import short_url
import json
import traceback
import uuid
import re
import math
from sql import *
from demeter.core import *
class Base(object):
	__table__ = ''
	__comment__ = ''
	def __init__(self, type, db, config):
		self.db = db
		self._type = type
		self._config = config
		self._table = self._config['prefix'] + '_' + self.__table__
		self._set = ''
		self._bind = {}
		self._attr = {}
		self._key = {}
		self.create()

	def cur(self):
		return self.db.cursor()

	def query(self, sql, method='select', fetch='fetchall'):
		cur = self.cur()
		bind = []
		if self._set:
			for key in self._set:
				if self._set[key] == 'time':
					self._set[key] = self.time()
				elif self._set[key] == 'True':
					self._set[key] = True
				elif self._set[key] == 'False':
					self._set[key] = False
				elif 'date' in key:
					self._set[key] = self.mktime(self._set[key])
				bind.append(self._set[key])
		for value in self._key:
			if value[0] in self._bind and self._bind[value[0]] != None:
				val = self._bind[value[0]]
				self._attr[value[0]].unset()
				if type(val) == list and val:
					for i in val:
						bind.append(i)
				else:
					bind.append(val)
		if method == 'select' and ';' in sql:
			temp = sql.split(';')
			sql = temp[1]
			totalSql = temp[0]
			cur.execute(totalSql, bind)
			Demeter.config['page']['totalNum'] = self.fetch(cur, 'fetchone', 'count')
			Demeter.config['page']['total'] = math.ceil(round(float(Demeter.config['page']['totalNum'])/float(Demeter.config['page']['num']),2))
		cur.execute(sql, bind)
		if method == 'select':
			return self.fetch(cur, fetch)
		id = True
		if method == 'insert':
			id = cur.fetchone()[0]
		self.db.commit()
		self._set = {}
		return id
		"""
		try:
			
		except Exception, e:
			print e.message
			os._exit(0)
		"""


	def fetch(self, cur, type, method = ''):
		load = getattr(cur, type)
		rows = load()
		if type == 'fetchall':
			result = []
			if rows:
				for key in rows:
					row = {}
					i = 0
					for v in key:
						row[self._key[i][0]] = v
						i = i + 1
					result.append(row)
		elif method == 'count':
			return rows[0]
		else:
			result = {}
			i = 0
			if rows:
				for key in rows:
					if not key:
						key = ''
					result[self._key[i][0]] = key
					i = i + 1
		return result

	def attr(self, method):
		fields = vars(self.__class__)
		self._attr = {}
		self._bind = {}
		self._key = {}
		col = (int, str, long, float, unicode, bool, uuid.UUID)
		for field in fields:
			if isinstance(fields[field], Fields):
				self._attr[field] = fields[field]
				self._key[field] = self._attr[field].getKey()
				insert = (method == 'insert')
				if insert and self._attr[field].uuid:
					self.setUuid(field, col)
				bind = False
				val = self._attr[field].getArgv()
				if val:
					bind = True
				else:
					val = getattr(self, field)
					if isinstance(val, col):
						setattr(self, field, self._attr[field])
						bind = True
					elif insert and self._attr[field].default:
						val = self._attr[field].default
						bind = True
						if val == 'time':
							val = self.time()
						elif '.' in val:
							temp = val.split('.')
							val = Demeter.config[temp[0]][temp[1]]
					elif method == 'select' and self._attr[field].default and field == 'state':
						val = self._attr[field].default
						bind = True
				if bind and val:
					if type(val) == list:
						length = len(val)
						if length <= 1:
							val = val[0]
					if insert and self._attr[field].md5:
						val = self.createMd5(val)
					if self._attr[field].type == 'boolean' and isinstance(val, (str, unicode)):
						val = Demeter.bool(val)
					self.check(field, val, self._attr[field])
					self._bind[field] = val
					self._attr[field].val(self._bind[field])
					self._attr[field].bind('%s')

		self._key = sorted(self._key.items(), key=lambda d:d[1], reverse = False)
		Counter().unset()

	def check(self, field, val, attr):
		if attr.match == 'not':
			if not val:
				Demeter.error(field + ' not exists')
		elif attr.match:
			result = re.search(attr.match, val)
			if not result:
				Demeter.error(field + ' not match:' + attr.match)

	def time(self):
		module = __import__('time')
		time = getattr(module, 'time')
		return int(time())

	def mktime(self, value):
		return Demeter.mktime(value)

	def setUuid(self, field, col):
		id = getattr(self, self._attr[field].uuid)
		if isinstance(id, col):
			system = short_url.encode_url(id)
		else:
			system = self._attr[field].uuid
		name = system + '.' + self.__table__
		result = uuid.uuid5(uuid.uuid1(), name)
		result = str(result)
		setattr(self, field, result)

	def createMd5(self, value):
		return Demeter.md5(value, salt=True)

	def createState(self):
		create = Demeter.bool(self._config['create'])
		if create:
			return Demeter.runtime(self._type, self.__table__, json.dumps(self._key))
		return False

	def drop(self):
		return self.handle('drop')

	def create(self):
		return self.handle('create')

	def insert(self):
		return self.handle('insert')

	def update(self, *args, **kwargs):
		if args:
			self._set = args[0]
		else:
			self._set = kwargs
		return self.handle('update', set=self._set)

	def delete(self):
		return self.handle('delete')

	def select(self, type='fetchall',col = '*', order = 'cdate desc', group = '', limit = '0,100', page=False):
		pageConfig = {}
		if page and 'page' in Demeter.config:
			pageConfig['current'] = Demeter.config['page']['current']
			if page == True:
				pageConfig['num'] = 15
			elif 'num' in page:
				pageConfig['num'] = page['num']
			Demeter.config['page']['num'] = pageConfig['num']
		return self.handle('select', type=type, col=col, order=order, group=group, limit=limit, page=pageConfig)

	def manage(self):
		self.attr(method)
		return

	def handle(self, method='select', type='fetchall', col = '*', order = '', group = '', limit = '0,100', page=False, set = ''):
		self.attr(method)
		if method == 'create':
			create = self.createState()
			if create == False:
				return False
		if type == 'fetchone':
			limit = '0,1'
		load = getattr(Sql(self._type), method)
		return self.query(load(self._table, {'key':self._key, 'fields':self._attr, 'col':col, 'order':order, 'group':group, 'limit':limit, 'page':page, 'set':set, 'table_comment':self.__comment__}), method, type)