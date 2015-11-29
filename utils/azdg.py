# -*- coding: utf-8 -*-

import base64
import hashlib
import time

default_encoding = 'utf-8'

class AzDG:
	
	"""docstring for AzDG"""
	
	cipher = '0123456789'
	charset = 'utf-8'
	def __init__(self, cipher = None):
		if cipher != None:
			self.cipher = cipher
	def getCipher(self):
		return self.cipher
	
	def cipherEncode(self, sourceText):	 
		cipherHash = hashlib.md5(self.getCipher()).hexdigest()
		cipherEncodeText = ''
		for i in range(len(sourceText)):
				cipherEncodeText = '%s%s' % (cipherEncodeText, chr(ord(sourceText[i]) ^ ord(cipherHash[i%32])))
		return cipherEncodeText

	def encode(self, sourceText, charset = 'utf-8'):
		if charset != self.charset:
				sourceText = sourceText.encode(charset)
		noise = hashlib.md5('%s' % (time.time())).hexdigest()
		encodeText = ''
		for i in range(len(sourceText)):
				encodeText = '%s%s%s' % (encodeText, noise[i%32], chr(ord(sourceText[i]) ^ ord(noise[i%32])))
		return base64.b64encode(self.cipherEncode(encodeText))
		
	def decode(self, sourceText, charset = 'utf-8'):
		decodeSourceText = self.cipherEncode(base64.b64decode(sourceText))			  
		textLength = len(decodeSourceText)
		decodeText = ''
		i = 0
		while i < textLength:
				decodeText = '{0}{1}'.format(decodeText, chr(ord(decodeSourceText[i]) ^ ord(decodeSourceText[i+1])))
				i = i + 2
		if charset != self.charset:
				decodeText =  unicode(decodeText, charset).encode(self.charset)
		return decodeText