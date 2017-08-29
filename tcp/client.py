#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	demeter tcp
	name:client.py
	author:rabin
"""
import socket  
import time  
HOST = '0.0.0.0'	# The remote host  
PORT = 8000		   # The same port as used by the server  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s.connect((HOST, PORT))  
  
s.sendall('Hello, \nw')  
time.sleep(5)  
s.sendall('ord! \n')  
  
data = s.recv(1024)  
  
print 'Received', repr(data)  
  
time.sleep(60)  
s.close() 