# -*- coding: utf-8 -*-

import os

import webob
import webtest
import webtest_casperjs

files = os.path.dirname(__file__)

try:
    unicode()
except NameError:
    b = bytes
    def u(value):
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value
else:
    def b(value):
        return str(value)
    def u(value):
        if isinstance(value, unicode):
            return value
        return unicode(value, 'utf-8')


def application(environ, start_response):
    req = webob.Request(environ)
    resp = webob.Response()
    if req.method == 'GET':
        filename = req.path_info.strip('/') or 'index.html'
        if filename in ('302',):
            redirect = req.params['redirect']
            resp = webob.exc.HTTPFound(location=redirect)
            return resp(environ, start_response)
        if filename.isdigit():
            resp.status = filename
            filename = 'index.html'
        filename = os.path.join(files, 'html', filename)
        if os.path.isfile(filename):
            kw = dict(message=req.params.get('message', ''),
                      redirect=req.params.get('redirect', ''))
            with open(filename) as f:
                resp.unicode_body = u(f.read()) % kw
            _, ext = os.path.splitext(filename)
            if ext == '.html':
                resp.content_type = 'text/html'
            elif ext == '.js':
                resp.content_type = 'text/javascript'
            elif ext == '.json':
                resp.content_type = 'application/json'
    else:
        redirect = req.params.get('redirect', '')
        if redirect:
            resp = webob.exc.HTTPFound(location=redirect)
        else:
            resp.body = req.body
    return resp(environ, start_response)


def test_casperjs():
    app = webtest.TestApp(application)
    with webtest_casperjs.casperjs(app) as run:
        run('fixtures/test_casperjs.js')


def test_casperjs_fail():
    app = webtest.TestApp(application)
    with webtest_casperjs.casperjs(app) as run:
        try:
            run('fixtures/test_casperjs_fail.js')
        except AssertionError:
            pass
        else:
            raise AssertionError('test does not fail')
