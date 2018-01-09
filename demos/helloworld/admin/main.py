# -*- coding: utf-8 -*-
from demeter.web import *
import demeter.admin.page as admin_page
import page
Web.start(application=[page,admin_page])