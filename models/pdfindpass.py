# -*- coding: utf-8 -*-
from basemodel import *
import md5

class PDfindpass(BaseModel):
	table_name = 'pd_find_pass'
	db_name = web.config.write_db_name
	
	def find(self,email,hash):
		rows = self.reader().select(self.table_name,where="f_uemail=$email and f_hash=$hash",vars={'email':email,'hash':hash})
		for row in rows:
			return row
		return None

	def delete(self,email,hash):
		self.writer().delete(self.table_name,where="f_uemail=$email and f_hash=$hash",vars={'email':email,'hash':hash})
		
	def deleteall(self,email):
		self.writer().delete(self.table_name,where="f_uemail=$email",vars={'email':email})
		
	def insert_by_list(self, rows):
		self.writer().multiple_insert(self.table_name, rows)

pdfindpass = PDfindpass() #public instance

