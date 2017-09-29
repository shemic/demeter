#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter mqtt
    name:connect.py
    author:rabin
"""
from demeter.core import *
import paho.mqtt.client as mqtt
#from gevent import monkey; monkey.patch_all()
#import gevent

class Connect(object):

	def __init__(self, act):
		act.connect = self
		self.client = mqtt.Client()
		self.client.on_connect = self.connect
		state = hasattr(act, 'message')
		if state:
			self.client.on_message = act.message
		self.client.connect(Demeter.config['mqtt']['host'], Demeter.config['mqtt']['port'], int(Demeter.config['mqtt']['timeout']))
		if state:
			self.client.loop_forever()

	def __del__(self):
		pass

	def getClient(self):
		return self.client

	def connect(self, client, userdata, flags, rc):
		#print("Connected with result code "+str(rc))
		#client.subscribe("sensor/#")
		sub = Demeter.config['mqtt']['sub'].split(',')
		for value in sub:
			client.subscribe(value + "/#")
		"""
		gevent.joinall([
			gevent.spawn(self.subscribe, client, 'sensor/#'),
			gevent.spawn(self.subscribe, client, 'pic/#'),
			gevent.spawn(self.subscribe, client, 'msg/#'),
		])
		"""

	@staticmethod
	def subscribe(client, key):
		client.subscribe(key)

	def handle(self, key, value):
		Demeter.record(key, value)


class Pub(object):

	def __init__(self):
		Connect(self)

	def __del__(self):
		pass

	def push(self, key, msg, qos=0, retain=False):
		self.connect.getClient().publish(key,msg,qos,retain)


class Sub(object):

	def __init__(self):
		Connect(self)

	def __del__(self):
		pass

	def message(self, client, userdata, msg):
		#print(msg.topic+" "+str(msg.payload))
		self.connect.handle(msg.topic, str(msg.payload))