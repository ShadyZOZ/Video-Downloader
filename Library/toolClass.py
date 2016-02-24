#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import cookielib
import StringIO
import re

class Tools :

	def __init__ (self) :
		self.cookies = None

	# def getPage (self, url, requestHeader = []) :
	# 	resultFormate = StringIO.StringIO()
	#
	# 	curl = pycurl.Curl()
	# 	curl.setopt(pycurl.URL, url.strip())
	# 	curl.setopt(pycurl.ENCODING, 'gzip,deflate')
	# 	curl.setopt(pycurl.HEADER, 1)
	# 	curl.setopt(pycurl.TIMEOUT, 10)
	# 	if len(requestHeader) > 0 :
	# 		curl.setopt(pycurl.HTTPHEADER, requestHeader)
	# 	curl.setopt(pycurl.WRITEFUNCTION, resultFormate.write)
	# 	curl.perform()
	# 	headerSize = curl.getinfo(pycurl.HEADER_SIZE)
	# 	curl.close()
	#
	# 	header = resultFormate.getvalue()[0 : headerSize].split('\r\n')
	# 	body = resultFormate.getvalue()[headerSize : ]
	#
	# 	return header, body

	def getPage(self, url, headers={}, decoded=True):
		req = urllib2.Request(url, headers=headers)
		if self.cookies:
			self.cookies.add_cookie_header(req)
			req.headers.update(req.unredirected_hdrs)
		try :
			response = urllib2.urlopen(req)
		except Exception, e :
			print ('连接出错，重试一次')
			response = urllib2.urlopen(req)
		body = response.read()

		# Handle HTTP compression for gzip and deflate (zlib)
		content_encoding = response.info().getheader('Content-Encoding')
		if content_encoding == 'gzip':
			body = ungzip(body)
		elif content_encoding == 'deflate':
			body = undeflate(body)

		# Decode the response body
		if decoded:
			match = re.search(r'charset=([\w-]+)', response.info().getheader('Content-Type'))
			if match is not None:
				charset = match.group(1)
				body = body.decode(charset)
			else:
				body = body.decode('utf-8')

		return body

	def getCookie (self, url) :
		cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		r = opener.open(url)
		# print ('cj', cj)
		# print ('r', r)
		return cj

	def xor (self, x, y, base = 32) :
		stat = True
		if x >= 0 :
			x = str(bin(int(str(x), 10)))[2:]
			for i in xrange(0, base - len(x)):
				x = '0' + x
		else :
			x = str(bin(int(str(x + 1), 10)))[3:]
			for i in xrange(0, base - len(x)):
				x = '0' + x
			t = ''
			for i in xrange(0,len(x)):
				if x[i] == '1' :
					t = t + '0'
				else :
					t = t + '1'
			x = t
		if y >= 0 :
			y = str(bin(int(str(y), 10)))[2:]
			for i in xrange(0, base - len(y)):
				y = '0' + y
		else :
			y = str(bin(int(str(y + 1), 10)))[3:]
			for i in xrange(0, base - len(y)):
				y = '0' + y
			t = ''
			for i in xrange(0,len(y)):
				if y[i] == '1' :
					t = t + '0'
				else :
					t = t + '1'
			y = t
		t = ''
		for i in xrange(0, base):
			if x[i] == y[i] :
				t = t + '0'
			else :
				t = t + '1'
		x = t
		if x[0] == '1' :
			stat = False
			t = ''
			for i in xrange(0,len(x)):
				if x[i] == '1' :
					t = t + '0'
				else :
					t = t + '1'
			x = t
		r = int(str(x), 2)
		if stat == False :
			r = 0 - r - 1

		return r

	def rotate (self, x, y, w, base = 32) :
		stat = True
		if x >= 0 :
			x = str(bin(int(str(x), 10)))[2:]
			for i in xrange(0, base - len(x)):
				x = '0' + x
		else :
			x = str(bin(int(str(x + 1), 10)))[3:]
			for i in xrange(0, base - len(x)):
				x = '0' + x
			t = ''
			for i in xrange(0,len(x)):
				if x[i] == '1' :
					t = t + '0'
				else :
					t = t + '1'
			x = t
		if y >= base :
			y = y % base
		for i in xrange (0, y) :
			if w != 'r+' :
				x = x[0] + x + '0'
			else :
				x = '0' + x + '0'
		if w == 'r' or w == 'r+' :
			x = x[0 : base]
		else :
			x = x[(len(x) - base) : ]
		if x[0] == '1' :
			stat = False
			t = ''
			for i in xrange(0,len(x)):
				if x[i] == '1' :
					t = t + '0'
				else :
					t = t + '1'
			x = t
		r = int(str(x), 2)
		if stat == False :
			r = 0 - r - 1

		return r

	def r1(self, pattern, text):
		m = re.search(pattern, text)
		if m:
			return m.group(1)
