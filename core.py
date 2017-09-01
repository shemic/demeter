#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter core
    name:demeter.py
    author:rabin
"""
import time
import os
import sys
import getopt
import ConfigParser
import subprocess
class Demeter(object):
	path = ''
	config = {}
	serviceObj = {}
	modelObj = {}
	web = ''

	def __new__(self, *args, **kwargs):
		print 'error'
		sys.exit()

	def __init__(self):
		pass

	@classmethod
	def initConfig(self):
		self.path = File.path()
		if self.config == {}:
			name = 'dev'
			if 'DEMETER_CONF' in os.environ:
				name = os.environ['DEMETER_CONF']
			filename = self.path + 'conf/'+name+'.conf'
			if File.exists(filename):
				config = ConfigParser.ConfigParser()
				config.read(filename)

				for item in config.sections():
					self.config[item] = self.readConfig(config, item)
				return True
			else:
				print filename + ' is not exists'
				sys.exit()

	@staticmethod
	def readConfig(config, type):
		value = config.options(type)
		result = {}
		for item in value:
			result[item] = config.get(type, item)
		return result

	@classmethod
	def echo(self, args):
		module = self.getObject('pprint')
		module.pprint(args)

	@classmethod
	def record(self, key, value):
		# 记录日志
		# self.log(key, value)
		service = self.service('record')
		service.push(key, value)

	@classmethod
	def service(self, name):
		if name not in self.serviceObj:
			path = 'service.'
			if name == 'common':
				path = 'demeter.'
				name = 'service'
			service = self.getClass(name, path)
			self.serviceObj[name] = service()
		return self.serviceObj[name]

	@classmethod
	def model(self, table, name='rdb'):
		if table not in self.modelObj:
			name = self.config['db'][name]
			config = self.config[name]
			obj = self.getObject('db', 'demeter.')
			db = getattr(obj, name.capitalize())
			connect = db(config).get()
			model = self.getClass(table, 'model.')
			self.modelObj[table] =  model(name, connect, config)
		return self.modelObj[table]

	@classmethod
	def getClass(self, name, path=''):
		obj = self.getObject(name, path)
		return getattr(obj, name.capitalize())

	@staticmethod
	def getObject(name, path = ''):
		module = __import__(path + name)
		return getattr(module, name)

	@staticmethod
	def bool(value):
		return value == str(True)

	@classmethod
	def runtime(self, path, file, content=''):
		path = self.path + 'runtime/' + path + '/'
		File.mkdir(path)
		file = path + file
		if File.exists(file):
			return False
		else:
			File.write(file, content)
			return True

	@classmethod
	def webstart(self, name):
		self.web = name
		self.webPath = self.path + self.web + '/'
		self.getObject('main', name + '.')

	@classmethod
	def md5(self, value, salt=False):
		module = __import__('md5')
		md5 = getattr(module, 'new')
		md5_obj = md5()
		if salt:
			if salt == True:
				salt = self.rand()
			md5_obj.update(value + salt)
			return md5_obj.hexdigest() + '_' + salt
		else:
			md5_obj.update(value)
			return md5_obj.hexdigest()

	@staticmethod
	def rand(length = 4):
		module = __import__('random')
		rand = getattr(module, 'randint')
		salt = ''
		chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
		len_chars = len(chars) - 1
		for i in xrange(length):
			salt += chars[rand(0, len_chars)]
		return salt

	@staticmethod
	def time():
		return int(time.time())

	@staticmethod
	def mktime(value, string='%Y-%m-%d %H:%M:%S'):
		return int(time.mktime(time.strptime(value,string)))

	@staticmethod
	def date(value, string='%Y-%m-%d %H:%M:%S'):
		module = __import__('datetime')
		datetime = getattr(module, 'datetime')
		fromtimestamp = getattr(datetime, 'fromtimestamp')
		return str(fromtimestamp(value).strftime(string))

	@staticmethod
	def error(string):
		print string
		os._exit(0)

class File(object):

	@staticmethod
	def write(file, content):
		handle = open(file, 'w')
		handle.write(content)
		handle.close()
		Shell.popen('chmod +x ' + file)

	@staticmethod
	def read(path, name):
		handle = open(path + name, 'r')
		content = handle.read()
		handle.close()
		return content

	@staticmethod
	def cur_path():
		return os.path.split(os.path.realpath(__file__))[0] + '/'

	@staticmethod
	def path():
		return os.sys.path[0] + '/'

	@staticmethod
	def exists(name):
		return os.path.exists(name)

	@staticmethod
	def rename(old, new):
		return os.rename(old, new)

	@staticmethod
	def remove(file):
		return os.remove(file)

	@staticmethod
	def mkdir(path):
		if File.exists(path) == False:
			os.mkdir(path)
		return path

	@staticmethod
	def mkdirs(path):
		if File.exists(path) == False:
			os.makedirs(path)
		return path

class Shell(object):
	@staticmethod
	def popen(command, sub=False, bg=False):
		string = command
		if bg == True:
			command = command + ' 1>/dev/null 2>&1 &'
		if sub == False:
			process = os.popen(command)
			output = process.read()
			process.close()
			return output
		else:
			popen  = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
			output = ''
			print string
			while True:
				output = popen.stdout.readline()
				print output
				if popen.poll() is not None:
					break
			return output

Demeter.initConfig()