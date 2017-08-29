#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter load
    author:rabin
"""
import tornado.web
from demeter.core import *
import json

class Base(tornado.web.RequestHandler):
	def initialize(self):
		self.data = {}
		self.page()
		self.search()
		self.cookie()
		self.setting()
		self.assign()

	def get_current_user(self):
		return self.get_secure_cookie(self.KEYS[1])

	def assign(self):
		self.data['setting'] = Demeter.config['setting']
		
	def cookie(self):
		for key in self.KEYS:
			cookie = None
			if key in Demeter.config['base']:
				cookie = Demeter.config['base'][key]
			if not cookie:
				cookie = self.get_secure_cookie(key)
				#cookie = self.get_cookie(key)
			if not cookie:
				value = self.input(key)
				if value:
					#self.set_secure_cookie(key, value)
					Demeter.config['setting'][key] = value
				else:
					Demeter.config['setting'][key] = 0
			else:
				Demeter.config['setting'][key] = cookie

	def page(self):
		Demeter.config['page'] = {}
		page = self.input('page')
		if page:
			Demeter.config['page']['ajax'] = True
		else:
			Demeter.config['page']['ajax'] = False
			page = 1
		Demeter.config['page']['current'] = page
		Demeter.config['page']['total'] = 0
		self.data['page'] = Demeter.config['page']

	def search(self):
		data = self.request.arguments
		self.data['search'] = {}
		self.data['update'] = {}
		for key in data:
			if 'search_' in key:
				index = key.replace('search_', '')
				self.data['search'][index] = ",".join(data[key])
			if 'update_' in key:
				index = key.replace('update_', '')
				self.data['update'][index] = ",".join(data[key])

	def input(self, key, value=None):
		return self.get_argument(key, value)

	def service(self, name):
		return Demeter.service(name)

	def model(self, name):
		return Demeter.model(name)

	def common(self, **kwd):
		self.data['common'] = kwd
		farm = str(Demeter.config['setting']['farm'])
		self.data['common']['argvs'] = '&farm=' + farm + '&search_farm_id-select-=' + farm

	def commonView(self, name):
		self.view('common/'+name+'.html')

	def commonList(self, model):
		self.data['state'] = self.input('state', True)
		self.data['list'] = self.service('common').list(model, state=self.data['state'], search=self.data['search'], page=True)

	def commonOne(self, model, **kwd):
		id = self.input('id')
		self.data['info'] = {}
		if id:
			kwd['id'] = id
		if kwd:
			self.data['info'] = self.service('common').one(model, **kwd)
		if not self.data['info'] and Demeter.config['setting']['farm'] > 0:
			self.data['info']['farm_id'] = Demeter.config['setting']['farm']

	def commonUpdate(self, model, msg='', id=0, **kwd):
		if not self.data['auth']:
			self.auth()
		else:
			if id <= 0:
				id = self.input('id')
			if kwd:
				info = self.service('common').one(model, **kwd)
				if id:
					id = int(id)
				if info and (id != info['id']):
					self.out(msg)
					return
			state = self.service('common').update(model, id, self.data['update'])
			self.log(model, 'update', self.data['update'])
			self.out('yes', {'id':state})
			return state

	def commonDelete(self, model):
		if not self.data['auth']:
			self.auth()
		else:
			id = self.input('id')
			state = self.input('state', False)
			state = self.service('common').delete(model, id, state)
			self.log(model, 'delete', {id:id, state:state})
			self.out('yes', {'state':state})

	def log(self, model, method, data):
		insert = {}
		insert['admin_id'] = Demeter.config['setting']['admin']
		insert['model'] = model
		insert['method'] = method
		insert['data'] = json.dumps(data)
		self.service('common').update('manage_log', None, insert)

	def view(self, name):
		if not self.data['auth']:
			self.auth()
		else:
			self.render(name, data=self.data)

	def auth(self):
		self.out('您没有权限')

	def out(self, msg='', data={}, code=0):
		callback = self.input('callback')
		function = self.input('function')
		result = ''
		send = {}
		send['status'] = 1
		send['msg'] = msg
		send['data'] = data
		send['code'] = code
		if not send['data']:
			send['status'] = 2
		result = json.dumps(send)
		if callback:
			result = callback + '(' + result + ')'
		elif function:
			result = '<script>parent.' + function + '(' + result + ')' + '</script>';
		self.write(result)
		#self.finish(result)
