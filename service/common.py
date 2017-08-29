#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter service
    name:common.py 通用业务
    author:rabin
"""
from demeter.core import *

class Common(object):

	# 获取某个model下的列表数据
	def list(self, name, state = True, search = None, page=False):
		model = self.model(name)
		model.state = state
		if search:
			for key, value in search.items():
				if value:
					key = key.split('-')
					if hasattr(model, key[0]):
						attr = getattr(model, key[0])
						if hasattr(attr, key[2]):
							method = key[2]
						else:
							method = 'assgin'
						func = getattr(attr, method)
						func(value)
		data = model.select(page=page)
		return data

	# 获取某个model下的数据
	def one(self, name, **kwd):
		model = self.model(name)
		if kwd:
			for key,value in kwd.items():
				if hasattr(model, key):
					attr = getattr(model, key)
					func = getattr(attr, 'assgin')
					func(value)
		data = model.select(type='fetchone')
		return data

	# 更新
	def update(self, name, id, data):
		model = self.model(name)
		if id:
			model.id = id
			if 'cdate' not in data:
				data['cdate'] = 'time'
			model.update(data)
			return id
		else:
			for key, value in data.items():
				if hasattr(model, key):
					attr = getattr(model, key)
					method = 'assgin'
					if 'date' in key:
						method = 'time'
					func = getattr(attr, method)
					func(value)
			return model.insert()

	# 删除
	def delete(self, name, id, state = False):
		model = self.model(name)
		model.id = id
		return model.update(state=state)

	def model(self, name):
		return Demeter.model(name)