#!/usr/bin/env python
# coding: utf-8
import web
import math
import sys
import re
from models.pdtodo import *
from models.pduser import *

default_encoding = 'utf-8' 
if sys.getdefaultencoding() != default_encoding: 
    reload(sys) 
    sys.setdefaultencoding(default_encoding) 
    
urls = (
    '/retest', 'ReTest',
)

globals()["ctx"] = web.ctx
render = web.template.render('templates/tool',
                            base='../layout',
                            globals=globals())
class ReTest:
    def GET(self):
        return render.retest(None, None, None, None)
    
    def POST(self):
        post = web.input(_unicode=False)
        
        if not post.get('re_text'):
            return render.retest(None, None, None, "没有需要测试的文本内容")
        
        if not post.get('re_patterns'): 
            return render.retest(None, None, None, "没有需要测试的正则表达式")
        re_text =  post.get('re_text')
        re_patterns = post.get('re_patterns')
        
        re_patterns_list = re.split(r"[~\r\n]+", re_patterns)
        re_patterns_list = filter(lambda x: x != "", re_patterns_list)
        
        return_text = return_test_patterns(re_text, re_patterns_list)
        return render.retest(re_text, re_patterns, return_text, None)

       
def return_test_patterns(text, patterns=[]):
    return_list = []
    for pattern in patterns:
        str = ""
        #print 'Pattern %r\n' % (pattern)
        str += 'Pattern %s\n' % (pattern)
        #print '  %r\n' % text
        str += '%s\n' % text
        for match in re.finditer(pattern, text):
            s = match.start()
            e = match.end()
            substr = text[s:e]
            n_backslashes = text[:s].count('\\')
            prefix = '.' * (s + n_backslashes)
            #print '  %s%r\n' % (prefix, substr)
            str += '%s%s\n' % (prefix, substr)
        return_list.append(str)
    return return_list

def logininfo_hook():
    if web.ctx.user is None:
        # return web.seeother(web.ctx.sitehost)
        return web.seeother("/account/login")

app_tool = web.application(urls, locals())

# app_index.add_processor(web.loadhook(logininfo_hook))
