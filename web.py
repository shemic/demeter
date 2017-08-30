#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	demeter web
	name:application.py
	author:rabin
"""
import os
import json
from demeter.core import *
import tornado.web
import tornado.ioloop
import tornado.httpserver

class Base(tornado.web.RequestHandler):
	def initialize(self):
		self.data = {}
		self.page()
		self.cookie()
		self.setting()
		self.assign()

	def get_current_user(self):
		return self.get_secure_cookie(self.KEYS[0])

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
		self.data['common']['argvs'] = ''
		if Demeter.config['setting']['farm'] > 0:
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
		if 'admin' in Demeter.config['setting'] and Demeter.config['setting']['admin'] > 0:
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
		if data:
			if 'page' in data and data['page']['total'] <= 0:
				del data['page']
			if 'update' in data and not data['update']:
				del data['update']
			if 'search' in data and not data['search']:
				del data['search']
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

class Web(object):
	@staticmethod
	def auth(method):
		return tornado.web.authenticated(method)
		
	@staticmethod
	def file(path):
		files = os.listdir(path)
		result = []
		for key in files:
			if '.DS_Store' not in key and  '__' not in key and 'pyc' not in key:
				key = key.replace('.py', '')
				result.append(key)
		return result
	@staticmethod
	def url(module, key, url):
		str = dir(module)
		for i in str:
			act = ''
			if '_path' in i:
				act = i.replace('_path', '')
			if '_html' in i:
				act = i.replace('_html', '.html')
			if act:
				attr = getattr(module, i)
				if key == 'main' and act == 'index':
					url.append((r'/', attr))
				elif key == act or act == 'index':
					url.append((r'/'+key, attr))
				url.append((r'/'+key+'/'+act, attr))
		return url
	@staticmethod
	def start(url):
		config = Demeter.config[Demeter.web]
		settings = {
			"static_path": Demeter.webPath + 'static',
			"template_path": Demeter.webPath + 'templates',
			"cookie_secret": "61oETzKXQAGaYekL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
			"login_url": "/user/login",
			"xsrf_cookies": True,
			"debug": Demeter.bool(config['debug']),
			#"autoreload": Demeter.bool(config['autoreload']),
			"port": config['port'],
			"max_buffer_size": int(config['max_buffer_size']),
			"process": int(config['process'])
		}
		handlers = []
		def application_setting():
			handlers.append((r"/upload/(.*)", tornado.web.StaticFileHandler, {"path": Demeter.path + 'runtime/upload/'}))
			handlers.append((r"/static/(.*)", tornado.web.StaticFileHandler, {"path":"static"}))
			handlers.append((r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])))
			handlers.extend(url)

		application_setting()
		application = tornado.web.Application(handlers=handlers, **settings)
		
		if settings['debug'] == True:
			application.listen(settings['port'])
			tornado.ioloop.IOLoop.instance().start()
		else:
			server = tornado.httpserver.HTTPServer(application, settings['max_buffer_size'])
			server.bind(settings['port'])
			server.start(settings['process'])
			try:		
				print 'running on port %s' % settings['port']
				tornado.ioloop.IOLoop.instance().start()

			except KeyboardInterrupt:
				tornado.ioloop.IOLoop.instance().stop()