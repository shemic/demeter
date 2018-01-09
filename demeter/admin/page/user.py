# -*- coding: utf-8 -*-
"""
    demeter web page
    name:user.py
    author:rabin
"""
from .__load__ import *

class login_path(Load):
	def get(self):
		self.view("login.html")
	def post(self):
		mobile = self.input('username')
		password = self.input('password')
		if mobile and password:
			admin = self.service('common').one('manage_admin', mobile=mobile)
			if admin:
				temp = admin['password'].split('_')
				if Demeter.md5(password, temp[1]) == admin['password']:
					self.set_secure_cookie('admin', str(admin['id']))
					#self.redirect('/')
					self.out('yes', {'id':admin['id']})
					return
		self.out('手机号或密码错误，登录失败')

		


class loginout_path(Load):
	def get(self):
		self.set_secure_cookie('admin', '')
		self.redirect('/user/login')