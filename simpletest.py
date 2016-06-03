#!/usr/bin/env python
import subprocess, xlwt, xlrd
from xlutils.copy import copy
import sys, re
from xlwt import easyxf

class Handler(): 
	def __init__(self):
		self.start_row = 1
		self.bookName = "octracker.xls"
		self.f=open("log",'w')

	def call(self, *args):
		if type(args[0]) == list:
			command = ["oc"] + args[0] + ["-h"]
		else:
			command = ["oc"] + list(args) + ["-h"]
		print command

		if subprocess.Popen(command, stderr=subprocess.PIPE).stderr.read(): # command output is from oc stderr 
			return subprocess.Popen(command, stderr=subprocess.PIPE).stderr.read()
		else:
			return subprocess.Popen(command, stdout=subprocess.PIPE).stdout.read()  # command output is from oc stdout
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

	def get_sub_command_name(self, subcmdPageStr):
		subCmd_namesL = []
		cmdLines = re.split("\n",subcmdPageStr)
		for line in cmdLines:
			sub_cmd = line.split()[0]		
			subCmd_namesL.append(sub_cmd)

		return subCmd_namesL

	def get_flags(self, pageStr, ocCmd):
		''' start from root oc command, like `create`, and get all subcommands/subcommands flags'''

		flags = []
		commands = []
		if "ptions:" in pageStr:
			flagStr = pageStr.split("ptions:\n")[1].split('\n\n')[0]
			flagLines = re.split("\n",flagStr)
			for line in flagLines:
				flags.append(line.split(':')[0])
			self.append_log(list=flags, title='oc '+ocCmd)

		if "vailable Commands" in pageStr:
			subcmdPageStr = pageStr.split("vailable Commands:\n")[1].split('\n\n')[0]
			subCmdNamesL = self.get_sub_command_name(subcmdPageStr)
			nextLevel = self.get_next_level_flags(ocCmd, subCmdNamesL)

			subcmdStr = nextLevel[0]
			subcmdFlagsL = nextLevel[1]
			pageStr = nextLevel[2]
			commands.append(subcmdStr)
			flags.append(subcmdFlagsL)

		return flags

	def get_next_level_flags(self, ocCmd, subcmdL):   #ocCmd, subcmdL
		for subcmd in subcmdL:  # subcmdL= namespace, secret, ...
			newCmd = ocCmd +' '+ subcmd
			ocCmdSubCmd = (newCmd).split()
			newPageStr = self.call(ocCmdSubCmd) # e.g ocCmd="create", subcmd='namespace'
			flags = self.get_flags(newPageStr, newCmd)  

		return (newCmd, flags, newPageStr)

	def open_book_with_sheet(self,name):
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
			self.sheet = tablesheet
	
	def color4bold(self, color):
		'''for bold color: '''
		style = xlwt.easyxf('font: bold true;'
               'borders: left no_line, right no_line, top no_line, bottom no_line;'
               'font: color %s'%color)
		return style

	def insert_rows(self, commandList=[], color=''):
		i = 0
		for value in commandList:
			i = commandList.index(value)
			if color: self.sheet.write(self.start_row+i, self.colWriteNum, value ,style=self.color4bold(color=color)) 
			else: self.sheet.write(self.start_row+i, self.colWriteNum, value)
		self.start_row = self.start_row + i +1

		
	def append_log(self, list=[], title=[]):
		self.f.write('\n%s\n'%title)
		self.insert_rows([title], color='black')
		self.insert_rows(list)
		for item in list:
			self.f.write(str(item) + '\n')

class oc(Handler):
	def __init__(self):
		Handler.__init__(self)
		self.ocLists = []
		
	def call_command_title(self, *args):
		self.commandTitleStr = self.call(*args)
		titles = self.get_command_title(self.commandTitleStr)
		return titles

	def insert_cmds_for_titles(self, valueList):
		print "command titles are \n" + str(valueList) + '\n======= above are top level titles =========\n'
		self.insert_rows(["======= top level titles ========="], color='aqua')
		for title in valueList:
			commandList = self.get_commands(pageStr=self.commandTitleStr, title=title)[0]	
			self.append_log(commandList,title)
			self.ocLists.append(commandList)
		self.f.write('================================\n')
		self.insert_rows(["================================"], color='aqua')

if __name__ == '__main__':
	test=oc()
	test.open_book_with_sheet("all")
	test.sheet = test.book.sheet_by_index(0) 
	test.colWriteNum = test.sheet.ncols # write from col 0, so does not need + 1

	if len(sys.argv)<2: logTitle = raw_input("Please input a title for this version of result, suggest '3.2.0.x' :")
	else: logTitle = sys.argv[1]
	writeList = test.call_command_title("")  #	whole command page - test.commandTitleStr
	editBook = copy(test.book)
	test.sheet = editBook.get_sheet(0)
	test.sheet.write(0, test.colWriteNum, logTitle, test.color4bold(color='green'))
	test.insert_cmds_for_titles( writeList) # write top level commands



	for oclist in test.ocLists:
		print '\n============================================'
		print oclist
		for ocCmd in oclist:
		#	print ocCmd
			outputStr = test.call(ocCmd)
			flags = test.get_flags(outputStr, ocCmd)
			


	editBook.save("octracker.xls")
	test.f.close()



