# -*- coding: utf-8 -*-
"""
    demeter web page
    name:upload.py
    author:rabin
"""
from .__load__ import *
from datetime import *
import os
import uuid

class upload_path(Load):
	@Web.auth
	@Web.setting
	def post(self, *args, **kwargs):
		url = self.request.protocol + "://" + self.request.host
		file_metas = self.request.files["file"]

		day = str(date.today())
		day = day.split('-')
		for meta in file_metas:
			name = meta['filename']
			temp = name.split('.')
			file_name =  str(uuid.uuid5(uuid.uuid1(), 'file'))
			file_path = day[0] + '/' + day[1] + '/' + day[2]
			file_path = File.mkdirs(os.path.join(Demeter.path, 'runtime','upload', file_path)) + '/' + Demeter.md5(file_name) + '.' + temp[1]
			with open(file_path, 'wb') as up:
				up.write(meta['body'])
		self.out('yes', {'src':url + file_path.replace(Demeter.path + 'runtime', '')})