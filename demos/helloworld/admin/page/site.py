# -*- coding: utf-8 -*-
"""
    demeter web page
    name:site.py 站点相关
    author:rabin
"""

class site_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.common(
			name = u'站点管理'
			,path = '/site/site'
			,width = '600'
			,height = '600'
			,search = (('label-1','workdate-time-start','workdate-time-end','name-input-mlike'), (u'日期范围',u'开始时间',u'截止时间',u'站点名称'))
			,thead = (u'站点名称', u'快捷功能', u'更新时间')
			,tbody = ('name','func', 'cdate')
			,state = True
		)
		menu = (
			{'name':'抢购商品管理', 'url':'/site/product'}
			,
			)
		self.commonList('site')
		if self.data['list']:
			for key, value in enumerate(self.data['list']):
				id = str(value['id'])
				param = '?search_site_id-select-=' + id
				self.data['list'][key]['func'] = ''
				for i in menu:
					self.data['list'][key]['func'] = self.data['list'][key]['func'] + '<a href="'+i['url']+''+param+'">'+i['name']+'</a>&nbsp;&nbsp;&nbsp;&nbsp;'
		self.commonView('list')

class site_update_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.common(
			path = '/site/site'
			,label = (u'站点名称',u'站点网址',u'登录页链接',u'登录账号',u'登录密码')
			,update = ('name-input-required','link-input-required','login_link-input-required','username-input-required','password-password-required')
		)
		self.commonOne('site')
		self.commonView('update')
	@Web.auth
	@Web.setting
	def post(self):
		self.commonUpdate('site')
	@Web.auth
	@Web.setting
	def delete(self):
		self.commonDelete('site')

class product_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.common(
			name = u'抢购商品'
			,path = '/site/product'
			,width = '600'
			,height = '600'
			,search = (('label-1','cdate-time-start','cdate-time-end','site_id-select-','name-input-mlike'), (u'日期范围',u'开始时间',u'截止时间',u'选择站点',u'商品名'))
			,thead = (u'所属站点', u'商品名', u'状态', u'更新时间')
			,tbody = ('site', 'name', 'status', 'cdate')
			,state = True
		)
		self.data['common']['search_site_id-select-'] = self.service('common').list('site')
		self.commonList('product')
		status = {}
		status[1] = '待机'
		status[2] = '入队'
		status[3] = '抢购中'
		status[4] = '抢购完成'
		if self.data['list']:
			for key, value in enumerate(self.data['list']):
				site = self.service('common').one('site', id=value['site_id'])
				self.data['list'][key]['site'] = site['name']
				self.data['list'][key]['status'] = '<a href="/site/order?search_product_id-select-='+str(value['id'])+'">'+status[value['status']]+'[查看二维码]</a>'

		self.commonView('list')

class product_update_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		status = [
			{'id':'1', 'name': '待机-如果之前抢购完成，选择此项可以重新开始抢购'},
		]
		self.common(
			path = '/site/product'
			,label = (u'所属站点', u'商品名称', u'商品链接', u'状态控制')
			,update = ('site_id-select-required', 'name-input-required','link-input-required', 'status-select-required')
			,update_site_id = self.service('common').list('site')
			,update_status = status
		)
		self.commonOne('product')
		self.commonView('update')
	@Web.auth
	@Web.setting
	def post(self):
		self.commonUpdate('product')
	@Web.auth
	@Web.setting
	def delete(self):
		self.commonDelete('product')

class order_path(Load):
	@Web.auth
	@Web.setting
	def get(self):
		self.common(
			name = u'商品订单列表'
			,path = '/site/order'
			,width = '600'
			,height = '600'
			,edit = False
			,add = False
			,search = (('label-1','cdate-time-start','cdate-time-end', 'orderID-input-mlike'), (u'日期范围',u'开始时间',u'截止时间',u'订单ID'))
			,thead = (u'商品名称', u'订单ID', u'二维码', u'更新时间')
			,tbody = ('name', 'orderID', 'pic', 'cdate')
			,state = False
		)
		#self.data['common']['search_product_id-select-'] = self.service('common').list('product')
		self.commonList('order')
		if self.data['list']:
			for key, value in enumerate(self.data['list']):
				product = self.service('common').one('product', id=value['product_id'])
				self.data['list'][key]['name'] = product['name']
				value['pic'] = value['pic'].replace(Demeter.path + 'runtime', '')
				self.data['list'][key]['pic'] = '<img src="'+value['pic']+'" width="200px" />'

		self.commonView('list')