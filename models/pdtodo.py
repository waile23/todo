#!/usr/bin/env python
# coding: utf-8

from basemodel import *
import math
from datetime import datetime

class PDtodo(BaseModel):
    table_name="pd_todo"
    db_name = web.config.write_db_name
    
    def get_by_id(self, id):
        s = self.reader().select(self.table_name, where='t_id=$id', vars={'id':id})
        if not s:
            return False
        return s[0]
    
    def get_commond(self, title):
        return '@ll#h'
     
    def new(self, uid, title): 
        commond = self.get_commond(title)
        self.writer().insert(self.table_name, t_title=title, t_create_uid=uid, t_share=0, t_commond=commond, t_create_date=datetime.now())
    
    def finish(self, uid, id, finished):
        self.writer().update(self.table_name, t_finished=finished, t_finished_uid=uid, t_finished_date=datetime.now(), where='t_id=$id', vars={'id':id})
        
    def share(self, id, share):
        self.writer().update(self.table_name, t_share=share, where='t_id=$id', vars={'id':id})
        
    def edit(self, id, title):
        commond = self.get_commond(title)
        self.writer().update(self.table_name, t_title=title, t_commond=commond, where='t_id=$id', vars={'id':id})
    
    def delete(self, id):
        self.writer().delete(self.table_name, where='t_id=$id', vars={'id':id})

    def todo_order_by_all(self, page=0, size=10):
        sql = "select pt.*, pu.u_name from pd_todo pt left join pd_user pu on pt.t_create_uid = pu.u_id where pt.t_share = 1 order by pt.t_finished asc, pt.t_create_date desc, pt.t_finished_date limit $limit offset $offset"
        #todos = db.select(tb, where="TO_DAYS(NOW()) - TO_DAYS(post_date) < " + str(daterange), order='finished asc, id asc', limit=size, offset=page*size)
        todos = self.reader().query(sql, vars={"offset":page*size,"limit":size})
        #todos = self.reader().select(self.table_name, order='t_finished asc, t_create_date desc, t_finished_date', limit=size, offset=page*size)
        return todos 
    
    def todo_rowcount_by_all(self):
        sql = "select count(1) as count from pd_todo pt left join pd_user pu on pt.t_create_uid = pu.u_id where pt.t_share = 1"
        #rows = db.select(tb, what="count(1) as count", where="TO_DAYS(NOW()) - TO_DAYS(post_date) < " + str(daterange))
        rows = self.reader().query(sql)
        #rows = self.reader().select(self.table_name, what='count(1) as count')
        return rows[0].count
    
    def todo_order_by_user(self, uid, page=0, size=10):
        sql= "select pt.*, pu.u_name from pd_todo pt left join pd_user pu on pt.t_create_uid = pu.u_id where pt.t_create_uid = $uid and pt.t_share = 1 order by pt.t_finished asc, pt.t_create_date desc, pt.t_finished_date limit $limit offset $offset"
        #todos = db.select(tb, where="TO_DAYS(NOW()) - TO_DAYS(post_date) < " + str(daterange), order='finished asc, id asc', limit=size, offset=page*size)
        todos = self.reader().query(sql, vars={'uid':uid, "offset":page*size, "limit":size})
        #todos = self.reader().select(self.table_name, order='t_finished asc, t_create_date desc, t_finished_date', limit=size, offset=page*size)
        return todos 
    def todo_rowcount_by_user(self, uid):
        sql = "select count(1) as count from pd_todo pt left join pd_user pu on pt.t_create_uid = pu.u_id where pt.t_create_uid = $uid and pt.t_share = 1"
        #rows = db.select(tb, what="count(1) as count", where="TO_DAYS(NOW()) - TO_DAYS(post_date) < " + str(daterange))
        rows = self.reader().query(sql, vars={'uid':uid})
        #rows = self.reader().select(self.table_name, what='count(1) as count')
        return rows[0].count
        
    def todo_order_by_login_user(self, uid, page=0, size=10):
        #todos = db.select(tb, where="TO_DAYS(NOW()) - TO_DAYS(post_date) < " + str(daterange), order='finished asc, id asc', limit=size, offset=page*size)
        todos = self.reader().select(self.table_name, where='t_create_uid=$uid', order='t_finished asc, t_create_date desc, t_finished_date', vars={'uid':uid}, limit=size, offset=page*size)
        return todos 
    
    def todo_rowcount_by_login_user(self, uid):
        #rows = db.select(tb, what="count(1) as count", where="TO_DAYS(NOW()) - TO_DAYS(post_date) < " + str(daterange))
        rows = self.reader().select(self.table_name, what='count(1) as count', where='t_create_uid=$uid', vars={'uid':uid})
        return rows[0].count
    
pdtodo = PDtodo() #public instance    
