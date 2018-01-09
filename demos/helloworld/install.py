# -*- coding: utf-8 -*-
from demeter.core import *

def manage():
	model = Demeter.model('manage_admin')
	model.id = 1
	info = model.select(type='fetchone')
	if not info:
		model.role_id = 1
		model.username = 'admin'
		model.mobile = '15810090845'
		model.password = '123456'
		model.insert()

	model = Demeter.model('manage_role')
	model.id = 1
	info = model.select(type='fetchone')
	if not info:
		model.name = u'管理员'
		model.insert()

manage()

print 'install success!'