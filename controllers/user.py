# -*- coding: utf-8 -*-
'''
Created on 2012-8-27

@author: shanfeng
'''
import web

urls = ("/like/(.*)", "Like",
	"/comment/(.*)", "Comment",
	"/(.*)", "User")

render = web.template.render('templates/player',
							base='../layout',
							globals={"ctx":web.ctx})		
	

class Comment:
	def GET(self,pid):
		
		pid= int(pid)
		
		if pid:
			player = pstplayer.load_by_id(pid)
			if player is not None:
				params = web.input(page=0)
				page = int(params.get("page"))
				pagesize = 10 
				
				toys = pstcomment.player_comments(player.p_id,page,pagesize)
				total = pstcomment.player_comments_count(player.p_id)
				totalpage=math.ceil(total/pagesize)
				if totalpage*pagesize<total:
					totalpage=totalpage+1
					
				player.toptags = psttag.get_player_hot_tags(player.p_id)
				
				return render.comment(player,toys,page,pagesize,int(totalpage),total)
				
		return web.seeother(web.ctx.sitehost)		

class Like:
	def GET(self,pid):
		
		pid= int(pid)
		
		if pid:
			player = pstplayer.load_by_id(pid)
			if player is not None:
				params = web.input(page=0)
				page = int(params.get("page"))
				pagesize = 10 
				
				toys = pstlike.player_liked_toys(player.p_id,page,pagesize)
				total = pstlike.player_like_count(player.p_id)
				totalpage=math.ceil(total/pagesize)
				if totalpage*pagesize<total:
					totalpage=totalpage+1
					
				player.toptags = psttag.get_player_hot_tags(player.p_id)
				
				return render.like(player,toys,page,pagesize,int(totalpage),total)
				
		return web.seeother(web.ctx.sitehost)


class Player:
	def GET(self,pid):
		
		pid= int(pid)
		
		if pid:
			player = pstplayer.load_by_id(pid)
			if web.ctx.player is not None and (web.ctx.player.p_id == pid):
				return web.seeother(web.ctx.sitehost+"/me")
			if player is not None:
				params = web.input(page=0)
				page = int(params.get("page"))
				pagesize = 10 
				
				toys = psttoy.toy_with_pid(player.p_id,page,pagesize,iscache=False)
				total = psttoy.row_count_with_pid(player.p_id)
				totalpage=math.ceil(total/pagesize)
				if totalpage*pagesize<total:
					totalpage=totalpage+1
					
				player.toptags = psttag.get_player_hot_tags(player.p_id)
				
				return render.player(player,toys,page,pagesize,int(totalpage),total)
				
		return web.seeother(web.ctx.sitehost)

	
app_user = web.application(urls, locals())
