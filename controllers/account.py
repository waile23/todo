# -*- coding: utf-8 -*-
'''
Created on 2012-8-27

@author: shanfeng
'''
import web
import time,datetime
import md5
import json
import os

from models.pduser import *
from models.pdfindpass import *
from models import login
from utils.xwjemail import * 
	

urls = ("/register", "Register",
		"/login", "Login",
		"/logout", "Logout",
		"/findpass","FindPass",
		"/newpass","NewPass",
		"/check/(.*)", "Check")

globals()["ctx"] = web.ctx
render = web.template.render('templates/account',
							base='../layout',
							globals=globals())

class Logout:
	def GET(self):
		login.Login.logout()
		return web.seeother(web.ctx.sitehost)

class Check:
	
	def GET(self, flag):
		if flag == "email":
			if web.ctx.user is not None:
				exist = pduser.check_email(web.input().value,web.ctx.user.u_id)
			else:
				exist = pduser.check_email(web.input().value)
			return json.dumps({"success":not exist, "message":"邮箱地址已注册"})
		elif flag == "name":
			if web.ctx.user is not None:
				exist = pduser.check_name(web.input().value,web.ctx.user.u_id)
			else:
				exist = pduser.check_name(web.input().value)
			return json.dumps({"success":not exist, "message":"昵称已存在"})

class Login:
	def GET(self):
		login.Login.logout()
		return render.login(None,web.input().get('ref','/'))
	
	def POST(self):
		post = web.input()
		if post.get('u_email') and post.get('u_pass'):	
			user = pduser.loaduser_by_email(post.u_email)
			if user and user.u_pass==md5.new(web.utf8(post.u_pass)).hexdigest():
				login.Login.encode_cookie(user.u_id)
				return web.seeother(web.ctx.sitehost+web.input().get('ref',"/"))
		return render.login(post)
	
class FindPass:
	def GET(self):
		return render.findpass(None)
	
	def POST(self):
		post = web.input()
		if post.get('u_email'):
			post.u_email = post.u_email.strip() 	
			user = pduser.loaduser_by_email(post.u_email)
			if user:
				createtime = time.time()
				row = web.Storage(f_create_time=createtime)
				row.f_hash= md5.new(str(createtime)).hexdigest()
				row.f_uemail=post.u_email
				pdfindpass.insert_by_list([row])
				XWJemail.sendfindpass(user, row.f_hash)
				return render.findpass({'code':1})
		return render.findpass({'code':0,'email':post.get('u_email')})

class NewPass:
	def GET(self):
		params = web.input()
		if params.get('v') and params.get('email'):
			row = pdfindpass.find(params.get('email'),params.get('v'))
			if (row is None) or (row.f_create_time < (time.time()-60*60*24*30)):
				#失效或者过期
				return render.newpass({'code':-1,'message':'链接过期或者失效','params':params})
		return render.newpass({'code':0,'message':'','params':params})
	
	
	def POST(self):
		params = web.input()
		if params.get('v') and params.get('email'):
			row = pdfindpass.find(params.get('email'),params.get('v'))	
			user = pduser.loaduser_by_email(params.get('email'))
			if (row is None) or (row.f_create_time < (time.time()-60*60*24*30)):
				return render.newpass({'code':-1,'message':'链接过期或者失效','params':params})
			#update info 
			
			updateinfo = web.storify({})
			updateinfo.u_pass = md5.new(params.get('u_pass')).hexdigest()
			updateinfo.u_id = user.u_id
			pduser.update_by_insert(updateinfo)
			#clear info
			pdfindpass.deleteall(params.get('email'))
			
			return render.newpass({'code':1,'message':'密码修改成功','params':params})
		return render.newpass({'code':0,'message':'','params':params})
	
class Register:
	def GET(self):
		login.Login.logout()
		return render.register(None)
	
	def POST(self):
		post = web.input()
		post.u_create_time = int(time.time())
		
		post.u_email = web.utf8(post.get('u_email'))
		post.u_name = web.utf8(post.get('u_name'))
		#change to md5
		post.u_pass = md5.new(web.utf8(post.u_pass)).hexdigest()
		try:
			idlist = pduser.insert_by_list([post])
			newid = idlist.pop()
		
			if newid: #表示注册成功
				login.Login.encode_cookie(newid) #保存注册信息
				#return web.seeother(web.ctx.sitehost+"/me/setting/basic") # go to accounts index
				return web.seeother(web.ctx.sitehost) # go to accounts index
		except:
			pass
		return render.register(post)
		
app_account = web.application(urls, locals())