# -*- coding: utf-8 -*-
"""
    demeter
    name:web.py
    author:rabin
    好多年前写的，以后换成fastapi吧
"""
#from gevent import monkey
#monkey.patch_all()
#import gevent
import functools
import os
import json
import threading
import signal
from demeter.core import *
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.httpclient 
import tornado.concurrent
import asyncio

class Base(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def initialize(self):
        try:
            Demeter.request = self
            self.assign()
            self.page()
            self.cookie()
            self.setting()
        except Exception as e:
            return

    def get_current_user(self):
        return self.get_secure_cookie(self.KEYS[0])

    def assign(self):
        self.data = {}
        self.data['setting'] = Demeter.config['setting']
        self.data['base'] = Demeter.config['base']
        
    def cookie(self):
        for key in self.KEYS:
            cookie = None
            """
            if key in self.data['base']:
                cookie = self.data['base'][key]
            """
            if not cookie:
                cookie = self.get_secure_cookie(key)
                #cookie = self.get_cookie(key)
            if not cookie:
                value = self.input(key)
                if value:
                    #self.set_secure_cookie(key, value)
                    self.data['setting'][key] = value
                else:
                    self.data['setting'][key] = 0
            else:
                self.data['setting'][key] = cookie

    def page(self):
        Demeter.config['page'] = {}
        page = self.input('page')
        if page:
            Demeter.config['page']['ajax'] = True
        else:
            Demeter.config['page']['ajax'] = False
            page = 1
        Demeter.config['page']['current'] = page
        Demeter.config['page']['total'] = 0
        self.data['page'] = Demeter.config['page']

    def search(self):
        data = self.request.arguments
        self.data['search'] = {}
        self.data['update'] = {}
        for key in data:
            if 'search_' in key:
                index = key.replace('search_', '')
                i = 0
                for a in data[key]:
                    data[key][i] = a.decode()
                self.data['search'][index] = ",".join(data[key])
            if 'update_' in key:
                index = key.replace('update_', '')
                i = 0
                for a in data[key]:
                    data[key][i] = a.decode()
                    i = i + 1
                self.data['update'][index] = ",".join(data[key])

    def input(self, key, value=None):
        return self.get_argument(key, value)

    def inputs(self, key):
        return self.get_arguments(key)

    def inputAll(self):
        param = {k: v[0].decode() for k, v in self.request.arguments.items() if v}
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                param.update(tornado.escape.json_decode(self.request.body))
            except:
                pass
        return param

    def service(self, name):
        return Demeter.service(name)

    def model(self, name):
        return Demeter.model(name)

    def set(self, **kwd):
        self.data['common'] = kwd
        self.data['common']['argvs'] = ''

    def show(self, name):
        self.view('common/'+name+'.html')

    def list(self, model, order = 'cdate desc'):
        self.data['state'] = self.input('state', True)
        self.data['list'] = self.service('common').list(model, state=self.data['state'], search=self.data['search'], page=True, order=order)

    def one(self, model, **kwd):
        self.data['info'] = {}
        if 'id' not in kwd and self.input('id'):
            id = self.input('id')
            if id:
                kwd['id'] = id
        if kwd:
            self.data['info'] = self.service('common').one(model, **kwd)

    def update(self, model, msg='', id=0, **kwd):
        if not self.data['auth']:
            self.auth()
        else:
            if id <= 0:
                id = self.input('id')
            if kwd:
                info = self.service('common').one(model, **kwd)
                if info and (id != info['id']):
                    self.out(msg)
                    return
            state = self.service('common').update(model, id, self.data['update'])
            self.log(model, 'update', self.data['update'])
            self.out('yes', {'id':state})
            return state

    def drop(self, model):
        if not self.data['auth']:
            self.auth()
        else:
            id = self.input('id')
            state = self.input('state', False)
            state = self.service('common').delete(model, id, state)
            self.log(model, 'delete', {id:id, state:state})
            self.out('yes', {'state':state})

    def log(self, model, method, data):
        if 'admin' in self.data['setting'] and self.data['setting']['admin'] > 0:
            insert = {}
            insert['admin_id'] = self.data['setting']['admin']
            insert['model'] = model
            insert['method'] = method
            insert['data'] = json.dumps(data)
            self.service('common').update('manage_log', None, insert)

    def view(self, name):
        if not self.data['auth']:
            self.auth()
        else:
            config = Demeter.config[Demeter.web]
            path = ''
            if 'mobile' in config:
                mobile = Demeter.checkMobile(self.request)
                if mobile:
                    path = 'mobile/'
                else:
                    path = 'pc/'
            self.render(path + name, data=self.data, Demeter=Demeter)

    def host(self):
        return self.request.protocol + "://" + self.request.host

    def auth(self):
        self.out('您没有权限')

    def out(self, msg='', data={}, code=0):
        callback = self.input('callback')
        function = self.input('function')
        result = Demeter.out(msg=msg, data=data, code=code, callback=callback, function=function)
        self.write(result)
        if not data:
            from tornado.web import Finish
            raise Finish()
        else:
            self.finish()

class Web(object):
    @classmethod
    def auth(cls, method):
        return tornado.web.authenticated(method)

    @classmethod
    def setting(cls, method):
        return cls.run(method)
        
    @staticmethod
    def run(method):
        @tornado.gen.coroutine
        @functools.wraps(method)
        def callback(self, *args, **kwargs):
            try:
                result = method(self, *args, **kwargs)
                return result
            except Exception as e:
                import traceback
                error = traceback.format_exc()
                if 'Finish' in error:
                    return
                else:
                    traceback.print_exc()
                    try:
                        return self.view('404.html')
                    except Exception as e:
                        return self.out('404')
        return callback

    @classmethod
    def init(cls, application):
        for v in application:
            cls.load(v)

    @classmethod
    def load(cls, package):
        url = []
        for key in Demeter.getPackage(package):
            module = Demeter.getObject(key)
            url = cls.url(module, key, url)
        Demeter.route = Demeter.route + url

    @staticmethod
    def url(module, key, url):
        methods = Demeter.getMethod(module)
        key = key.split('.')[-1]
        for i, j in methods:
            act = ''
            if '_path' in i:
                act = i.replace('_path', '')
            if '_html' in i:
                act = i.replace('_html', '.html')
            if act:
                attr = getattr(module, i)
                if key == 'main' and act == 'index':
                    url.append((r'/', attr))
                elif key == act or act == 'index':
                    url.append((r'/' + key, attr))
                url.append((r'/' + key + '/' + act, attr))
        return url

    @classmethod
    def start(cls, application=[]):
        # 这里不使用线程，直接主线程启动服务
        cls.start_server(application)

    @classmethod
    def start_server(cls, application=[]):
        # 确保事件循环存在
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        cls.init(application)
        if 'route' in Demeter.config['setting']:
            Demeter.echo(Demeter.route)

        config = Demeter.config[Demeter.web]
        cookie = False
        if 'tornado' not in Demeter.config:
            Demeter.config['tornado'] = {}
        if 'xsrf_cookies' in config:
            cookie = Demeter.bool(config['xsrf_cookies'])

        settings = dict({
            "static_path": Demeter.webPath + 'static',
            "template_path": Demeter.webPath + 'templates',
            "cookie_secret": 'demeter',
            "login_url": '/user/login',
            "xsrf_cookies": cookie,
            "debug": Demeter.bool(config['debug']),
            "port": config['port'],
            "max_buffer_size": int(config['max_buffer_size']),
            "process": int(config['process'])
        }, **Demeter.config['tornado'])

        # 补充设置项
        for v in ('cookie_secret', 'login_url', 'static_path', 'template_path'):
            if v in config:
                settings[v] = config[v]

        handlers = []

        def application_setting():
            handlers.append((r"/upload/(.*)", tornado.web.StaticFileHandler, {"path": Demeter.path + 'runtime/upload/'}))
            handlers.append((r"/files/(.*[\.png|\.jpg|\.gif|\.js|\.css|\.font|\.fonts|\.ttc|\.ttf|\.woff|\.woff2|\.fon|\.eot|\.otf])",
                             tornado.web.StaticFileHandler, {"path": Demeter.path + 'runtime/files/'}))
            handlers.append((r"/qrcode/(.*)", tornado.web.StaticFileHandler, {"path": Demeter.path + 'runtime/qrcode/'}))
            handlers.append((r"/camera/(.*)", tornado.web.StaticFileHandler, {"path": Demeter.path + 'runtime/camera/'}))
            handlers.append((r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}))
            handlers.append((r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])))
            handlers.extend(Demeter.route)

        def stop_server(signum, frame):
            print("Signal received, stopping Tornado...")
            tornado.ioloop.IOLoop.current().add_callback_from_signal(tornado.ioloop.IOLoop.current().stop)

        # 注册信号处理，只能在主线程调用
        signal.signal(signal.SIGINT, stop_server)
        signal.signal(signal.SIGTERM, stop_server)

        application_setting()
        application = tornado.web.Application(handlers=handlers, **settings)

        if settings['debug']:
            application.listen(settings['port'])
        else:
            server = tornado.httpserver.HTTPServer(application, settings['max_buffer_size'])
            server.bind(settings['port'])
            server.start(settings['process'])

        Demeter.echo(f'running on port {settings["port"]}')

        try:
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            print("KeyboardInterrupt received, stopping...")
            tornado.ioloop.IOLoop.current().stop()
        finally:
            print("Server stopped, exiting.")
            os._exit(0)
