#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import os
import time
import threading
import commands
import json

class FileProcesser :

	def __init__ (self) :
		self.fileUrl = ''
		self.fileList = ''
		self.title = ''
		self.savePath = ''
		# self.savePath = ''
		self.saveName = ''
		self.fileID = 0
		self.videoId = 0
		self.totalVideo = 0
		self.totalPart = 0
		self.process = ''
		self.totalTime = '00:00:00'
		self.time = 0
		self.ffmpegPath = ''
		self.settings = (os.getcwd() + '\\settings.json').encode('GBK')
		if not os.path.isfile(self.settings) :
			self.ffmpegPath = (os.getcwd() + '\\ffmpeg\\bin').encode('GBK')
			self.savePath = self.__makeSavePath()
			file = open(self.settings, 'wb')
			data = {'ffmpegPath': self.ffmpegPath, 'savePath': self.savePath}
			file.write(json.dumps(data, indent = 4))
			file.close()
		else :
			file = open(self.settings, 'rb')
			jsondate = file.read()
			data = json.loads(jsondate)
			file.close()
			self.ffmpegPath = data['ffmpegPath']
			self.savePath = data['savePath']

	def download (self, fileList, startfrom, endWith) :
		self.process = '准备中...'
		self.fileList = fileList['video'][startfrom:endWith]
		self.totalVideo = len(self.fileList)
		self.title = fileList['title']
		self.savePath = self.savePath + '\\' + fileList['title']
		p = threading.Thread(target = self.__downloadFile)
		p.start()

	def __downloadFile (self) :
		self.videoId = 1
		if not os.path.isdir(self.savePath):
			os.makedirs(self.savePath)
		for item in self.fileList :
			self.fileID = 1
			self.combineFileList = []
			self.saveName = item['name']
			self.totalPart = len(item['downloadUrl'])
			for url in item['downloadUrl']:
				# target = urllib.urlopen(url)
				try :
					target = urllib.urlopen(url)
				except Exception, e :
					self.process = '下载失败，链接打开失败'
					return 127
				header = str(target.info()).split('\n')
				for x in header :
					if x[0:12] == 'Content-Type' :
						cType = x[14:]
						break
				if 'flv' in cType :
					self.fileType = '.flv'
				elif 'mp4' in cType:
					self.fileType = '.mp4'
				else :
					self.fileType = '.mp4'
				fileName = self.savePath + '\\' + self.saveName + '_' + str(self.fileID) + self.fileType
				self.time = time.clock()
				# urllib.urlretrieve(url, fileName, reporthook = self.__report)
				try :
					urllib.urlretrieve(url, fileName, reporthook = self.__report)
				except Exception, e :
					self.process = '下载失败，文件取回失败'
					return 127
				self.combineFileList.append(fileName)
				self.fileID += 1
			if len(self.combineFileList) > 1:
				self.process = '下载完成，正在合并视频'
				self.__combineSource()
			else:
				self.process = '下载完成'
			self.videoId += 1
		self.process = '全部完成  总用时: %s' % self.totalTime

	def __report(self, count, blockSize, totalSize) :
		timeUsed = time.clock() - self.time
		downloadSize = count * blockSize / 1024.00
		if timeUsed == 0 :
			speed = 0
		else :
			speed = downloadSize / timeUsed
		if speed > 1000 :
			speed = '下载速度: %.2f MB/s' % (speed / 1024.00)
		else :
			speed = '下载速度: %.2f KB/s' % speed
		if totalSize > 0:
			percent = int(count * blockSize * 100 / totalSize)
			self.process = "正在下载视频 %d/%d part %d/%d" % (self.videoId, self.totalVideo, self.fileID, self.totalPart) + " - " + "%d%%  %s 总用时: %s" % (percent, speed, self.totalTime)
		else:
			total = "%.2f" % (count * blockSize / 1024.00 / 1024.00)
			self.process = "正在下载视频 %d/%d part %d/%d" % (self.videoId, self.totalVideo, self.fileID, self.totalPart) + " - " + "%s MB  %s 总用时: %s" % (total, speed, self.totalTime)

	def __makeSavePath (self) :
		# sysPath = self.__findSysPath()
		folder = 'download'
		savePath = os.path.join(os.getcwd(), folder)
		if not os.path.isdir(savePath):
			os.makedirs(savePath)

		return savePath

	# def __findSysPath (self) :
	# 	return os.path.join(os.path.expanduser("~"), 'Desktop')

	def __makeFileList (self) :
		outfile = open(self.savePath + '\\combineList%d' % self.fileID, 'wb')
		for filepath in self.combineFileList:
			line = "file '%s'\n" % filepath
			outfile.write(line.encode('GBK'))
		outfile.close()

	def __cleanUp (self) :
		os.remove(self.savePath + '\\combineList%d' % self.fileID)
		for file in self.combineFileList:
			os.remove(file)

	def __combineSource(self) :
		self.__makeFileList()
		cmd = '%s\\ffmpeg.exe -f concat -i %s\\combineList%d -bsf:a aac_adtstoasc -c copy %s\\%s.mp4 -y' % (self.ffmpegPath.encode('GBK'), self.savePath, self.fileID, self.savePath, self.saveName)
		os.system(cmd.encode('GBK'))
		self.__cleanUp()
		self.process = '合并完成'
