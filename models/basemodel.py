from stmemcache import *
import md5

class BaseModel:
	"""
	use for base model:
		reader
		writer
	"""
	db_name="" 
	table_name=""
	
	readconnct=None
	writeconnct=None

	def __init__(self):
		pass

	@staticmethod
	def memdel(key):
		return pcacheclient.delete(key)

	@staticmethod
	def memget(key):
		return pcacheclient.get(key)

	@staticmethod
	def memset(key,value,expires=600):
		pcacheclient.set(key,value,expires,102400)

	@staticmethod
	def expires():
		return 60*10		
	
	def rowcount(self,iscache=True):
		mkey=self.create_pri_cache_key(rowcount="")	
		ret=self.memget(mkey)
		if not iscache or not ret:
			rows = self.reader().select(self.table_name, what="count(1) as count")
			ret=0
			for row in rows:
				ret=row.count
				break
			self.memset(mkey,ret)
		return ret


	def reader(self):
		if self.readconnct:
			return self.readconnct
		else:
			self.readconnct=web.database(dbn=web.config.db_style,
							db=self.db_name,
							user=web.config.db_reader,
							pw=web.config.db_pass,
							port=web.config.db_port,
							host=web.config.db_host)
			return self.readconnct
		
	def writer(self):
		if self.writeconnct:
			return self.writeconnct
		else:
			self.writeconnct=web.database(dbn=web.config.db_style, 
							db=self.db_name,
							user=web.config.db_writer, 
							pw=web.config.db_pass,
							port=web.config.db_port,
							host=web.config.db_host)
			return self.writeconnct

	def create_pri_cache_key(self,**keyword):
		keystr=[self.db_name+"_"+self.table_name]
		for k in keyword:
			keystr.append(k+"_"+str(keyword[k]))
		return md5.new("_".join(keystr)).hexdigest()
