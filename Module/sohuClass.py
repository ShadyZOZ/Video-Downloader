#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
from Library import toolClass

class ChaseSohu :

	def __init__ (self) :
		self.videoLink     = ''
		self.fileUrlPrefix = 'http://m.tv.sohu.com/phone_playinfo?vid='
		self.fileUrlSuffix = '.m3u8?plat=15&pt=6&prod=ott&pg=1&ch=v&qd=816'
		self.urlSuffix     = '&start=0&end=10000000000&'
		self.videoTypeList = {'n': 'nor', 'h': 'hig', 's': 'sup'}
		self.videoType     = 's'
		self.Tools         = toolClass.Tools()

	def getVideoPlaylist (self) :
		pageBody = self.Tools.getPage(self.videoLink, decoded=False)
		result = re.findall(r'''playlistId="\d+''', pageBody)
		playlistId = result[0][12:]
		playlistUrl = 'http://pl.hd.sohu.com/videolist?playlistid=' + playlistId
		pageBody = self.Tools.getPage(playlistUrl)
		rawplaylist = pageBody
		playlist = json.loads(rawplaylist)
		title = playlist['albumName']
		tvlist = {'title': title, 'video': []}
		for item in playlist['videos']:
			self.videoLink = item['pageUrl']
			downloadUrl = self.__chaseUrl()['msg']
			tvlist['video'].append({'name': item['showName'].replace(' ', '').replace('/', ''), 'url': self.videoLink, 'downloadUrl': downloadUrl})
		return tvlist

	def __chaseUrl (self) :
		result = {'stat': 0, 'msg': ''}
		videoID = self.__getVideoID(self.videoLink)

		if videoID :
			confgFileUrl = self.fileUrlPrefix + str(videoID)
			fileUrl = self.__getVideoFileUrl(confgFileUrl)
			if fileUrl != False :
				listFile = self.__getFileList(fileUrl)
				if len(listFile) > 0:
					result['msg'] = listFile
				else:
					result['stat'] = 1
			else :
				result['stat'] = 1
		else :
			result['stat'] = 2

		return result

	def __getVideoID(self, link):
		pageBody = self.Tools.getPage(link, decoded=False)

		result = re.findall(r"\s+?vid\s*?=\s*?[\"\']\s*?(.*)\s*?[\"\']", pageBody)
		if len(result) > 0 :
			videoID = result[0]
		else :
			result = re.findall(r"\s+?vid\s*?:\s*?[\"\']\s*?(.*)\s*?[\"\']", pageBody)
			if len(result) > 0 :
				videoID = result[0]
			else :
				videoID = False

		return videoID

	def __getVideoFileUrl (self, confgFileUrl, siteType = 1) :
		if siteType != 1:
			confgFileUrl = confgFileUrl + '&site=' + str(siteType)
		pageBody = self.Tools.getPage(confgFileUrl)
		info = json.JSONDecoder().decode(pageBody)

		if info.has_key('data') :
			if len(info['data']['urls']['m3u8'][self.videoTypeList[self.videoType]]) > 0 :
				fileUrl = info['data']['urls']['m3u8'][self.videoTypeList[self.videoType]][0]
			else :
				fileUrl = info['data']['urls']['m3u8'][self.videoTypeList['n']][0]

			fileUrlBase = re.findall(r"^(.*)\.m3u8\?", fileUrl)
			if len(fileUrlBase) > 0 :
				fileUrl = fileUrlBase[0] + self.fileUrlSuffix
			else :
				fileUrl = False
		else :
			fileUrl = self.__getVideoFileUrl(confgFileUrl, 2)

		return fileUrl

	def __getFileList (self, fileUrl) :
		pageBody = self.Tools.getPage(fileUrl)
		data = self.__formatList(pageBody)

		return data

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
