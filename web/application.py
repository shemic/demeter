#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    demeter web
    name:application.py
    author:rabin
"""
from demeter.core import *
import tornado.web
import tornado.ioloop
import tornado.httpserver

def start(url):
    config = Demeter.config[Demeter.web]
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "template_path": os.path.join(os.path.dirname(__file__), 'templates'),
        "cookie_secret": "61oETzKXQAGaYekL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        "login_url": "/user/login",
        "xsrf_cookies": True,
        "debug": Demeter.bool(config['debug']),
        #"autoreload": Demeter.bool(config['autoreload']),
        "port": config['port'],
        "max_buffer_size": int(config['max_buffer_size']),
        "process": int(config['process'])
    }
    handlers = []
    def application_setting():
        handlers.append((r"/upload/(.*)", tornado.web.StaticFileHandler, {"path": Demeter.path + 'runtime/upload/'}))
        handlers.append((r"/static/(.*)", tornado.web.StaticFileHandler, {"path":"static"}))
        handlers.append((r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])))
        handlers.extend(url)

    application_setting()
    application = tornado.web.Application(handlers=handlers, **settings)
    
    if settings['debug'] == True:
        application.listen(settings['port'])
        tornado.ioloop.IOLoop.instance().start()
    else:
        server = tornado.httpserver.HTTPServer(application, settings['max_buffer_size'])
        server.bind(settings['port'])
        server.start(settings['process'])
        try:        
            print 'running on port %s' % settings['port']
            tornado.ioloop.IOLoop.instance().start()

        except KeyboardInterrupt:
            tornado.ioloop.IOLoop.instance().stop()