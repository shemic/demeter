# -*- coding: utf-8 -*-
"""
    demeter
    name:service.py
    author:rabin
"""
from demeter.core import *

class Service(object):

	def list(self, name, state = True, search=None, page=False, order='cdate desc', limit = '0,100'):
		model = self.model(name)
		if state != -1:
			model.state = state
		if search:
			for key, value in search.items():
				if value or value == 0:
					if '-' in key:
						key = key.split('-')
						keyLen = len(key)
						if keyLen > 2 and key[2]:
							method = key[2]
						else:
							method = 'assign'
						self.assign(model, key[0], value, method)
					else:
						self.assign(model, key, value)
		data = model.select(page=page, order=order, limit=limit)
		return data

	def one(self, name, **kwd):
		model = self.model(name)
		if kwd:
			for key,value in kwd.items():
				self.assign(model, key, value)
		data = model.select(type='fetchone')
		return data

	def update(self, name, id, data, cdate=True):
		model = self.model(name)
		if id:
			model.id = id
			if cdate == True and 'cdate' not in data:
				data['cdate'] = 'time'
			model.update(data)
		else:
			for key, value in data.items():
				method = 'assign'
				if 'date' in key:
					method = 'time'
				self.assign(model, key, value, method)
			id = model.insert()
		#Demeter.sync(name, id)
		return id

	def delete(self, name, id, state = False):
		model = self.model(name)
		model.id = id
		state = model.update(state=state)
		#Demeter.sync(name, id)
		return state

	def rDelete(self, name, id):
		model = self.model(name)
		model.id = id
		return model.delete()

	def model(self, name):
		return Demeter.model(name)

	def assign(self, model, key, value, method='assign'):
		if hasattr(model, key):
			attr = getattr(model, key)
			if hasattr(attr, method):
				call = getattr(attr, method)
				call(value)