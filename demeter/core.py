# -*- coding: utf-8 -*-
"""
	demeter
	name:core.py
	author:rabin
"""
import time
import os
import signal
import shutil
import re
import sys
import json
import subprocess
import importlib
#import fire
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class Demeter(object):
	path = ''
	root = ''
	config = {}
	option = {}
	web = ''
	request = False
	route = []
	logger = False
	dog = False
	syncData = {}

	def __new__(self, *args, **kwargs):
		sys.exit()

	def __init__(self):
		pass

	@staticmethod
	def checkPy3():
		if sys.version > '3':
			state = True
		else:
			state = False
		return state

	@classmethod
	def getConfig(self):
		state = self.checkPy3()
		if state:
			import configparser
			return configparser.ConfigParser()
		else:
			import ConfigParser
			return ConfigParser.ConfigParser()

	@staticmethod
	def isset(v): 
		try :
			type (eval(v))
		except :
			return 0
		else : 
			return 1

	@classmethod
	def initConfig(self):
		if not self.path:
			self.path = File.path()
			self.root = File.cur_path()
		if self.config == {}:
			filename = self.path + 'conf/'+self.getConfigName()+'.conf'
			if File.exists(filename):
				config = self.getConfig()
				config.read(filename, encoding="utf-8")

				for item in config.sections():
					self.config[item] = self.readConfig(config, item)
				return True
			else:
				self.path = self.path + '../'
				return self.initConfig()
				#Demeter.echo(filename + ' is not exists')
				#sys.exit()

	@classmethod
	def getConfigName(self):
		name = 'dev'
		if 'DEMETER_CONF' in os.environ:
			name = os.environ['DEMETER_CONF']
		param = {}
		param['config'] = 'c'
		self.getopt(param)
		if 'config' in self.option and self.option['config']:
			name = self.option['config']
		return name

	@staticmethod
	def readConfig(config, type):
		value = config.options(type)
		result = {}
		for item in value:
			result[item] = config.get(type, item)
		return result

	@classmethod
	def getopt(self, param = {}):
		import getopt
		param['help'] = 'h'
		shortopts = ''
		longopts  = []
		check = []
		for k,v in param.items():
			if k == 'help':
				shortopts = shortopts + v
			else:
				shortopts = shortopts + v + ':'
			longopts.append(k)
		try:
			options, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
			for name, value in options:
				for k,v in param.items():
					if name in ('-' + v, '--' + k):
						if k == 'help':
							self.usage()
						else:
							self.option[k] = value
		except getopt.GetoptError:
			#self.usage()
			return

	@classmethod
	def usage(self, name = 'usage'):
		file = self.path + name
		if not File.exists(file):
			file = self.root + name
		self.echo(File.read(file, encoding="utf-8"))
		sys.exit()

	@classmethod
	def temp(self, key='', name='', value=''):
		temp = Demeter.path + 'conf/temp.conf'
		if File.exists(temp):
			config = self.getConfig()
			config.read(temp, encoding="utf-8")
			if key and name:
				config.set(key, name, value)
				config.write(open(temp, 'w'))
			else:
				result = {}
				for item in config.sections():
					result[item] = self.readConfig(config, item)
				return result

	@classmethod
	def echo(self, args):
		import pprint
		pprint.pprint(args)

	@classmethod
	def record(self, key, value):
		# 记录日志
		# self.log(key, value)
		service = self.service('record')
		service.push(key, value)

	@classmethod
	def service(self, name, parent = ''):
		return self.load(name, parent, 'service')

	@classmethod
	def load(self, name, parent = '', base = 'service'):
		self.initConfig()
		path = base + '.'
		if name == 'common':
			path = 'demeter.'
			name = base
		if parent:
			path = path + parent + '.'
		load = self.getClass(name, path)
		return load()

	@classmethod
	def adminModel(self, table):
		self.initConfig()
		config = ('manage_admin', 'manage_log', 'manage_role')
		if table in config:
			return self.getClass(table, 'demeter.admin.model.')
		return False

	@classmethod
	def model(self, table, name='rdb'):
		self.initConfig()
		name = self.config['db'][name]
		config = self.config[name]
		obj = self.getObject('db', 'demeter.')
		db = getattr(obj, name.capitalize())
		connect = db(config).get()
		model = self.adminModel(table)
		if not model:
			model = self.getClass(table, 'model.')
		return model(name, connect, config)

	@classmethod
	def getMethod(self, module):
		import inspect
		return inspect.getmembers(module, callable)

	@classmethod
	def getPackage(self, package):
		import pkgutil
		for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__, prefix=package.__name__ + '.', onerror=lambda x: None):
			yield modname

	@classmethod
	def getPath(self, path):
		import pkgutil
		for importer, modname, ispkg in pkgutil.walk_packages(path):
			loader = importer.find_module(modname)
			mod = loader.load_module(modname)
			yield mod

	@staticmethod
	def getObject(name, path = ''):
		return importlib.import_module(path + name)

	"""
	@classmethod
	def getObject(self, name, path = ''):
		module = __import__(path + name)
		return getattr(module, name)
	"""

	@classmethod
	def getClass(self, name, path=''):
		obj = self.getObject(name, path)
		return getattr(obj, name.capitalize())

	@staticmethod
	def bool(value, type = 'db'):
		if type == 'mysql':
			value = value == str(True)
			if value == True:
				return '1'
			else:
				return '2'
		else:
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
	def webInit(self, name):
		self.initConfig()
		self.web = name
		self.webPath = self.path + self.web + '/'
		if self.web == 'admin':
			self.webPath = self.root + self.web + '/'
		self.getObject('main', name + '.')

	@classmethod
	def md5(self, value, salt=False):
		import hashlib
		if salt:
			if salt == True:
				salt = self.rand()
			value = value + salt
			return hashlib.md5(value.encode("utf-8")).hexdigest() + '_' + salt
		else:
			return hashlib.md5(value.encode("utf-8")).hexdigest()

	@classmethod
	def sha1(self, value, salt=False):
		import hashlib
		if salt:
			if salt == True:
				salt = self.rand()
			value = value + salt
			return hashlib.sha1(value.encode("utf-8")).hexdigest() + '_' + salt
		else:
			return hashlib.sha1(value.encode("utf-8")).hexdigest()

	@classmethod
	def range(self, length):
		if self.checkPy3():
			return range(length)
		else:
			return xrange(length)

	@classmethod
	def rand(self, length = 4):
		module = self.getObject('random')
		rand = getattr(module, 'randint')
		salt = ''
		chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
		len_chars = len(chars) - 1
		l = Demeter.range(length)
		for i in l:
			salt += chars[rand(0, len_chars)]
		return salt

	@classmethod
	def hash(self):
		return self.md5(str(time.clock()))

	@classmethod
	def uuid(self, value):
		import uuid
		return str(uuid.uuid5(uuid.uuid1(), value))

	@staticmethod
	def hour(value):
		if value < 10:
			return '0' + str(value)
		return value
	@staticmethod
	def time():
		return int(time.time())

	@staticmethod
	def mktime(value, string='%Y-%m-%d %H:%M:%S'):
		if ' ' in string and ' ' not in value:
			value = value + ' 00:00:00'
		return int(time.mktime(time.strptime(value,string)))

	@classmethod
	def date(self, value, string='%Y-%m-%d %H:%M:%S'):
		module = self.getObject('datetime')
		datetime = getattr(module, 'datetime')
		fromtimestamp = getattr(datetime, 'fromtimestamp')
		return str(fromtimestamp(value).strftime(string))

	@staticmethod
	def isJson(value):
		result = False
		try:
			result = json.loads(value)
		except ValueError:
			return result
		return result

	@staticmethod
	def host(value):
		import urllib
		protocol, s1 = urllib.splittype(value)
		value, s2 = urllib.splithost(s1)
		value, port = urllib.splitport(value)
		return value

	@staticmethod
	def compressUuid(value):
		row = value.replace('-', '')
		code = ''
		hash = [x for x in "0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
		l = Demeter.range(10)
		for i in l:
			enbin = "%012d" % int(bin(int(row[i * 3] + row[i * 3 + 1] + row[i * 3 + 2], 16))[2:], 10)
			code += (hash[int(enbin[0:6], 2)] + hash[int(enbin[6:12], 2)])
		return code

	@staticmethod
	def checkMobile(request):
		if 'Demeter-Mobile' in request.headers:
			return True
		userAgent = request.headers['User-Agent']
		# userAgent = env.get('HTTP_USER_AGENT')

		_long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
		_long_matches = re.compile(_long_matches, re.IGNORECASE)
		_short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
		_short_matches = re.compile(_short_matches, re.IGNORECASE)

		if _long_matches.search(userAgent) != None:
			return True
		user_agent = userAgent[0:4]
		if _short_matches.search(user_agent) != None:
			return True
		return False

	@staticmethod
	def exp(exp, value):
		if exp:
			exp = exp.replace('{n}', value)
			value = str(eval(exp))
		return value

	@classmethod
	def curl(self, url = '', param={}, method = 'get', timeout=5, max=2):
		import requests
		from requests.adapters import HTTPAdapter
		try:
			s = requests.Session()
			s.mount('http://', HTTPAdapter(max_retries=max))
			s.mount('https://', HTTPAdapter(max_retries=max))
			if method == 'get':
				req = s.get(url, params=param, timeout=timeout)
			else:
				req = s.post(url, params=param, timeout=timeout)
			result = req.text
		except requests.exceptions.RequestException as e:
			result = False
		return result

	@classmethod
	def out(self, msg='', data={}, code=0, callback='', function=''):
		if data:
			if 'page' in data and data['page']['total'] <= 0:
				del data['page']
			if 'update' in data and not data['update']:
				del data['update']
			if 'search' in data and not data['search']:
				del data['search']
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
		return result

	@classmethod
	def error(self, string):
		if self.request:
			self.request.out(string)
		else:
			self.echo(string)
			#os._exit(0)

	@classmethod
	def redis(self):
		self.initConfig()
		import redis
		config = self.config['redis']
		pool = redis.ConnectionPool(host=config['host'], password=config['password'], port=int(config['port']))
		return redis.Redis(connection_pool=pool)

	@classmethod
	def sync(self, table, id):
		table = table.replace('demeter_', '')
		if 'sync' in Demeter.config:
			config = Demeter.config['sync']['table'].split(',')
			service = Demeter.config['sync']['service'].split(',')
			if table in config and table not in self.syncData:
				Demeter.service(service[0], service[1]).rsync(table, id)
				#self.syncData[table] = True

class Log(object):
	@classmethod
	def init(self, name, output = False):
		import logging
		from logging.handlers import RotatingFileHandler
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

		logger = logging.getLogger(name)
		logger.setLevel(logging.DEBUG)

		if output:
			stream_handler = logging.StreamHandler(sys.stderr)
			stream_handler.setFormatter(formatter)
			logger.addHandler(stream_handler)

		file_handler = RotatingFileHandler(self.file(name), maxBytes=1024*1024,backupCount=5)
		file_handler.setLevel(level=logging.DEBUG)
		file_handler.setFormatter(formatter)
		logger.addHandler(file_handler)

		return logger
	@classmethod
	def read(self, name, lines=200):
		file = self.file(name)
		if File.exists(file):
			return File.tail(file, lines)
		return ''
	@classmethod
	def file(self, name):
		path = File.path() + 'runtime/log/'
		File.mkdir(path)

		return os.path.join(path, name + '.log')

class WatchDog(object):

	@staticmethod
	def init(path = [], reloads = [], recursive = False):
		event_handler = WatchDogHandle(reloads)
		dog = Observer()
		base = File.path()
		if not path:
			path = ['conf/',]
		for item in path:
			dog.schedule(event_handler, base + item, recursive=recursive)
		dog.start()

		return dog

class WatchDogHandle(FileSystemEventHandler):

	@classmethod
	def __init__(self, reloads = False):
		FileSystemEventHandler.__init__(self)
		self.reloads = reloads

	@classmethod
	def on_modified(self, event):
		if not event.is_directory and '.' in event.src_path:
			if self.reloads:
				for item in self.reloads:
					item.reload()
			elif Demeter.web:
				Demeter.webInit(Demeter.web)
			else:
				Demeter.echo('modify ' + event.src_path)

class File(object):

	@staticmethod
	def write(file, content):
		handle = open(file, 'w')
		handle.write(content)
		handle.close()
		#Shell.popen('chmod +x ' + file)
		os.chmod(file, 0o666)

	@staticmethod
	def read(path, name = ''):
		handle = open(path + name, 'r')
		content = handle.read()
		handle.close()
		return content
		
	@staticmethod
	def readContent(path, name = ''):
		content = ''
		handle = open(path + name, 'r')
		while True:
			line = handle.readline()
			if line:
				line = line.rstrip("\n")
				content = content + line
			else:
				break
		handle.close()
		return content

	@staticmethod
	def cur_path():
		return os.path.split(os.path.realpath(__file__))[0] + '/'

	@staticmethod
	def getFiles(path):
		return os.listdir(path)

	@staticmethod
	def path():
		return os.sys.path[0] + '/'

	@staticmethod
	def exists(name):
		return os.path.exists(name)

	@staticmethod
	def rename(old, new):
		return os.rename(old, new)

	@classmethod
	def remove(self, file):
		if isinstance(file, str) and self.exists(file):
			if os.path.isfile(file):
				return os.remove(file)
			else:
				# 删除非空目录
				return shutil.rmtree(file)
		return False

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

	@staticmethod
	def ext(path):
		return os.path.splitext(path)[1]

	@classmethod
	def runtime(self, path = 'data'):
		return self.mkdir(self.path() + 'runtime/' + path + '/')

	"""
	实现 tail -n
	"""
	@classmethod
	def tail(self, filepath, n=10):
		PAGE = 4096
		res = ""
		with open(filepath, 'rb') as f:
			f_len = f.seek(0, 2)
			rem = f_len % PAGE
			page_n = f_len // PAGE
			r_len = rem if rem else PAGE
			while True:
				# 如果读取的页大小>=文件大小，直接读取数据输出
				if r_len >= f_len:
					f.seek(0)
					lines = f.readlines()[::-1]
					break

				f.seek(-r_len, 2)
				# print('f_len: {}, rem: {}, page_n: {}, r_len: {}'.format(f_len, rem, page_n, r_len))
				lines = f.readlines()[::-1]
				count = len(lines) -1   # 末行可能不完整，减一行，加大读取量

				if count >= n:  # 如果读取到的行数>=指定行数，则退出循环读取数据
					break
				else:   # 如果读取行数不够，载入更多的页大小读取数据
					r_len += PAGE
					page_n -= 1

		for line in lines[:n][::-1]:
			res += line.decode('utf-8')
		return res

class Shell(object):
	@staticmethod
	def popen(command, sub=False, bg=False, timeout=0):
		string = command
		if bg == True:
			command = command + ' 1>/dev/null 2>&1 &'

		if timeout > 0:
			proc = subprocess.Popen(command,bufsize=0,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True, close_fds=True, preexec_fn = os.setsid)
			poll_seconds = .250
			deadline = time.time() + timeout
			while time.time() < deadline and proc.poll() == None:
				time.sleep(poll_seconds)
			if proc.poll() == None:
				os.killpg(proc.pid, signal.SIGTERM)
				return 'timeout'

			stdout,stderr = proc.communicate()
			return stdout
		elif sub == False:
			process = os.popen(command)
			output = process.read()
			process.close()
			return output
		else:
			popen  = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
			output = ''
			Demeter.echo(string)
			while True:
				output = popen.stdout.readline()
				Demeter.echo(output)
				if popen.poll() is not None:
					break
			return output

class Check(object):
	@staticmethod
	def match(rule, value):
		if not rule.match(value):
			return False
		return True

	@staticmethod
	def mobile(value):
		rule = re.compile(r'1\d{10}')
		return Check.match(rule, value)

	@staticmethod
	def number(value):
		try:
			int(value)
			return True
		except ValueError:
			return False

	@staticmethod
	def numberFloat(value):
		try:
			float(value)
			return True
		except ValueError:
			return False