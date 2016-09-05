#!/usr/bin/env python
import subprocess, xlwt, xlrd
from xlutils.copy import copy
import sys, re
from xlwt import easyxf

class Handler(): 
	def __init__(self):
		self.start_row = 1
		self.bookName = ""
	#	self.ocLists = []
		self.subGroups = ["vailable Commands:", "daemon sets:", "application flows:"  ]	# for looking for sub commands

	def call(self, *args):
		if type(args[0]) == list:
			command = [self.o] + args[0] + ["-h"]
		else:
			command = [self.o] + list(args) + ["-h"]

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

	def get_flags(self, pageStr, ocCmd):
		''' start from root oc command, like `create`, and get all subcommands/subcommands flags'''
		flags = []
		commands = []
		if "ptions:" in pageStr:	## FILTER FLAGS
			flagStr = pageStr.split("ptions:\n")[1].split('\n\n')[0]
			flagLines = re.split("\n",flagStr)
			for line in flagLines:
				flags.append(line.split(':')[0])
			self.append_log(list=flags, title=self.o +' '+ ocCmd)

		for sub in self.subGroups:	## FILTER SUB COMMANDS
			if sub in pageStr:
				self.get_sub_cmds(sub+"\n", pageStr, ocCmd, commands)
		return flags

	def get_sub_cmds(self, subGroup, pageStr, ocCmd, commands):
		subcmdPageStr = pageStr.split(subGroup)[1].split('\n\n')[0]
		subCmdNamesL = self.get_sub_command_name(subcmdPageStr)
	#	print 'find sub > ' + str(subCmdNamesL)	
		nextLevel = self.get_next_level_flags(ocCmd, subCmdNamesL)

		subcmdStr = nextLevel[0]
		subcmdFlagsL = nextLevel[1]
		pageStr = nextLevel[2]

	def get_sub_command_name(self, subcmdPageStr):
		subCmd_namesL = []
		cmdLines = re.split("\n",subcmdPageStr)
		for line in cmdLines:
			sub_cmd = line.split()[0]		
			subCmd_namesL.append(sub_cmd)
		return subCmd_namesL

	def get_next_level_flags(self, ocCmd, subcmdL):   #ocCmd, subcmdL
		for subcmd in subcmdL:  # subcmdL= namespace, secret, ...
			newCmd = ocCmd +' '+ subcmd
			ocCmdSubCmd = (newCmd).split()
			newPageStr = self.call(ocCmdSubCmd) # e.g ocCmd="create", subcmd='namespace'
			flags = self.get_flags(newPageStr, newCmd)  
		return (newCmd, flags, newPageStr)

	def open_book_with_sheet(self,name):
		try:
			book = xlrd.open_workbook(self.bookName, formatting_info=True)
			tablesheet = book.sheet_by_name(name)
		except:
			book = xlwt.Workbook()
			book.add_sheet(name)
			book.save(self.bookName)
			book = xlrd.open_workbook(self.bookName, formatting_info=True)
			tablesheet = book.sheet_by_name(name)
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

	def check_diff(self):
		''' diff will save a file compare the new log with last time added log. 
			*NOTE for pre action for next run:
			Before next time to use this py script, need to `git add log` to save the changed "log" for baseline, will compare next log with this baseline,
			otherwise, git diff will only compare next new log with last log'''


		cmd = "git diff --unified=1000 %s"%self.logName
		cmd2= "git diff %s"%self.logName
		diffLog = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).stdout.read()
		printLog = subprocess.Popen(cmd2.split(), stdout=subprocess.PIPE).stdout.read()
		diff_f=open(self.o+"_difflog_"+self.v,'w')
		diff_f.write(diffLog)
		diff_f.close()
		if diffLog == '': print "\nNothing changed!"
		else: print printLog

	def get_oc_option_list(self):
		self.commandTitleStr = subprocess.Popen([self.o,'options'], stderr=subprocess.PIPE).stderr.read()
		optionsParagraph = self.commandTitleStr.split('\n\n')[1]
		optionL = []
		lines =  optionsParagraph.split('\n')
		for line in lines:
			optionL.append(line.split(':')[0])
		return optionL

class oc(Handler):
	def __init__(self):
		Handler.__init__(self)
		self.ocLists = []
		
	def call_command_title(self, *args):
		self.commandTitleStr = self.call(*args)
		titles = self.get_command_title(self.commandTitleStr)
		return titles

	def insert_cmds_for_titles(self, valueList):
	#	print "command titles are \n" + str(valueList) + '\n======= above are top level titles =========\n'
		self.insert_rows(["======= top level titles ========="], color='aqua')
		for title in valueList:
			commandList = self.get_commands(pageStr=self.commandTitleStr, title=title)[0]	
			self.append_log(commandList,title)
			self.ocLists.append(commandList)
		self.f.write('================================\n')
		self.insert_rows(["================================"], color='aqua')

class run():
	def __init__(self, ocoadm, versionName):
		self.ocoadm = ocoadm
		self.versionName = versionName

	def run_diff(self):
		test=oc()

		if "oc" in self.ocoadm:
			test.o = "oc"
		elif "oadm" in self.ocoadm:
			test.o = "oadm"	
		test.bookName = test.o + "tracker.xls"
		test.logName = test.o+"_log"
		subprocess.Popen(['git', 'add', test.logName], stdout=subprocess.PIPE).stdout.read()

		test.open_book_with_sheet("all")
		test.sheet = test.book.sheet_by_index(0) 
		test.colWriteNum = test.sheet.ncols # write from col 0, so does not need + 1

		test.v = logTitle = self.versionName
		headerList = test.call_command_title("") 
		test.f=open(test.logName,'w')

		editBook = copy(test.book)
		test.sheet = editBook.get_sheet(0)
		test.sheet.write(0, test.colWriteNum, logTitle, test.color4bold(color='green'))
		test.insert_cmds_for_titles(headerList) 

		# >>>>>>>>>>>>>> write 'oc options'
		ocOptionL = test.get_oc_option_list()
		test.append_log(ocOptionL,'(%s options)'%test.o)
	#	print '============== (%s options) =============='%test.o
	#	print ocOptionL
		
		# >>>>>>>>>>>>>> for each top level oc command, write all sub-commands and flags
		for oclist in test.ocLists:
		#	print '\n============================================'
		#	print oclist
			for ocCmd in oclist:
				outputStr = test.call(ocCmd)
				flags = test.get_flags(outputStr, ocCmd)
		
		# >>>>>>>>>>>>>> save xls, log file, diff file
		editBook.save(test.bookName)
		test.f.close()
		print "\n\n>>>>>>>>>>> below are diff to the last 'git add' ;) <<<<<<<<<<< "
		test.check_diff()





if __name__ == '__main__':

	run_oc = run('oc', sys.argv[1])
	run_oc.run_diff()
	run_oadm = run('oadm', sys.argv[2])
	run_oadm.run_diff()

