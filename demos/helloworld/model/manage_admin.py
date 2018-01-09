# -*- coding: utf-8 -*-
"""
    demeter database
    name:manage_admin.py
    author:rabin
"""
from .__load__ import *

class Manage_admin(Model):
	__table__ = 'manage_admin'
	__comment__ = '超级管理员'
	id = Fields(type='int', primaryKey=True, autoIncrement=True, comment='管理员ID')
	role_id = Fields(type='int', comment='角色ID')
	username = Fields(type='varchar(50)', comment='管理员账号')
	mobile = Fields(type='bigint', comment='园区管理员手机号', unique=True)
	password = Fields(type='varchar(38)', comment='安全密码', md5=True)
	state = Fields(type='boolean', default='True', comment='数据存在状态')
	cdate = Fields(type='int', default='time', comment='创建时间')