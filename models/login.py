'''
Created on 2012-8-29

@author: shanfeng
'''

from utils.azdg import *
import json
import web

cookiekey = "user"
safekey = "todo"
expires = 604800 #one week

class Login:
	'''
	classdocs
	'''
	@staticmethod
	def logout():
		web.webapi.setcookie(cookiekey, "", -1,path="/")
		
		
	@staticmethod
	def decode_cookie(hashstr=None):
		if hashstr is None:
			cookies = web.webapi.cookies()
			hashstr = cookies.get(cookiekey)
			
		if hashstr:
			azdg = AzDG(safekey)
			value = azdg.decode(hashstr)
			if value:
				info = json.loads(value)
				if info.get('key') and info.get('key') == safekey:
					return info.get('id')
		return False
	
	@staticmethod		
	def encode_cookie(pid):
		key = safekey 
		azdg = AzDG(key)
		cookieinfo = azdg.encode(json.dumps({"key":key, "id":pid}))
		web.webapi.setcookie(cookiekey, cookieinfo, expires,path='/')
		return cookieinfo 
