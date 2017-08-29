#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter database
    name:__sql__.py
    author:rabin
"""
from demeter.core import *
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


	def assgin(self, value, exp='=', logic='and'):
		self.add(value)
		self.exp(exp)
		self.logic(logic)
		return self

	def bind(self, value):
		self.bindValue = value
		return self

	def exp(self, value):
		if type(self.expValue) != list:
			self.expValue = []
		self.expValue.append(value)
		return self

	def logic(self, value):
		if type(self.logicValue) != list:
			self.logicValue = []
		self.logicValue.append(value)
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
		if not self.argv:
			self.argv = []
		self.argv.append(value)
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

class Counter(object):
	num = 0
	instance = None

	def __new__(cls, *args, **kwd):
		if Counter.instance is None:
			Counter.instance = object.__new__(cls, *args, **kwd)
		return Counter.instance

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
	instance = None
	def __new__(cls, *args, **kwd):
		if Sql.instance is None:
			Sql.instance = object.__new__(cls, *args, **kwd)
		return Sql.instance

	def __init__(self, type):
		self.type = type

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
			fields.append(key)
			if val.autoIncrement and self.type == 'postgresql':
				fields.append('SERIAL')
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
				fields.append('DEFAULT \'' + str(default) + '\'')

			if val.comment:
				if self.type == 'mysql':
					fields.append('COMMENT \'' + val.comment + '\'')
				else:
					comment[key] = val.comment

			fields = ' '.join(fields)
			create.append(fields)

		if primary:
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

		if comment:
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
				fields.append(key)

		fields = ','.join(fields)
		values = ','.join(values)
		sql = 'INSERT INTO ' + table + ' (' + fields + ') VALUES (' + values + ')'
		if self.type == 'postgresql':
			sql = sql + ' RETURNING id'
		return sql

	def update(self, table, args):
		fields = []
		for key in args['set']:
			fields.append(key + ' = %s')

		fields = ','.join(fields)
		sql = 'UPDATE ' + table + ' SET ' + fields + self.where(args['key'], args['fields'])
		return sql

	def delete(self, table, args):
		sql = 'DELETE FROM ' + table + self.where(args['fields'])
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
			result = logic + ' ' + key + ' ' + exp + ' ' + str(val)
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
			if self.type == 'mysql':
				result = ' LIMIT ' + value[0] + ',' + value[1]
			elif self.type == 'postgresql':
				result = ' LIMIT ' + value[1] + ' OFFSET ' + value[0]

		return result

