#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	demeter tcp
	name:server.py
	author:rabin
"""
import socket  
import time
from demeter.core import *
from demeter.mqtt import *
from tornado.tcpserver import TCPServer
from tornado.ioloop  import IOLoop

class Connection(object):
	clients = set()
	def __init__(self, stream, address):
		Connection.clients.add(self)
		self._stream = stream
		self._address = address
		self._stream.set_close_callback(self.on_close)
		self.read_message()
		
	def read_message(self):
		self._stream.read_until('\n', self.broadcast_messages)
	
	def broadcast_messages(self, data):
		pub = Pub()
		temp = data.split(':')
		key = temp[0]
		value = temp[1]
		pub.push(key, value)
		
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
	def __init__(self, host='0.0.0.0', port=8000):
		self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect.connect((host, port))
		
	def send(self, msg):
		self.connect.sendall(msg + '\n')
		#data = self.connect.recv(1024)
		self.connect.close()