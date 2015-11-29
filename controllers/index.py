#!/usr/bin/env python
# coding: utf-8
import web
import math
import sys
from models.pdtodo import *
from models.pduser import *
urls = (
    '/',                   'Index',
    '/todo/new',           'New',
    '/todo/(\d+)',         'View',
    '/todo/(\d+)/edit',    'Edit',
    '/todo/(\d+)/delete',  'Delete',
    '/todo/(\d+)/finish',  'Finish',
    '/todo/(\d+)/share',   'Share',
    '/todo/(\d+)/user',    'UserTodo',
)

from datetime import datetime 
def formatdate(dateStr, format): 
    date = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f") 
    return datetime.strftime(date, format) 
    
def time_span(date): 
    #date = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f") 
    delta = datetime.now() - date
    
    str = ""
    color = "label-default"
    
    if delta.days >= 365:
       str = '%d年前' % (delta.days / 365)
    elif delta.days >= 30:
       str =  '%d个月前' % (delta.days / 30)
    elif delta.days > 0:
       str =  '%d天前' % delta.days
    elif delta.seconds < 60:
       str =  "%d秒前" % delta.seconds
    elif delta.seconds < 60 * 60:
       str =  "%d分钟前" % (delta.seconds / 60)
    else:
       str =  "%d小时前" % (delta.seconds / 60 / 60)    

    return str
    
    '''
    if delta.days > 1:
        color = "label-warning"     
    if delta.days > 2:
        color = "label-danger"  
    elif delta.days > 30:
        color = "label-default"
    else:
        color = "label-primary"
    
    span = """<span class="label %s">%s</span>""" % (color,str)    
    return unicode(span)
    '''
globals()["ctx"] = web.ctx
render = web.template.render('templates',
                            base='layout',
                            globals=globals())
class New:
    def POST(self):
        if web.ctx.user is None:
            return web.seeother("/account/login")
        
        i = web.input()
        title = i.get('title', None)
        if not title:
            return render.error('计划是必须要填写的', None)
        pdtodo.new(web.ctx.user.u_id, title)
        raise web.seeother('/')


class Finish:
    def GET(self, id):
        if web.ctx.user is None:
            return web.seeother("/account/login")
        
        todo = pdtodo.get_by_id(id)
        if not todo:
            return render.error('没找到这条记录', None)
        i = web.input()
        status = i.get('status', 'yes')
        if status == 'yes':
            finished = 1
        elif status == 'no':
            finished = 0
        else:
            return render.error('您发起了一个不允许的请求', '/')
        pdtodo.finish(web.ctx.user.u_id, id, finished)
        raise web.seeother('/')
    
class Share:
    def GET(self, id):
        if web.ctx.user is None:
            return web.seeother("/account/login")
        
        todo = pdtodo.get_by_id(id)
        if not todo:
            return render.error('没找到这条记录', None)
        i = web.input()
        status = i.get('status', 'yes')
        if status == 'yes':
            share = 1
        elif status == 'no':
            share = 0
        else:
            return render.error('您发起了一个不允许的请求', '/')
        pdtodo.share(id, share)
        raise web.seeother('/')

class Edit:
    def GET(self, id):
        if web.ctx.user is None:
            return web.seeother("/account/login")
        
        todo = pdtodo.get_by_id(id)
        if not todo:
            return render.error('没找到这条记录', None)
        return render.todo.edit(todo)

    def POST(self, id):
        if web.ctx.user is None:
            return web.seeother("/account/login")
        todo = pdtodo.get_by_id(id)
        if not todo:
            return render.error('没找到这条记录', None)
        i = web.input()
        title = i.get('title', None)
        if not title:
            return render.error('计划是必须要填写的', None)
        pdtodo.edit(id, title)
        return render.error('修改成功！', '/')

class Delete:
    def GET(self, id):
        if web.ctx.user is None:
            return web.seeother("/account/login")
        
        todo = pdtodo.get_by_id(id)
        if not todo:
            return render.error('没找到这条记录', None)
        pdtodo.delete(id)
        return render.error('删除成功！', '/')
    
class UserTodo:
    def GET(self, uid):
        params = web.input(page=0)
        page = int(params.get("page"))
        pagesize = 10 
        
        user = pduser.load_by_id(uid)
        
        if user is None:
            return render.error('没有对应的用户！', '/')
        
        todos = pdtodo.todo_order_by_user(uid, page, pagesize)
        total = pdtodo.todo_rowcount_by_user(uid)
        
        
        
        totalpage=math.ceil(total/pagesize)
        if totalpage*pagesize<total:
            totalpage=totalpage+1   
        return render.todo.usertodo(todos, user, page,pagesize,int(totalpage),total)  

class Index:
    def GET(self):
        #if web.ctx.user is None:
        #    return web.seeother("/account/login")
        params = web.input(page=0)
        page = int(params.get("page"))
        pagesize = 10 
        if web.ctx.user is None:
            todos = pdtodo.todo_order_by_all(page, pagesize)
            total = pdtodo.todo_rowcount_by_all()
        else:
            todos = pdtodo.todo_order_by_login_user(web.ctx.user.u_id, page, pagesize)
            total = pdtodo.todo_rowcount_by_login_user(web.ctx.user.u_id)
        totalpage=math.ceil(total/pagesize)
        if totalpage*pagesize<total:
            totalpage=totalpage+1   
        return render.index(todos,page,pagesize,int(totalpage),total)     
       
def logininfo_hook():
    if web.ctx.user is None:
        #return web.seeother(web.ctx.sitehost)
        return web.seeother("/account/login")

app_index = web.application(urls, locals())

#app_index.add_processor(web.loadhook(logininfo_hook))