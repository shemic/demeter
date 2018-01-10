# -*- coding: utf-8 -*-
"""
    demeter database
    name:order.py
"""
from __load__ import *

class Order(Model):
	__table__ = 'order'
	__comment__ = '订单表'
	id = Fields(type='int', primaryKey=True, autoIncrement=True, comment='订单ID')
	orderID = Fields(type='varchar(500)', comment='原订单ID')
	pic = Fields(type='varchar(300)', comment='订单图片')
	site_id = Fields(type='int', comment='所属站点')
	product_id = Fields(type='int', comment='商品id')
	state = Fields(type='boolean', default='True', comment='数据存在状态')
	cdate = Fields(type='int', default='time', comment='创建时间')