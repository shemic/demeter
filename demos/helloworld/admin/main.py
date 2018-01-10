# -*- coding: utf-8 -*-
from demeter.web import *
import demeter.admin.page as admin_page
import admin.page
Web.start(application=[admin.page,admin_page])