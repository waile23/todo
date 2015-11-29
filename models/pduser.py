# -*- coding: utf-8 -*-
from basemodel import *
import md5
import math
import sys

class PDuser(BaseModel):
	'''model autocreate by createModel'''
	table_name = 'pd_user'
	#db_name = 'todo_local'
	db_name = web.config.write_db_name
	
	
	def _format_user(self, row):
		if hasattr(row, 'u_logo'):
			if not row.u_logo:
				row.u_logo = "/static/img/default_logo.png"
		return row
	
	def load_by_id(self, id, iscache=True, isformat=True):
		mkey = self.create_pri_cache_key(u_id=id)
		ret = BaseModel.memget(mkey)
		if not iscache or not ret:
			rows = self.reader().select(self.table_name, where="u_id=$uid", vars={"uid":id})
			for row in rows:
				if isformat:
					ret = self._format_user(row)
				else:
					ret = row
				break 
			BaseModel.memset(mkey, ret)
		return ret
		
	def check_name(self, name,loginid=0):
		ret = self.reader().select(self.table_name, where="u_name=$name and u_id not in ($loginid)", vars={"name":name,"loginid":loginid})
		for v in ret:
			return True
		return False
	
	def check_name_count(self, name):
		ret = self.reader().select(self.table_name,what="count(1) as count", where="u_name=$name", vars={"name":name})
		for v in ret:
			return v.count
		return 0


	def check_email(self, email,loginid=0):
		ret = self.reader().select(self.table_name, where="u_email=$email and u_id not in ($loginid)", vars={"email":email,"loginid":loginid})
		for v in ret:
			return True
		return False
	
	def user_list(self,page=0,size=15,iscache=True,isformat=True):
		mkey=md5.new(self.__class__.__name__+"."+sys._getframe().f_code.co_name+"_page_"+str(page)+"_size_"+str(size)).hexdigest()
		ret=BaseModel.memget(mkey)
		if not iscache or not ret:
			ret=[]
			ret_i = self.reader().select(self.table_name,order="u_create_time desc",limit=size,offset=page*size)
			for row in ret_i:
				if isformat:
					ret.append(self._format_user(row))
				else:
					ret.append(row)
			BaseModel.memset(mkey,ret)
		return ret
		
	def loaduser_by_email(self, email):
		rows = self.reader().select(self.table_name, where="u_email=$email", vars={"email":email})
		ret = None
		for row in rows:
			ret = row
			break 
		return ret
		
	
	def loaduser_by_social(self, fr, auth):
		
		rows = self.reader().select(self.table_name, where="u_from='" + fr + "' and u_auth='" + auth + "'")
		ret = None
		for row in rows:
			ret = row
			break 
		return ret
	
	def insert_by_list(self, rows):
		ret = self.writer().multiple_insert(self.table_name, rows)
		for i in ret:
			self.memdel(self.create_pri_cache_key(u_id=i))
		return ret
	
	def update_by_insert(self, row):
		sql = ["update"]
		sql.append(self.table_name)
		sql.append("set")
		tmp = []
		for k in row:
			tmp.append(k + "=$" + k)
		sql.append(",".join(tmp))
		sql.append("where u_id=$u_id")
		
		sqlstr = " ".join(sql)
		self.writer().query(sqlstr, row)
		self.memdel(self.create_pri_cache_key(u_id=row.u_id))
		
pduser = PDuser() #public instance

