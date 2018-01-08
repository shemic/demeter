# -*- coding: utf-8 -*-
"""
    demeter database
    name:product.py
    author:rabin
"""
from __load__ import *

class Product(Model):
	__table__ = 'product'
	__comment__ = '商品表'
	id = Fields(type='int', primaryKey=True, autoIncrement=True, comment='商品ID')
	name = Fields(type='varchar(200)', comment='商品名')
	link = Fields(type='varchar(500)', comment='商品链接')
	site_id = Fields(type='int', comment='所属站点')
	state = Fields(type='boolean', default='True', comment='数据存在状态')
	status = Fields(type='int', default='1', comment='抢购状态1待机2入队3抢购中4抢购完成')
	cdate = Fields(type='int', default='time', comment='创建时间')