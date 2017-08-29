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
PATH = ''
class Demeter(object):
	path = ''
	config = {}
	serviceObj = {}
	modelObj = {}
	web = ''

	def __new__(cls, *args, **kwargs):
		print 'error'
		sys.exit()

	def __init__(self):
		pass

	@classmethod
	def initConfig(cls):
		global PATH
		if PATH == '':
			PATH = File.path()
		cls.path = PATH
		if cls.config == {}:
			name = 'dev'
			if 'DEMETER_CONF' in os.environ:
				name = os.environ['DEMETER_CONF']
			filename = cls.path + 'conf/'+name+'.conf'
			if File.exists(filename):
				config = ConfigParser.ConfigParser()
				config.read(filename)

				for item in config.sections():
					cls.config[item] = cls.readConfig(config, item)
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
	def echo(cls, args):
		module = cls.getObject('pprint')
		module.pprint(args)

	@classmethod
	def record(cls, key, value):
		# 记录日志
		# cls.log(key, value)
		service = cls.service('record')
		service.push(key, value)

	@classmethod
	def service(cls, name):
		if name not in cls.serviceObj:
			path = 'service.'
			if name == 'common':
				path = 'demeter.' + path 
			service = cls.getClass(name, path)
			cls.serviceObj[name] = service()
		return cls.serviceObj[name]

	@classmethod
	def model(cls, table, type='rdb'):
		if table not in cls.modelObj:
			type = cls.config['db'][type]
			config = cls.config[type]
			db = cls.getClass(type, 'demeter.db.')
			connect = db(config).get()
			model = cls.getClass(table, 'model.')
			cls.modelObj[table] =  model(type, connect, config)
		return cls.modelObj[table]

	@classmethod
	def getClass(cls, name, path=''):
		obj = cls.getObject(name, path)
		return getattr(obj, name.capitalize())

	@staticmethod
	def getObject(name, path = ''):
		module = __import__(path + name)
		return getattr(module, name)

	@staticmethod
	def bool(value):
		return value == str(True)

	@classmethod
	def runtime(cls, path, file, content=''):
		path = cls.path + 'runtime/' + path + '/'
		File.mkdir(path)
		file = path + file
		if File.exists(file):
			return False
		else:
			File.write(file, content)
			return True

	@classmethod
	def webstart(cls, name):
		cls.web = name
		cls.getObject('main', name + '.')

	@classmethod
	def md5(cls, value, salt=False):
		module = __import__('md5')
		md5 = getattr(module, 'new')
		md5_obj = md5()
		if salt:
			if salt == True:
				salt = cls.rand()
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
	def mktime(value):
		module = __import__('time')
		strptime = getattr(module, 'strptime')
		mktime = getattr(module, 'mktime')
		return int(mktime(strptime(value,'%Y-%m-%d %H:%M:%S')))

	@staticmethod
	def date(value):
		module = __import__('datetime')
		datetime = getattr(module, 'datetime')
		fromtimestamp = getattr(datetime, 'fromtimestamp')
		return str(fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S'))

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