# -*- coding: utf-8 -*-
from demeter.web import *

class Load(Base):
    KEYS = ('admin',)

    def setting(self):
        self.search()
        self.admin()

    def admin(self):
        self.data['auth'] = True
        
        if 'admin' in self.data['setting'] and self.data['setting']['admin']:
            self.data['setting']['admin'] = int(self.data['setting']['admin'])
            self.data['setting']['adminInfo'] = self.service('common').one('manage_admin', id=self.data['setting']['admin'])
            if self.data['setting']['adminInfo']:
                self.data['setting']['roleInfo'] = self.service('common').one('manage_role', id=self.data['setting']['adminInfo']['role_id'])
        else:
            #self.redirect('/user/login')
            return

        self.data['setting']['menuList'] = self.menu()

        if self.data['setting']['adminInfo']['id'] == admin:
            if 'menu' in self.data['setting']:
                del self.data['setting']['menu']
        else:
            self.data['setting']['menu'] = ['_/', '_/login', '_/main', '_/admin/log_update']
            menu = self.data['setting']['roleInfo']['auth'] + ','
            for i,j in enumerate(self.data['setting']['menuList'][1]):
                m = 0
                for n in j[1]:
                    if n+',' in menu:
                        l = str(i)+'_'+str(n)
                        self.data['setting']['menu'].append(l)
                        self.data['setting']['menu'].append(l + '_update')
                    m = m + 1
            self.data['setting']['menu'] = ',' + ",".join(self.data['setting']['menu'])+','

            uri = '_' + self.request.uri + ','
            if self.data['setting']['admin'] != admin and uri not in self.data['setting']['menu']:
                self.data['auth'] = False
            if 'web' in Demeter.config and 'url' in Demeter.config['web']:
                self.data['setting']['web'] = Demeter.config['web']['url']

    def menu(self):
        parent_str = Demeter.config['admin']['menu_parent']
        child_str = Demeter.config['admin']['menu_child']
        parent_str = parent_str + ',基础设置:&#xe62a;'
        child_str = child_str + ';管理员设置:/admin/admin,管理权限设置:/admin/role,系统日志:/admin/log'

        parent = self.getMenu(parent_str)

        child = []
        temp = child_str.split(';')
        for i in temp:
            child.append(self.getMenu(i))

        return (parent,child)

    def getMenu(self, string):
        menu = []
        menu.append([])
        menu.append([])
        temp = string.split(',')
        for i in temp:
            t = i.split(':')
            menu[0].append(t[0])
            menu[1].append(t[1])
        return menu