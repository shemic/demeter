# -*- coding: utf-8 -*-
"""
    demeter
    name:mqtt.py
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
		state = hasattr(act, 'message')
		if state:
			self.client.on_connect = self.connectAndSub
			self.client.on_message = act.message
		else:
			self.client.on_connect = self.connect
		self.client.connect(Demeter.config['mqtt']['host'], Demeter.config['mqtt']['port'], int(Demeter.config['mqtt']['timeout']))
		if state:
			self.client.loop_forever()

	def __del__(self):
		pass

	def getClient(self):
		return self.client

	def connect(self, client, userdata, flags, rc):
		pass

	def connectAndSub(self, client, userdata, flags, rc):
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

	def push(self, key, msg, qos=0, retain=False, callback=False, param=False, feedback=False):
		result = self.connect.getClient().publish(key,payload=msg,qos=qos,retain=retain)

		self.callback = callback
		self.param = param
		if feedback == True and 'key' in self.param:
			self.connect.client.on_message = self.feedback
			self.connect.client.subscribe(self.param['key'])
			self.connect.client.loop_forever()
		elif qos in (1,2):
			self.connect.client.on_publish = self.publish
			self.connect.client.loop_forever()
		#else:
			#self.connect.client.disconnect()
		return result

	def publish(self, client, userdata, mid, msg='ok'):
		self.callback(self.param, client, userdata, mid, msg)
		self.connect.client.disconnect()

	def feedback(self, client, userdata, msg):
		if msg.topic == self.param['key']:
			self.publish(client, userdata, 0, msg.payload)

class Sub(object):

	def __init__(self):
		Connect(self)

	def __del__(self):
		pass

	def message(self, client, userdata, msg):
		#print(msg.topic+" "+str(msg.payload))
		#return
		self.connect.handle(msg.topic, str(msg.payload))