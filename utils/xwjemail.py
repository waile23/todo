# coding: utf-8
'''
Created on 2012-8-30

@author: shanfeng
'''
import smtplib
from email.mime.text import MIMEText
import urllib
import web

class XWJemail:
	'''
	classdocs
	'''
	def __init__(self, params):
		'''
		Constructor
		'''
		pass
	
	@staticmethod
	def sendfindpass(user,hash):
		link = "%s/account/newpass?%s" %(web.ctx.sitehost,urllib.urlencode({'email':user.u_email,"v":hash})) 
		mail_body = """
<html>
<head></head>
<body>
<h4>%s,你好</h4>
您刚才在 liulin.info 申请了找回密码。<br>
请点击下面的链接来重置密码：<br>
<a href="%s">%s</a><br>
如果无法点击上面的链接，您可以复制该地址，并粘帖在浏览器的地址栏中访问。<br>
</body>
</html>
					""" % (web.utf8(user.u_name),link,link)
		#mail_body = web.utf8(mail_body)
		
		if isinstance(mail_body,unicode):
			mail_body = str(mail_body)
		mail_from = "liulin.info<wukong10086@163.com>"
		mail_to = user.u_email
		mail_subject = 'liulin.info重置密码邮件'
		msg = MIMEText(mail_body,'html','utf-8')
		#msg=MIMEText(mail_body,'html')
		
		if not isinstance(mail_subject,unicode):
			mail_subject = unicode(mail_subject)
			
		msg['Subject']= mail_subject
		msg['From']=mail_from
		msg['To'] = mail_to
		msg["Accept-Language"]="zh-CN"
		msg["Accept-Charset"]="ISO-8859-1,utf-8"
		smtp=smtplib.SMTP()
		smtp.connect('smtp.163.com')
		smtp.login('wukong10086@163.com','831112')
		smtp.sendmail(mail_from,mail_to,msg.as_string())
		smtp.quit()
		
		
	def sendMail(mailto,subject,body,format='plain'):
	    if isinstance(body,unicode):
	        body = str(body)
	
	    me= ("%s<"+fromMail+">") % (Header(_mailFrom,'utf-8'),)
	    msg = MIMEText(body,format,'utf-8')
	    if not isinstance(subject,unicode):
	        subject = unicode(subject)
	    msg['Subject'] = subject
	    msg['From'] = me
	    msg['To'] = mailto
	    msg["Accept-Language"]="zh-CN"
	    msg["Accept-Charset"]="ISO-8859-1,utf-8"
	    try:
	        s = smtplib.SMTP()
	        s.connect(host)
	        s.login(user,password)
	        s.sendmail(me, mailto, msg.as_string())
	        s.close()
	        return True
	    except Exception, e:
	        print str(e)
	        return False