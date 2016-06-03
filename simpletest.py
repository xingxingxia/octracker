#!/usr/bin/env python
import subprocess, xlwt, xlrd
import sys, re
from xlutils.copy import copy

class Handler(): 
	def __init__(self):
		self.start_row = 1
		self.bookName = "octracker.xls"
		self.f=open("log",'w')
	#	self.ocLists = []

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
	#	print '###########################'
	#	print subCmd_namesL
	#	print '###########################'
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
#			self.insert_rows(flags)  #

		if "vailable Commands" in pageStr:
#			print "< %s > "%str(ocCmd)
			subcmdPageStr = pageStr.split("vailable Commands:\n")[1].split('\n\n')[0]
			subCmdNamesL = self.get_sub_command_name(subcmdPageStr)
			nextLevel = self.get_next_level_flags(ocCmd, subCmdNamesL)

			subcmdStr = nextLevel[0]
			subcmdFlagsL = nextLevel[1]
			pageStr = nextLevel[2]
			commands.append(subcmdStr)
			flags.append(subcmdFlagsL)
#			self.append_log(list=subcmdStr, title="%s's subcmd"%ocCmd)

	#	self.insert_rows(flags)
		return flags

	def get_next_level_flags(self, ocCmd, subcmdL):   #ocCmd, subcmdL
		for subcmd in subcmdL:  # subcmdL= namespace, secret, ...
			newCmd = ocCmd +' '+ subcmd
			ocCmdSubCmd = (newCmd).split()
			newPageStr = self.call(ocCmdSubCmd) # e.g ocCmd="create", subcmd='namespace'
			flags = self.get_flags(newPageStr, newCmd)  
#		print '######'
#		print type(subcmdL)
#		print subcmdL
#		self.append_log(list=subcmdL, title="%s's subcmd flags"%ocCmd)       ######need debug

		return (newCmd, flags, newPageStr)


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
	
	def insert_rows(self, commandList=[]):
		i = 0
		for value in commandList:
			i = commandList.index(value)
		#	self.sheet.write(self.start_row+index, self.colWriteNum, commandList[index])
			self.sheet.write(self.start_row+i, self.colWriteNum, value)
		self.start_row = self.start_row + i +1

		
	def append_log(self, list=[], title=[]):
		self.f.write('\n%s\n'%title)
		self.insert_rows([title] + list)
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
		for title in valueList:
			commandList = self.get_commands(pageStr=self.commandTitleStr, title=title)[0]	
			self.insert_rows(commandList)
			self.append_log(commandList,title)
			self.ocLists.append(commandList)
		self.f.write('================================\n')

if __name__ == '__main__':
	test=oc()
	writeList = test.call_command_title("")  #	whole command page - test.commandTitleStr
	if len(sys.argv)<2: 
		test.colWriteNum=0
	else:
		test.colWriteNum=int(sys.argv[1])-1

	test.open_sheet("all")
	editBook = copy(test.book)
	test.sheet = editBook.get_sheet(0)
	test.insert_cmds_for_titles( writeList) # write top level commands

#	for i in range(len(writeList)): # use number as SHEET name instead of command title, which might change by dev in future
#		test.open_sheet(str(i))
#		editBook = copy(test.book)
#	editBook.save("octracker.xls")



#	print test.ocLists
	for oclist in test.ocLists:
		print '\n============================================'
		print oclist
		for ocCmd in oclist:
		#	print ocCmd
			outputStr = test.call(ocCmd)
			flags = test.get_flags(outputStr, ocCmd)
			
		#	flagList = []
		#	for flag in flags:
		#		if flag =="":	pass
		#		else:
		#			try: flagList.append(flag.strip())  # level2 commands is a hash which cannot be stripped
		#			except: pass
		#	print flagList
	







## for test `oc create -h`
#	outputStr = test.call("create")
#	flags = test.get_flags(outputStr, "create")



	editBook.save("octracker.xls")
	test.f.close()










