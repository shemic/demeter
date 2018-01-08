# -*- coding: utf-8 -*-
"""
	demeter
	name:tcp.py
	author:rabin
"""
import socket  
import time
from demeter.core import *
from demeter.mqtt import *
from tornado.tcpserver import TCPServer
from tornado.ioloop  import IOLoop
from tornado import stack_context  
from tornado.escape import native_str 

class Connection(object):
	clients = set()
	EOF = '|e|'
	def __init__(self, stream, address):
		Connection.clients.add(self)
		self._pub = Pub()
		self._stream = stream
		self._address = address
		self._stream.set_close_callback(self.on_close)
		self.read_message()
		
	def read_message(self):
		self._message_callback = stack_context.wrap(self.on_message)  
		self._stream.read_until(self.EOF, self._message_callback)
	
	def on_message(self, data):
		data = data.replace(self.EOF, '')
		temp = data.split('|:|')
		key = temp[0]
		value = temp[1]
		self._pub.push(key, value)
		
		#print "User said:", data[:-1], self._address
		"""
		for conn in Connection.clients:
			conn.send_message(data)
		"""
		self.read_message()
		
	def send_message(self, data):
		self._stream.write(data)
			
	def on_close(self):
		#print "A user has left the chat room.", self._address
		Connection.clients.remove(self)
	
class Server(TCPServer):	
	def handle_stream(self, stream, address):
		#print "New connection :", address, stream
		Connection(stream, address)
		#print "connection num is:", len(Connection.clients)

class Client(object):
	EOF = '|e|'
	def __init__(self, host='0.0.0.0', port=8000):
		self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect.connect((host, port))
		
	def send(self, msg):
		msg = msg + self.EOF
		self.connect.sendall(msg)
		#data = self.connect.recv(1024)
	def close(self):
		self.connect.close()