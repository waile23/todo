import memcache
import web
import config

class STmemcache:


	@staticmethod
	def getclient(host=web.config.mem_host):
		return memcache.Client([host],debug=0)
	
pcacheclient = STmemcache.getclient()

