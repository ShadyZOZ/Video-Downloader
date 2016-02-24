#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter
import ttk
import tkMessageBox
import os
import sys
import time
import threading
from Module import youkuClass, tudouClass, sohuClass, letvClass, bilibiliClass, acfunClass, iqiyiClass, pptvClass
# from Module import youkuClass
# from Module import tudouClass
# from Module import sohuClass
# from Module import letvClass
# from Module import bilibiliClass
# from Module import acfunClass
# from Module import iqiyiClass
from Library import fileProcesserClass

class GUI :

	def __init__ (self) :
		self.masterTitle = 'Video Downloader'
		self.slaveTitle = 'Info'
		self.fileList = []

	def __mainWindow (self) :
		self.master = Tkinter.Tk();

		self.master.title(self.masterTitle)
		self.master.resizable(width = 'false', height = 'false')

		self.__menu()
		self.__topBox()

	def __menu (self) :
		menubar = Tkinter.Menu(self.master)

		filemenu = Tkinter.Menu(menubar, tearoff = 0)
		filemenu.add_command(label = "Info", command = self.__showInfo)
		filemenu.add_command(label = "Quit", command = self.master.quit)
		menubar.add_cascade(label = "About", menu = filemenu)

		self.master.config(menu = menubar)

	def __topBox (self) :
		self.mainTop = Tkinter.Frame(self.master, bd = 10)
		self.mainTop.grid(row = 0, column = 0, sticky = '')

		self.urlInput = Tkinter.Entry(self.mainTop, width = 50)
		self.urlInput.grid(row = 0, column = 0, padx = 5)

		s = self.__selector(self.mainTop)
		s.grid(row = 0, column = 1, padx = 5)

		self.startFromInput = Tkinter.Entry(self.mainTop, width = 5)
		self.startFromInput.grid(row = 0, column = 2, padx = 5)
		self.startFromInput.insert(0, '1')

		self.endInput = Tkinter.Entry(self.mainTop, width = 5)
		self.endInput.grid(row = 0, column = 3, padx = 5)

		# s.grid(row = 0, column = 1, padx = 5)
		self.__searchBtn()


	def __selector (self, position) :
		self.selectorVal = Tkinter.StringVar()
		self.selectorVal.set("HD")

		videoType = ['HD', '高清', '超清']

		s = ttk.Combobox(position, width = 5, textvariable = self.selectorVal, state='readonly', values = videoType)

		return s

	def __showResult (self) :
		self.mainFoot = Tkinter.Frame(self.master, bd = 10)
		self.mainFoot.grid(row = 1, column = 0, sticky = '')

		self.__searchBtn(False)
		self.resultWindow = Tkinter.Text(self.mainFoot, height = 5, width = 85, highlightthickness = 0)
		self.resultWindow.grid(row = 0, sticky = '')

		threading.Thread(target = self.__getUrl).start()

		self.dlZone = Tkinter.Button(self.mainFoot, text = '下载', command = self.__download)
		self.dlZone.grid(row = 1, column = 0, sticky = 'ew')

		self.mainFoot.update()

	def __getUrl (self):
		url = self.urlInput.get()
		result = True
		if 'youku' in url :
			getClass = youkuClass.ChaseYouku()
		elif 'sohu' in url :
			getClass = sohuClass.ChaseSohu()
		# elif 'letv' in url :
		# 	getClass = letvClass.ChaseLetv()
		# elif 'tudou' in url and 'acfun' not in url :
		# 	getClass = tudouClass.ChaseTudou()
		# elif 'bilibili' in url :
		# 	getClass = bilibiliClass.ChaseBilibili()
		# elif 'acfun' in url :
		# 	getClass = acfunClass.ChaseAcfun()
		elif 'iqiyi' in url :
			getClass = iqiyiClass.ChaseIqiyi()
		# elif 'pptv' in url :
		# 	getClass = pptvClass.ChasePptv()
		else :
			result = False

		if result :
			result = ''
			videoType = self.selectorVal.get()

			if videoType == u'HD' :
				videoType = 's'
			elif videoType == u'超清' :
				videoType = 'h'
			elif videoType == u'高清' :
				videoType = 'n'
			else :
				videoType = 's'

			getClass.videoLink = url
			getClass.videoType = videoType
			tvlist = getClass.getVideoPlaylist()
			self.fileList = tvlist
			result = tvlist['title'].encode('utf-8') + ' 共%d集' % len(tvlist['video'])
			for item in tvlist['video']:
				result += '\n%s : %s' % (item['name'].encode('utf-8'), item['url'].encode('utf-8'))

		else :
			result = '链接地址不再分析范围内！'

		self.resultWindow.insert('end', result)
		self.endInput.insert(0, str(len(tvlist['video'])))

		self.__searchBtn()

	def __download (self) :
		self.FPC = fileProcesserClass.FileProcesser()
		if len(self.fileList) > 0 :
			self.dlZone.grid_forget()
			self.dlStat = Tkinter.StringVar()
			self.dlZone = Tkinter.Label(self.mainFoot, textvariable = self.dlStat, width = 30, anchor = 'center')
			self.dlZone.grid(row = 1, column = 0, sticky = 'ew')

			startfrom = int(self.startFromInput.get())
			endWith = int(self.endInput.get())
			self.FPC.download(self.fileList, startfrom - 1, endWith)
			self.time = time.clock()
			self.__dlZoneUpdate()

	def __dlZoneUpdate (self) :
		self.dlStat.set(self.FPC.process)

		self.timer = self.master.after(1000, self.__dlZoneUpdate)
		self.__updateUsedTime()

	def __updateUsedTime (self) :
		timeDiff = int(round(time.clock() - self.time))
		second = timeDiff % 60
		if second < 10 :
			second = '0' + str(second)
		else :
			second = str(second)
		minute = timeDiff / 60 % 60
		if minute < 10 :
			minute = '0' + str(minute)
		else :
			minute = str(minute)
		hour = timeDiff / 3600
		if hour < 10 :
			hour = '0' + str(hour)
		else :
			hour = str(hour)
		timeString = '%s:%s:%s' % (hour, minute, second)
		self.FPC.totalTime = timeString

	def __searchBtn (self, stat = True) :
		if stat :
			self.sBtn = Tkinter.Button(self.mainTop, text = '搜索', width = 10, command = self.__showResult)
			self.sBtn.grid(row = 0, column = 4, padx = 5)
		else :
			self.sBtn = Tkinter.Button(self.mainTop, text = '分析中...', width = 10, command = '')
			self.sBtn.grid(row = 0, column = 4, padx = 5)


	def __showInfo(self):
		self.slave = Tkinter.Tk();

		self.slave.title(self.slaveTitle)
		self.slave.resizable(width = 'false', height = 'false')

		info = [
			'Support: www.youku.com\nwww.tudou.com\ntv.sohu.com\nwww.letv.com\nwww.bilibili.com\nwww.acfun.tv\nwww.iqiyi.com\n\n',
			'Full Episode Download Support: www.youku.com\ntv.sohu.com\nwww.iqiyi.com\n\n',
			'Original Project: https://github.com/EvilCult/Video-Downloader'
		]

		label = Tkinter.Label(self.slave, text="Video Downloader", font = ("Helvetica", "16", 'bold'), anchor = 'center')
		label.grid(row = 0)

		information = Tkinter.Text(self.slave, height = 13, width = 60, highlightthickness = 0)
		information.grid(row = 1, padx = 10, pady = 5)
		for n in info :
			information.insert('end', n.split(': ')[0] + '\n')
			information.insert('end', n.split(': ')[1] + '\r')

		label = Tkinter.Label(self.slave, text="Version: Beta 0.9.5", font = ("Helvetica", "10"), anchor = 'center')
		label.grid(row = 2)
		label = Tkinter.Label(self.slave, text="Project Site: https://github.com/ShadyZOZ/Video-Downloader", font = ("Helvetica", "10"), anchor = 'center')
		label.grid(row = 3)

	def run (self) :
		self.__mainWindow()
		self.master.mainloop()
