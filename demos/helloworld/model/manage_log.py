# -*- coding: utf-8 -*-
"""
    demeter database
    name:manage_log.py
"""
from .__load__ import *

class Manage_log(Model):
	__table__ = 'manage_log'
	__comment__ = '后台日志表'
	id = Fields(type='int', primaryKey=True, autoIncrement=True, comment='日志ID')
	admin_id = Fields(type='int', comment='管理员ID')
	model = Fields(type='varchar(50)', comment='操作的表')
	method = Fields(type='varchar(50)', comment='操作的方法')
	data = Fields(type='text', comment='数据记录')
	state = Fields(type='boolean', default='True', comment='数据存在状态')
	cdate = Fields(type='int', default='time', comment='创建时间')