# -*- coding: utf-8 -*-
"""
    demeter load
    author:rabin
"""
from demeter.web import *

#可以在此定义一些核心类库

# 这个是基类
class Load(Base):
	# user是权限
	KEYS = ('user',)

	def setting(self):
		self.user()

	def user(self):
		ajax = self.input('ajax')
		if ajax:
			self.data['ajax'] = True
		else:
			self.data['ajax'] = False
		self.data['auth'] = True

		# 权限判断
		if 'user' in self.data['setting'] and self.data['setting']['user'] > 0:
			self.data['setting']['userInfo'] = self.service('common').one('farm_user', id=self.data['setting']['user'])
		else:
			# 没有权限
			return

		if '/' in self.request.uri:
			temp = self.request.uri.split('/')
			slen = len(temp)
			if slen > 1 and temp[1]:
				cur = temp[1]
		self.data['setting']['cur'] = cur

