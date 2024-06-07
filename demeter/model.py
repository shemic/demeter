# -*- coding: utf-8 -*-
"""
    demeter
    name:model.py
    author:rabin
"""
import os
import uuid
import short_url
import json
import traceback
import re
import math
import datetime
from demeter.core import *
class Model(object):
	__table__ = ''
	__comment__ = ''
	def __init__(self, type, db, config):
		self.db = db
		self._type = type
		self._config = config
		self._set = ''
		self._bind = {}
		self._attr = {}
		self._key = {}
		self.call = False
		self.log = []
		self.sql = False
		self.bind = False
		self.place = '%s'
		if self._type == 'sqlite':
			self.place = '?'
		self.setTable(self.__table__)
		self.create()

	def setTable(self, name):
		if 'prefix' in self._config and self._config['prefix']:
			self._table = self._config['prefix'] + '_' + name
		else:
			self._table = name

	def setCall(self, call):
		self.call = call
		return self

	def addLog(self, value):
		self.log.append(value)

	def getLog(self):
		return self.log

	def cur(self):
		return self.db.cursor()

	def commit(self):
		return self.db.commit()

	def lastId(self, cur):
		if hasattr(cur, 'lastrowid'):
			id = cur.lastrowid
			if not id:
				id = cur.fetchone()[0]
		else:
			id = cur.fetchone()[0]
		return id

	def query(self, sql, bind=[], fetch='fetchone', method='', cur=False, call=False):
		if call:
			self.setCall(call)
		if not cur:
			cur = self.cur()
		if not method:
			if 'select' in sql:
				method = 'select'
			if 'insert' in sql:
				method = 'insert'
		self.sql = sql
		self.bind = bind
		self.addLog((sql, bind))
		try:
			cur.execute(sql, bind)
			if method == 'select':
				return self.fetch(cur, fetch)
			id = True
			if method == 'insert':
				id = self.lastId(cur)
				Demeter.sync(self._table, id)
			if method == 'update' and 'id' in self._bind:
				Demeter.sync(self._table, self._bind['id'])
				
			self.commit()
		except Exception as e:
			self.addLog(str(e))
			return False
		self._set = {}
		return id

	def execute(self, sql, method='select', fetch='fetchall'):
		cur = self.cur()
		bind = []
		state_true = True
		state_false = False
		if self._type == 'mysql':
			state_true = '1'
			state_false = '2'
		if self._set:
			for key in self._set:
				self.check(key, self._set[key], self._attr[key])
				if self._set[key] == 'time':
					self._set[key] = self.time()
				elif self._set[key] == 'True':
					self._set[key] = state_true
				elif self._set[key] == 'False':
					self._set[key] = state_false
				elif 'date' in key and type(self._set[key]) != int:
					self._set[key] = self.mktime(self._set[key])
				elif self._attr[key].md5:
					self._set[key] = self.createMd5(self._set[key])
				bind.append(self._set[key])
		for value in self._key:
			if value[0] in self._bind and self._bind[value[0]] != None:
				val = self._bind[value[0]]
				if method == 'insert':
					self.check(value[0], val, self._attr[value[0]])
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
			Demeter.config['page']['total'] = int(math.ceil(round(float(Demeter.config['page']['totalNum'])/float(Demeter.config['page']['num']),2)))
		elif ';' in sql:
			temp = sql.split(';')
			result = []
			for v in temp:
				result.append(self.query(v, (), fetch=fetch, method=method, cur=cur))
			return result
		return self.query(sql, bind, fetch=fetch, method=method, cur=cur)

	def fetchAll(self):
		return self.fetch(self.cur(), type='fetchall')

	def fetch(self, cur, type='fetchall', method = ''):
		load = getattr(cur, type)
		rows = load()
		desc = self._key
		desc = cur.description
		if type == 'fetchall':
			result = []
			if rows:
				for key in rows:
					row = {}
					i = 0
					for v in key:
						row[desc[i][0]] = self.data(desc[i][0], v)
						i = i + 1
					result.append(row)
		elif method == 'count':
			return rows[0]
		else:
			result = {}
			i = 0
			if rows:
				for v in rows:
					if not v:
						v = ''
					result[desc[i][0]] = self.data(desc[i][0], v)
					i = i + 1
		return result

	def data(self, key, value):
		if type(value) == datetime.datetime:
			value = str(value)
		if self.call:
			value = self.call(key, value)
		if value == None or not value:
			value = ''
		return value

	def attr(self, method):
		fields = vars(self.__class__)
		self._attr = {}
		self._bind = {}
		self._key = {}

		if Demeter.checkPy3():
			col = (int, str, float, bool, uuid.UUID)
			code = (str,)
		else:
			col = (int, str, long, float, unicode, bool, uuid.UUID)
			code = (str, unicode)
		for field in fields:
			if isinstance(fields[field], Fields):
				self._attr[field] = fields[field]
				self._key[field] = self._attr[field].getKey()
				insert = (method == 'insert')
				update = (insert or method == 'update')
				if insert and self._attr[field].uuid:
					self.setUuid(field, col)
				bind = False
				val = self._attr[field].getArgv()
				if val or val == False:
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
				if bind and val != None:
					if type(val) == list:
						length = len(val)
						if length <= 1:
							val = val[0]
					if insert and self._attr[field].md5:
						val = self.createMd5(val)
					if self._attr[field].type == 'boolean' and isinstance(val, code):
						val = Demeter.bool(val, self._type)
					if type(val) == list:
						val = tuple(val)
					self._bind[field] = val
					self._attr[field].val(self._bind[field])
					self._attr[field].bind(self.place)

		self._key = sorted(self._key.items(), key=lambda d:d[1], reverse = False)
		Counter().unset()

	def check(self, field, val, attr):
		if val == 'undefined':
			self.error(error)
		if attr.match == 'not':
			if not val:
				self.error(field + ' not exists')
		elif attr.match:
			if '|' in attr.match:
				temp = attr.match.split('|')
				match = temp[0]
				error = temp[1]
			else:
				match = attr.match
				error = field + ' not match:' + match
			if hasattr(Check, match):
				method = getattr(Check, match)
				result = method(val)
			else:
				result = re.search(match, val)
			if not result:
				self.error(error)

	def error(self, msg):
		for value in self._key:
			if value[0] in self._bind and self._bind[value[0]] != None:
				self._attr[value[0]].unset()
		self._set = {}
		Demeter.error(msg)

	def time(self):
		return Demeter.time()

	def mktime(self, value):
		return Demeter.mktime(value)

	def setUuid(self, field, col):
		id = getattr(self, self._attr[field].uuid)
		if isinstance(id, col):
			system = short_url.encode_url(id)
		else:
			system = self._attr[field].uuid
		name = system + '.' + self.__table__
		result = Demeter.uuid(name)
		setattr(self, field, result)

	def createMd5(self, value):
		if 'db_md5' in Demeter.config and Demeter.config['db_md5'] == 1:
			Demeter.config['db_md5'] = 2
			return value
		else:
			return Demeter.md5(value, salt=True)

	def createState(self):
		if 'create' in self._config:
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

	def select(self, type='fetchall',col = '*', order = 'cdate desc', group = '', limit = '0,100', page=False, call=False):
		if call:
			self.setCall(call)
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
		load = getattr(Sql(self._type, self.place), method)
		return self.execute(load(self._table, {'key':self._key, 'fields':self._attr, 'col':col, 'order':order, 'group':group, 'limit':limit, 'page':page, 'set':set, 'table_comment':self.__comment__}), method, type)


class Fields(object):
	def __init__(self, type='', default='', primaryKey=False, autoIncrement=False, null=True, unique=False, check='', constraint='', comment='', uuid='', index=False, indexs=False, md5=False, match='', manage=''):
		self.type = type
		self.default = default
		self.primaryKey = primaryKey
		self.autoIncrement = autoIncrement
		self.null = null
		self.unique = unique
		self.check = check
		self.constraint = constraint
		self.comment = comment
		self.uuid = uuid
		self.index = index
		self.indexs = indexs
		self.md5 = md5
		self.key = Counter().inc()
		self.match = match
		self.value = ''
		self.argv = ''
		self.bindValue = ''
		self.expValue = '='
		self.logicValue = 'and'
		self.manage = manage


	# set value
	def assign(self, value, exp='=', logic='and'):
		self.add(value)
		self.exp(exp)
		self.logic(logic)
		return self

	def ins(self, value):
		self.argv = value
		self.exp('in')
		return self

	def nq(self, value):
		self.argv = value
		self.exp('!=')
		return self

	def like(self, value):
		self.argv = '%' + value + '%'
		self.exp('like')
		return self

	def mlike(self, value):
		self.argv = value
		self.exp('~')
		self.logic('and')
		return self

	def time(self, value):
		self.add(Demeter.mktime(value))
		return self

	def start(self, value):
		self.time(value)
		self.exp('>=')
		self.logic('and')
		return self

	def end(self, value):
		self.time(value)
		self.exp('<=')
		self.logic('and')
		return self



	def bind(self, value):
		self.bindValue = value
		return self

	def exp(self, value):
		"""
		if type(self.expValue) != list:
			self.expValue = []
		self.expValue.append(value)
		"""
		self.expValue = value
		return self

	def logic(self, value):
		"""
		if type(self.logicValue) != list:
			self.logicValue = []
		self.logicValue.append(value)
		"""
		self.logicValue = value
		return self

	def val(self, value, exp='=', logic='and'):
		if type(value) == list:
			length = len(value)
			if length <= 1:
				value = value[0]
		self.value = value
		if not self.expValue:
			self.exp(exp)
		if not self.logicValue:
			self.logic(logic)
		return self

	def getArgv(self):
		return self.argv

	def getVal(self):
		return self.value

	def getBind(self):
		return self.bindValue

	def getExp(self):
		if not self.expValue:
			return ''
		if type(self.expValue) == list:
			length = len(self.expValue)
			if length <= 1:
				result = self.expValue[0]
			else:
				result = self.expValue
		else:
			result = self.expValue
		return result

	def getKey(self):
		return self.key

	def getLogic(self):
		if not self.logicValue:
			return ''
		if type(self.logicValue) == list:
			length = len(self.logicValue)
			if length <= 1:
				result = self.logicValue[0]
			else:
				result = self.logicValue
		else:
			result = self.logicValue
		return result

	def unset(self):
		self.argv = None
		self.value = None
		self.bindValue = None
		self.expValue = '='
		self.logicValue = 'and'
		return self

	def add(self, value):
		"""
		if not self.argv:
			self.argv = []
		self.argv.append(value)
		"""
		self.argv = value
		return self

class Counter(object):
	num = 0
	"""
	instance = None

	def __new__(cls, *args, **kwd):
		if Counter.instance is None:
			Counter.instance = object.__new__(cls, *args, **kwd)
		return Counter.instance
	"""
	def inc(self):
		self.num = self.num + 1
		return self.num

	def dec(self):
		self.num = self.num - 1
		return self.num

	def unset(self):
		self.num = 0
		return self.num

class Sql(object):
	"""
	instance = None
	def __new__(cls, *args, **kwd):
		if Sql.instance is None:
			Sql.instance = object.__new__(cls, *args, **kwd)
		return Sql.instance
	"""

	def __init__(self, type, place):
		self.type = type
		self.place = place
		self.prefix = '`'
		if self.type == 'postgresql':
			self.prefix = ''

	def drop(self, table, args):
		sql = 'DROP TABLE IF EXISTS ' + table
		return sql

	def alter(self, table, args):
		sql = 'ALTER TABLE ' + table + ' ADD COLUMN '
		return sql

	def create(self, table, args):
		create = []
		primary = []
		unique = []
		indexs = []
		index = []
		comment = {}
		for value in args['key']:
			key = value[0]
			val = args['fields'][key]
			if val.primaryKey:
				primary.append(key)
			if val.unique:
				unique.append(key)
			if val.index:
				index.append((key, val.index))
			if val.indexs:
				indexs.append(key)

			fields = []
			fields.append(self.prefix + key + self.prefix)
			if val.autoIncrement and self.type == 'postgresql':
				fields.append('SERIAL')
			elif self.type == 'mysql' and val.type == 'boolean':
				fields.append('int')
			elif self.type == 'sqlite' and val.type == 'int':
				if val.autoIncrement and val.primaryKey:
					fields.append('integer PRIMARY KEY autoincrement')
				else:
					fields.append('integer')
			else:
				fields.append(val.type)

			if not val.null:
				fields.append('NOT NULL')
				

			if val.autoIncrement and self.type == 'mysql':
				fields.append('AUTO_INCREMENT')

			#约束
			if val.constraint:
				fields.append('CONSTRAINT ' + val.constraint)
			if val.check:
				fields.append('CHECK ' + val.check)
			
			if val.default:
				default = val.default
				if val.default == 'time':
					default = '0'
				if '.' in val.default:
					temp = val.default.split('.')
					default = Demeter.config[temp[0]][temp[1]]
				if self.type == 'mysql' and val.type == 'boolean':
					default = Demeter.bool(default, self.type)
				fields.append('DEFAULT \'' + str(default) + '\'')

			if val.comment:
				if self.type == 'mysql':
					fields.append('COMMENT \'' + val.comment + '\'')
				else:
					comment[key] = val.comment

			fields = ' '.join(fields)
			create.append(fields)

		if primary and self.type != 'sqlite':
			create.append('PRIMARY KEY (' + ','.join(primary) + ')')
		if unique:
			create.append('UNIQUE (' + ','.join(unique) + ')')

		create = ','.join(create)
		sql = 'CREATE TABLE ' + table + '(' + create + ')'
		sql = self.drop(table, args) + ';' + sql
		if indexs:
			name = '_'.join(indexs)
			value = ','.join(indexs)
			sql = sql + ';' + 'CREATE INDEX ' + table + '_' + name +' ON ' + table + '(' + value + ')'

		if index:
			for value in index:
				sql = sql + ';' + 'CREATE INDEX ' + table + '_' + value[0] +' ON ' + table + value[1]

		if comment and self.type != 'sqlite':
			if args['table_comment']:
				sql = sql + ';' + 'COMMENT ON TABLE ' + table + ' IS \''+args['table_comment']+'\''
			for key in comment:
				sql = sql + ';' + 'COMMENT ON COLUMN ' + table + '.'+key+' IS \''+comment[key]+'\''
		return sql

	def insert(self, table, args):
		fields = []
		values = []
		for value in args['key']:
			key = value[0]
			val = args['fields'][key].getBind()
			if val:
				values.append(val)
				fields.append(self.prefix + key + self.prefix)

		fields = ','.join(fields)
		values = ','.join(values)
		sql = 'INSERT INTO ' + table + ' (' + fields + ') VALUES (' + values + ')'
		if self.type == 'postgresql':
			sql = sql + ' RETURNING id'
		return sql

	def update(self, table, args):
		fields = []
		for key in args['set']:
			fields.append(self.prefix + key + self.prefix + ' = ' + self.place)

		fields = ','.join(fields)
		sql = 'UPDATE ' + table + ' SET ' + fields + self.where(args['key'], args['fields'])
		return sql

	def delete(self, table, args):
		sql = 'DELETE FROM ' + table + self.where(args['key'], args['fields'])
		return sql

	def select(self, table, args):
		string = ' FROM ' + table + self.where(args['key'], args['fields']) + ' ' + self.group(args['group'])
		sql = ''
		if args['page']:
			sql = 'SELECT count(1) as total' + string + ';'
		sql = sql + 'SELECT ' + args['col'] + string + ' ' + self.order(args['order']) + ' ' + self.limit(args['limit'], args['page'])
		return sql

	def where(self, key, fields):
		fields = self.fields(key, fields)
		if fields:
			return ' WHERE ' + fields
		return ''

	def fields(self, key, fields):
		result = ''
		k = 0
		for value in key:
			key = value[0]
			field = fields[key]
			bind = field.getBind()
			val = field.getVal()
			logic = field.getLogic()
			exp = field.getExp()
			if type(val) == list and val:
				n = 0
				for i in val:
					data = self.field(field, bind, key, k, logic[n], exp[n])
					n = n + 1
					if data:
						result = result + data
						k = 1
			else:
				data = self.field(field, bind, key, k, logic, exp)
				if data:
					result = result + data
					k = 1
		return result

	def field(self, field, val, key, k, logic, exp):
		result = ''
		if val:
			if k == 0:
				logic = ''
			else:
				logic = ' ' + logic
			result = logic + ' ' + self.prefix + key + self.prefix + ' ' + exp + ' ' + str(val)
		return result

	def order(self, value):
		result = ''
		if value:
			result = ' ORDER BY ' + value

		return result

	def group(self, value):
		result = ''
		if value:
			result = ' GROUP BY ' + value

		return result

	def limit(self, value, page):
		result = ''
		if page:
			value = str((int(page['current'])-1) * page['num']) + ',' + str(page['num'])
		if value:
			value = value.split(',')
			if self.type == 'postgresql':
				result = ' LIMIT ' + value[1] + ' OFFSET ' + value[0]
			else:
				result = ' LIMIT ' + value[0] + ',' + value[1]

		return result