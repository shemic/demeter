#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter service
    name:service.py 通用业务
    author:rabin
"""
from demeter.core import *

class Service(object):

	# 获取某个model下的列表数据
	def list(self, name, state = True, search=None, page=False, order='cdate desc', limit = '0,100'):
		model = self.model(name)
		model.state = state
		if search:
			for key, value in search.items():
				if value != None:
					if '-' in key:
						key = key.split('-')
						keyLen = len(key)
						if keyLen > 2 and key[2]:
							method = key[2]
						else:
							method = 'assgin'
						self.assgin(model, key[0], value, method)
					else:
						self.assgin(model, key, value)
		data = model.select(page=page, order=order, limit=limit)
		return data

	# 获取某个model下的数据
	def one(self, name, **kwd):
		model = self.model(name)
		if kwd:
			for key,value in kwd.items():
				self.assgin(model, key, value)
		data = model.select(type='fetchone')
		return data

	# 更新
	def update(self, name, id, data, cdate=True):
		model = self.model(name)
		if id:
			model.id = id
			if cdate == True and 'cdate' not in data:
				data['cdate'] = 'time'
			model.update(data)
			return id
		else:
			for key, value in data.items():
				method = 'assgin'
				if 'date' in key:
					method = 'time'
				self.assgin(model, key, value, method)
			return model.insert()

	# 删除
	def delete(self, name, id, state = False):
		model = self.model(name)
		model.id = id
		return model.update(state=state)

	# 物理删除
	def rDelete(self, name, id):
		model = self.model(name)
		model.id = id
		return model.delete()

	def model(self, name):
		return Demeter.model(name)

	def assgin(self, model, key, value, method='assgin'):
		if hasattr(model, key):
			attr = getattr(model, key)
			if hasattr(attr, method):
				call = getattr(attr, method)
				call(value)