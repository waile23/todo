#!/usr/bin/env python
# coding: utf-8
import os
import sys
app_root = os.path.dirname(__file__)
sys.path.append(app_root)
os.chdir(app_root)
import web

web.config.debug = False

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("./models")

from controllers import *
from models.pduser import *
from models.login import *
urls=("/account", account.app_account,
      "/user",user.app_user,
      "/tool",tool.app_tool,
      "",index.app_index)

app = web.application(urls, globals(),autoreload=True)

def logininfo_hook():
    #if file not request
    web.ctx.sitehost = "http://"+web.ctx.env['HTTP_HOST']
    if web.ctx.env['PATH_INFO']=="/favicon.ico":
        return web.redirect("/static/ico/favicon.ico")
    
    web.ctx.user = None
    uid = Login.decode_cookie()
    
    if uid and not web.ctx.get('user'):
        user = pduser.load_by_id(uid)
        if user is not None:
            admin=set([100000])
            if uid in admin:
                user.isadmin = True
            web.ctx.user = user

app.add_processor(web.loadhook(logininfo_hook))

application = app.wsgifunc()
if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
