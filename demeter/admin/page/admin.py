# -*- coding: utf-8 -*-
"""
    demeter web page
    name:admin.py
    author:rabin
"""
from .__load__ import *

class admin_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.set(
			name = u'管理员' #中文名
			,path = '/admin/admin' #路径
			,width = '600' # 新增页面的宽度
			,height = '400' # 新增页面的高度
			,search = (('label-1','cdate-time-start','cdate-time-end','name-input-mlike','mobile-input-mlike'), (u'日期范围',u'开始时间',u'截止时间',u'管理员姓名',u'手机号')) #搜索
			,thead = (u'管理员ID',u'管理员姓名', u'所属角色', u'手机号', u'更新时间') #表头
			,tbody = ('id','username', 'role', 'mobile', 'cdate') #表内容
			,state = False #启用回收站
		)
		self.list('manage_admin')
		self.show('list')

class admin_update_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.set(
			path = '/admin/admin'
			,label = (u'管理员姓名',u'所属角色',u'手机号',u'密码')
			,update = ('username-input-required','role_id-select-required','mobile-input-phone','password-password-')
			,update_role_id = self.service('common').list('manage_role')
		)
		self.one('manage_admin')
		self.show('update')
	@Web.auth
	@Web.setting
	def post(self):
		self.update('manage_admin', '手机号已经被注册', mobile=self.data['update']['mobile'])


class role_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.set(
			name = u'角色'
			,path = '/admin/role'
			,width = '800'
			,height = '600'
			,full = 1
			#,add = False
			#,edit = False
			,search = (('label-1','cdate-time-start','cdate-time-end','name-input-mlike'), (u'日期范围',u'开始时间',u'截止时间',u'角色名称'))
			,thead = (u'角色ID',u'角色名称', u'更新时间')
			,tbody = ('id','name', 'cdate')
			,state = False
		)
		self.list('manage_role')
		self.show('list')

class role_update_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		auth = self.data['setting']['menuList']
		self.set(
			path = '/admin/role'
			#,label = (u'角色名称',u'操作权限',u'左侧菜单',u'头部菜单')
			#,update = ('name-input-required','oper-checkbox-required','auth-checkmenu-required','top-checkbox-required')
			,label = (u'角色名称',u'左侧菜单',u'头部菜单')
			,update = ('name-input-required','auth-checkmenu-required','top-checkbox-required')
			,update_oper = ({'id':'select', 'name':'查询'}, {'id':'insert', 'name':'新增'}, {'id':'update', 'name':'修改'}, {'id':'delete', 'name':'删除'}, {'id':'search', 'name':'搜索'})
			,update_auth = auth
		)
		self.one('manage_role')
		self.show('update')
	@Web.auth
	@Web.setting
	def post(self):
		self.update('manage_role')
	@Web.auth
	@Web.setting
	def delete(self):
		self.drop('manage_role')

class log_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.set(
			name = u'日志' #中文名
			,path = '/admin/log' #路径
			,width = '600' # 新增页面的宽度
			,height = '400' # 新增页面的高度
			,add = False
			,edit = False
			,search = (('label-1','cdate-time-start','cdate-time-end', 'admin_id-input-'), (u'日期范围',u'开始时间',u'截止时间',u'管理员ID')) #搜索
			,thead = (u'管理员ID', u'操作表', u'方法', u'数据', u'更新时间') #表头
			,tbody = ('admin_id', 'model', 'method', 'data', 'cdate') #表内容
			,state = False #启用回收站
		)
		self.list('manage_log')
		self.show('list')

class setCookie_path(Load):
	@Web.auth
	@Web.setting
	def post(self):
		value = self.input('farm', Demeter.config['setting']['farm'])
		self.set_secure_cookie('farm', value)
		#self.set_cookie('farm', value)
		Demeter.config['base']['farm'] = value

