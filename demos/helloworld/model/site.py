# -*- coding: utf-8 -*-
"""
    demeter database
    name:site.py
"""
from __load__ import *

class Site(Model):
	__table__ = 'site'
	__comment__ = '站点主表'
	id = Fields(type='int', primaryKey=True, autoIncrement=True, comment='站点ID')
	name = Fields(type='varchar(200)', comment='站点名')
	link = Fields(type='varchar(200)', comment='站点网址')
	login_link = Fields(type='varchar(300)', comment='登录页链接')
	username = Fields(type='varchar(300)', comment='账号')
	password = Fields(type='varchar(300)', comment='密码')
	state = Fields(type='boolean', default='True', comment='数据存在状态')
	cdate = Fields(type='int', default='time', comment='创建时间')