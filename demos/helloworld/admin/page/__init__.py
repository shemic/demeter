# -*- coding: utf-8 -*-
Web.load(__file__, globals())


class Load(Base):
    KEYS = ('admin',)

    def setting(self):
        self.search()
        self.admin()

    def admin(self):
        admin = 1
        self.data['auth'] = True
        
        if 'admin' in self.data['setting'] and self.data['setting']['admin'] > 0:
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
                for n in j[0]:
                    if n+',' in menu:
                        l = str(i)+'_'+str(n)
                        self.data['setting']['menu'].append(l)
                        self.data['setting']['menu'].append(l + '_update')
                    m = m + 1
            self.data['setting']['menu'] = ',' + ",".join(self.data['setting']['menu'])+','

            uri = '_' + self.request.uri + ','
            if self.data['setting']['admin'] != admin and uri not in self.data['setting']['menu']:
                self.data['auth'] = False

    def menu(self):
        parent = [['站点设置', '基础设置'],['&#xe62e;', '&#xe62a;']]
        child = [
            [['/site/site', '/site/product'],['站点管理', '抢购商品设置']]
            ,[['/admin/admin','/admin/role', '/admin/log'],['管理员设置', '管理权限设置', '系统日志']]
            ]
        return (parent,child)