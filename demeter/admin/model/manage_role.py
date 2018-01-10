# -*- coding: utf-8 -*-
"""
    demeter database
    name:manage_role.py
"""
from .__load__ import *

class Manage_role(Model):
	__table__ = 'manage_role'
	__comment__ = '角色表'
	id = Fields(type='int', primaryKey=True, autoIncrement=True, comment='角色ID')
	name = Fields(type='varchar(50)', comment='角色名称')
	auth = Fields(type='varchar(600)', comment='左侧菜单权限')
	top = Fields(type='varchar(500)', comment='头部菜单权限')
	oper = Fields(type='varchar(100)', comment='操作权限增删改查搜等')
	state = Fields(type='boolean', default='True', comment='数据存在状态')
	cdate = Fields(type='int', default='time', comment='创建时间')