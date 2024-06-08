# -*- coding: utf-8 -*-
"""
    demeter
    name:service.py
    author:rabin
"""
from demeter.core import *

class Service(object):

	def list(self, model, state = True, search=None, page=False, order='cdate desc', limit = '0,100'):
		model = self.model(model)
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

	def one(self, model, **kwd):
		model = self.model(model)
		if kwd:
			for key,value in kwd.items():
				self.assign(model, key, value)
		data = model.select(type='fetchone')
		return data

	def update(self, model, id, data, cdate=True):
		model = self.model(model)
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
		#Demeter.sync(model, id)
		return id

	def delete(self, model, id, state = False):
		model = self.model(model)
		model.id = id
		state = model.update(state=state)
		#Demeter.sync(model, id)
		return state

	def rDelete(self, model, id):
		model = self.model(model)
		model.id = id
		return model.delete()

	def model(self, model):
		return Demeter.model(model)

	def assign(self, model, key, value, method='assign'):
		if hasattr(model, key):
			attr = getattr(model, key)
			if hasattr(attr, method):
				call = getattr(attr, method)
				call(value)