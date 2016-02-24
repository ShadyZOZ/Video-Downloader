#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
import random
import math
import time
import urllib2
from Library import toolClass
from bs4 import BeautifulSoup

class ChaseLetv :

	def __init__ (self) :
		self.videoLink     = ''
		self.fileUrlPrefix = 'http://api.letv.com/mms/out/video/playJsonH5?platid=3&splatid=301&tss=ios&domain=m.letv.com'
		self.urlSuffix     = '&start=0&end=10000000000&'
		self.videoTypeList = {'n': '1000', 'h': '1300', 's': 'mp4'}
		self.videoType     = 's'
		self.Tools         = toolClass.Tools()

	def getVideoPlaylist (self) :
		pageHeader, pageBody = self.Tools.getPage(self.videoLink, decoded=False)
		cid = re.findall(r'cid: \d+', pageBody)[0][5:]
		pid = re.findall(r'pid: \d+', pageBody)[0][5:]
		playlistUrl = 'http://api.letv.com/mms/out/album/videos?id=%s&cid=%s&platform=pc' % (pid, cid)
		# pageHeader, pageBody = self.Tools.getPage(playlistUrl)
		p = urllib2.urlopen(playlistUrl)
		rawplaylist = p.read().decode('UTF-8')
		playlist = json.loads(rawplaylist)
		soup = BeautifulSoup(pageBody, "html.parser", from_encoding='utf-8')
		title = soup.find(attrs={"name": "irAlbumName"})
		# title = 'lzxxdn'
		print title['content']
		tvlist = {'title': title['content'], 'video': []}
		print len(playlist['data'][:21])
		for item in playlist['data'][:21]:
			self.videoLink = item['url']
			print self.videoLink
			downloadUrl = self.__chaseUrl()['msg']
			tvlist['video'].append({'name': item['title'].replace(' ', '').replace('/', ''), 'url': self.videoLink, 'downloadUrl': downloadUrl})
		return tvlist

	def __chaseUrl (self) :
		result = {'stat': 0, 'msg': ''}
		videoID = self.__getVideoID(self.videoLink)

		if videoID :
			# tkey = self.__auth(time.time())
			# print self.__auth(int(time.time()))
			# print self.__calcTimeKey(int(time.time()))
			# tkey = self.__calcTimeKey(int(time.time()))
			tkey = '-1051621692'
			confgFileUrl = self.fileUrlPrefix + '&id=' + str(videoID) + '&tkey=' + str(tkey)
			fileUrl = self.__getVideoFileUrl(confgFileUrl)
			if fileUrl != False :
				fileUrl = self.__getFile(fileUrl)
				if fileUrl != '' > 0:
					result['msg'] = fileUrl
				else:
					result['stat'] = 1
			else :
				result['stat'] = 1
		else :
			result['stat'] = 2

		return result

	def __getVideoID (self, link) :
		result = re.findall(r"/(\d+?)\.html", link)
		if len(result) > 0 :
			videoID = result[0]
		else :
			videoID = False

		return videoID

	def __auth (self, now) :
		key = 773625421
		now = int (now)
		result = self.__letvRor(now, key % 13)
		result = self.Tools.xor(result, key)
		result = self.__letvRor(result ,key % 17)

		return result

	def __calcTimeKey (self, t) :
		ror = lambda val, r_bits, : ((val & (2**32-1)) >> r_bits%32) |  (val << (32-(r_bits%32)) & (2**32-1))
		return ror(ror(t,773625421%13)^773625421,773625421%17)

	def __getVideoFileUrl (self, confgFileUrl) :
		# pageHeader, pageBody = self.Tools.getPage(confgFileUrl)
		p = urllib2.urlopen(confgFileUrl)
		info = json.JSONDecoder().decode(p.read())
		print info
		# url = str(info['playurl']['domain'][0]) + str(info['playurl']['dispatch'][self.videoTypeList[self.videoType]][0]) + '&format=1&sign=letv&expect=3000&rateid=' + self.videoTypeList[self.videoType]
		url = str(info['playurl']['domain'][0]) + str(info['playurl']['dispatch'][self.videoTypeList[self.videoType]][0])
		url = url.replace('tss=ios', 'tss=no')
		url = url.replace('splatid=101', 'splatid=104')

		return url

	def __getFile (self, fileUrl) :
		pageHeader, pageBody = self.Tools.getPage(fileUrl)

		url = ''
		if pageHeader[0] == 'HTTP/1.1 302 Moved' :
			for x in pageHeader :
				if x[:10] == 'Location: ' :
					url = x[10:]
					break

		return url

	def  __formatList (self, data) :
		result = []
		temp = []
		listContent = re.findall(r"http://(.*)\s+?", data)

		for x in listContent:
			link = re.sub(r"&start=.*?&end=.*?&", self.urlSuffix, x)
			if link not in temp :
				temp.append(link)

		linkStr = ''
		for x in temp:
			result.append('http://' + x)

		return result

	def __letvRor (self, a, b):
		i = 0
		while(i < b) :
			a = self.Tools.rotate(a, 1, 'r+') + self.Tools.rotate((a & 1), 31, 'l');
			i += 1

		return a
