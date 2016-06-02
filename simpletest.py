#!/usr/bin/env python
import subprocess, xlwt, xlrd, sys, re
from xlutils.copy import copy

class Handler(): 
	def __init__(self):
		self.start_row = 1
		self.bookName = "octracker.xls"
		self.f=open("log",'w')
	#	self.ocLists = []

	def call(self, *args):
		command = ["oc"] + list(args) + ["-h"]
	#	outputStr = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		if subprocess.Popen(command, stderr=subprocess.PIPE).stderr.read():
			return subprocess.Popen(command, stderr=subprocess.PIPE).stderr.read()
		else:
			print 'oc from stdout---'
			return subprocess.Popen(command, stdout=subprocess.PIPE).stdout.read()
	def get_command_title(self,outputStr):
		commandList = []
		for i in range(outputStr.count(':')):
			commandList.append(outputStr.split(':')[i].split('\n')[-1])
		return commandList
	def get_commands(self,pageStr,title):
		''' input: title - str, title name, e.g. "Basic Commands"
			output: (commandsL,descriptionL)  
				commandsL - list for commands of the title,  
				descriptionL - list for descriptions of commands
		'''
		commandsL = []
		descriptionL = []
		cmd_dspt_Str = pageStr.split(title+':')[1].split("\n\n")[0].strip()
		cmd_dscpt_Lists = cmd_dspt_Str.split("\n")
		for cmd_dscpt in cmd_dscpt_Lists:
			wordlist = cmd_dscpt.split()
			cmd = wordlist[0]
			wordlist.remove(wordlist[0])
			description = " ".join(wordlist)
			descriptionL.append(description)
			commandsL.append(cmd)
		return (commandsL, descriptionL)

	def get_flags(self, pageStr):

		flags = []
		secondLevelcmd = []
		if "vailable Commands" in pageStr:
			flagStr = pageStr.split("vailable Commands:\n")[1].split('\n\n')[0]
			flagLines = re.split("\n",flagStr)
			print flagLines
			for line in flagLines:
				flags.append(line.split()[0])

		elif "ptions:" in pageStr:
			flagStr = pageStr.split("ptions:\n")[1].split('\n\n')[0]
			flagLines = re.split("\n",flagStr)
			for line in flagLines:
				flags.append(line.split(':')[0])
		return flags



	def open_sheet(self,name):
		try:
			book = xlrd.open_workbook(self.bookName)
			tablesheet = book.sheet_by_name(name)
			print 'in try'
		except:
			book = xlwt.Workbook()
			book.add_sheet(name)
			book.save(self.bookName)
			book = xlrd.open_workbook(self.bookName)
			tablesheet = book.sheet_by_name(name)
			print 'in except'
		finally:
			self.book = book
	
	def insert_rows(self, sheet, colWriteNum, commandList):
		for index in range(len(commandList)):
			sheet.write(self.start_row+index, colWriteNum, commandList[index])
		self.start_row = self.start_row + index +1
		
	def append_log(self, list, title):
		self.f.write('\n--- %s ---\n'%title)
		for txt in list:
			self.f.write(txt + '\n')

class oc(Handler):
	def __init__(self):
		Handler.__init__(self)
		self.ocLists = []
		
	def call_command_title(self, *args):
		self.commandTitleStr = self.call(*args)
		titles = self.get_command_title(self.commandTitleStr)
		return titles

	def insert_cmds_for_titles(self, sheet, titles, colWriteNum):
		print "command titles are \n" + str(titles) + '\n======= above is titles =========\n'
		for title in titles:
			commandList = self.get_commands(pageStr=self.commandTitleStr, title=title)[0]		
			self.insert_rows(sheet, colWriteNum, commandList)
			self.append_log(commandList,title)
			self.ocLists.append(commandList)
		self.f.write('================================\n')

if __name__ == '__main__':
	test=oc()
	commandTitleList = test.call_command_title("")  #	whole command page - test.commandTitleStr
	if len(sys.argv)<2: 
		colWriteNum=0
	else:
		colWriteNum=int(sys.argv[1])-1

	test.open_sheet("all")
	editBook = copy(test.book)
	sheet1 = editBook.get_sheet(0)
	test.insert_cmds_for_titles(sheet1, commandTitleList, colWriteNum)
	editBook.save("octracker.xls")
	test.f.close()

#	for i in range(len(commandTitleList)): # use number as SHEET name instead of command title, which might change by dev in future
#		test.open_sheet(str(i))
#		editBook = copy(test.book)
#	editBook.save("octracker.xls")


	print test.ocLists
	print '======= above is level 1 cmds =========\n'
	for oclist in test.ocLists:
		print oclist
		for ocCmd in oclist:
			print ocCmd
			outputStr = test.call(ocCmd)
			flags = test.get_flags(outputStr)
			flagList = []
			for flag in flags:
				if flag =="":
					pass
				else:
					flagList.append(flag.strip())
			print flagList



		












