#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter web page
    name:work.py
    author:rabin
"""
from __load__ import *

class index_path(Load):
	#权限控制，需要在Load类中自行做判断
	#@Web.auth
	#异步加载，增加执行效率
	@Web.setting
	def get(self):
		self.view("index.html")

# 测试数据库 查询 /main/select
class select_path(Load):
	@Web.setting
	def get(self):
		# 从get、post获取数据，默认值为1
		id = int(self.input('site', 1))
		site = Demeter.model('site')
		site.id = id
		self.data['site'] = site.select(type='fetchone')

		product = Demeter.model('product')
		product.site_id = id
		self.data['product'] = product.select(col = '*', order = 'cdate desc', group = '', limit = '0,100')

		self.view('index.html')

# 测试数据库 更新和插入 /main/update
class update_path(Load):
	@Web.setting
	def get(self):
		id = int(self.input('site', 1))
		name = self.input('name', 'tests')
		site = Demeter.model('site')
		site.id = id
		state = site.update(name=name)

		self.data['site'] = site.select(type='fetchone')

		self.view('index.html')

# 测试数据库 使用sql（不建议使用） /main/sql.html
class sql_html(Load):
	@Web.setting
	def get(self):
		id = int(self.input('site', 1))
		name = self.input('name', 'tests')
		site = Demeter.model('site')
		state = site.query('update demeter_site set name = %s where id = %s', (name,id))

		self.data['site'] = site.query('select * from demeter_site where id = %s', (id))

		self.view('index.html')