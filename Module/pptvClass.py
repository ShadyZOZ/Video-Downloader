#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import json
import xmltodict
from random import random
from Library import toolClass

class ChasePptv :

	def __init__ (self) :
		self.videoLink     = ''
		self.ppiUrl = 'http://tools.aplusapi.pptv.com/get_ppi'
		self.fileUrlPrefix = 'http://web-play.pptv.com/webplay3-0-'
		self.fileUrlSuffix = '.xml?type=web.fpp'
		self.urlSuffix     = '&s=0&e=10000000000'
		self.videoTypeList = {'n': 'mp4', 'h': 'mp4', 's': 'mp4'}
		self.videoType     = self.videoTypeList['s']
		self.Tools         = toolClass.Tools()
		self.tempCookie = ''

	def getVideoPlaylist (self) :
		pageBody = self.Tools.getPage(self.videoLink)
		# pid = self.Tools.r1(r'"pid":\d+', pageBody)
		pid = re.findall(r'"pid":\d+', pageBody)[0][6:]
		url = self.fileUrlPrefix + pid + self.fileUrlSuffix
		pageBody2 = self.Tools.getPage(url)
		title = self.Tools.r1(r'nm="([^"]+)"', pageBody2)
		self.tempCookie = self.__getPpi()
		playlistUrl = 'http://v.pptv.com/show/videoList?&cb=videoList&pid=%s&pageSize=1000&cat_id=2' % pid
		pageBody = self.Tools.getPage(playlistUrl, {'Cookie': self.tempCookie})
		rawplaylist = pageBody[14:-2]
		playlist = json.loads(rawplaylist)
		tvlist = {'title': title, 'video': []}
		for item in playlist['data']['list']:
			if not item['isTrailer'] :
				self.videoLink = item['url']
				downloadUrl = self.__chaseUrl()['msg']
				tvlist['video'].append({'name': item['title'].replace(' ', '').replace('/', ''), 'url': self.videoLink, 'downloadUrl': downloadUrl})
			break
		return tvlist


	def __chaseUrl (self) :
		result = {'stat': 0, 'msg': ''}
		videoID = self.__getVideoID(self.videoLink)

		if videoID :
			fileUrl = self.fileUrlPrefix + str(videoID) + self.fileUrlSuffix
			listFile = self.__getFileList(fileUrl)
			if len(listFile) > 0:
				result['msg'] = listFile
			else:
				result['stat'] = 1
		else :
			result['stat'] = 2

		return result

	def __getVideoID(self, link):
		pageBody = self.Tools.getPage(link)

		result = re.findall(r'''{"id":\d+''', pageBody)
		if len(result) > 0 :
			videoID = result[0][6:]
		else :
			videoID = False

		return videoID

	def __getFileList (self, fileUrl) :
		print fileUrl
		pageBody = self.Tools.getPage(fileUrl)

		data = self.__formatList(pageBody)

		return data

	def  __formatList (self, data):
		j = xmltodict.parse(data)
		ip = j['root']['dt']['sh']
		# k = self.Tools.r1(r'<key expire=[^<>]+>([^<>]+)</key>', data)
		rid = j['root']['channel']['@rid']

		st = j['root']['dt']['st'][:-4]
		st = time.mktime(time.strptime(st)) * 1000 - 60 * 1000 - time.time() * 1000
		st += time.time() * 1000
		st = st / 1000

		key = self.__constructKey(st)

		total = len( j['root']['dragdata']['sgm'])

		urls = []
		for i in range(total) :
			# url = "http://ccf.pptv.com/%d/%s?key=%s&fpp.ver=1.3.0.4&k=%s&type=web.fpp" % (i, rid, key, k)
			url = 'http://%s/%s/%s?key=%s' % (ip, i, rid, key)
			print url
			urls.append(url)

		return urls

	def __getPpi (self) :
		pageBody = self.Tools.getPage(self.ppiUrl)

		return pageBody[2:-2].replace('"', '').replace(':', '=')

	def __str2hex (self, s) :
		r = ''
		for i in s[:8] :
			t = hex(ord(i))[2:]
			if len(t) == 1 :
				t = '0' + t
			r += t
		for i in range(16) :
			r += hex(int(15 * random()))[2:]
		return r

	def __rot (self, k, b) :
		if k >= 0 :
			return k >> b
		elif k < 0 :
			return (2 ** 32 + k) >> b
		pass

	def __lot (self, k, b) :
		return (k << b) % (2 ** 32)

	def __getkey(self, s) :
		#returns 1896220160
		l2 = [i for i in s]
		l4 = 0
		l3 = 0
		while l4 < len(l2) :
			l5 = l2[l4]
			l6 = ord(l5)
			l7 = l6 << ((l4 % 4) * 8)
			l3 = l3 ^ l7
			l4 += 1
		return l3

	def __encrypt (self, arg1, arg2) :
		delta = 2654435769
		l3 = 16
		l4 = self.__getkey(arg2)
		# l4 = 1896220160
		l8 = [i for i in arg1]
		l10 = l4
		l9 = [i for i in arg2]
		l5 = self.__lot(l10, 8) | self.__lot(l10, 24)
		# l5 = 101056625
		l6 = self.__lot(l10, 24) | self.__rot(l10, 16)
		# l6 = 100692230
		l7 = self.__lot(l10, 24) | self.__rot(l10, 8)
		# l7 = 7407110
		l11 = ''
		l12 = 0
		l13 = ord(l8[l12]) << 0
		l14 = ord(l8[l12 + 1]) << 8
		l15 = ord(l8[l12 + 2]) << 16
		l16 = ord(l8[l12 + 3]) << 24
		l17 = ord(l8[l12 + 4]) << 0
		l18 = ord(l8[l12 + 5]) << 8
		l19 = ord(l8[l12 + 6]) << 16
		l20 = ord(l8[l12 + 7]) << 24

		l21 = (((0 | l13) | l14) | l15) | l16
		l22 = (((0 | l17) | l18) | l19) | l20

		l23 = 0
		l24 = 0
		while l24 < 32 :
			l23 = (l23 + delta) % (2 ** 32)
			l33 = (self.__lot(l22, 4) + l4) % (2 ** 32)
			l34 = (l22 + l23) % (2 ** 32)
			l35 = (self.__rot(l22, 5) + l5) % (2 ** 32)
			l36 = (l33 ^ l34) ^ l35
			l21 = (l21 + l36) % (2 ** 32)
			l37 = (self.__lot(l21, 4) + l6) % (2 ** 32)
			l38 = (l21 + l23) % (2 ** 32)
			l39 = (self.__rot(l21, 5)) % (2 ** 32)
			l40 = (l39 + l7) % (2 ** 32)
			l41 = ((l37 ^ l38) % (2 ** 32) ^ l40) % (2 ** 32)
			l22 = (l22 + l41) % (2 ** 32)

			l24 += 1

		l11 += chr(self.__rot(l21, 0) & 0xff)
		l11 += chr(self.__rot(l21, 8) & 0xff)
		l11 += chr(self.__rot(l21, 16) & 0xff)
		l11 += chr(self.__rot(l21, 24) & 0xff)
		l11 += chr(self.__rot(l21, 0) & 0xff)
		l11 += chr(self.__rot(l21, 8) & 0xff)
		l11 += chr(self.__rot(l21, 16) & 0xff)
		l11 += chr(self.__rot(l21, 24) & 0xff)

		return l11

	def __constructKey(self, st) :
		loc1 = hex(int(st))[2:] + (16 - len(hex(int(st))[2:])) * '\x00'
		SERVER_KEY = 'qqqqqww' + '\x00' * 9
		res = self.__encrypt(loc1, SERVER_KEY)
		return self.__str2hex(res)

	# def __r1(self, pattern, text):
	# 	m = re.search(pattern, text)
	# 	if m:
	# 		return m.group(1)
