#!/usr/bin/env python
import subprocess
import sys, re

class Handler(): 
	def __init__(self):
		self.start_row = 1
	#	self.f=open("log",'w')
		self.subGroups = ["vailable Commands:", "daemon sets:", "application flows:"  ]	# for looking for sub commands

	def call(self, *args):
		if type(args[0]) == list:
			command = [self.o] + args[0] + ["-h"]
		else:
			command = [self.o] + list(args) + ["-h"]
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
		print 'find sub > ' + str(subCmdNamesL)	
		nextLevel = self.get_next_level_flags(ocCmd, subCmdNamesL)

		subcmdStr = nextLevel[0]
		subcmdFlagsL = nextLevel[1]
		pageStr = nextLevel[2]
		commands.append(subcmdStr)
		flags.append(subcmdFlagsL)

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

	def append_log(self, list=[], title=[]):
		self.f.write('\n%s\n'%title)
		for item in list:
			self.f.write(str(item) + '\n')

	def check_diff(self):
		''' diff will save a file compare the new log with last time added log. 
			*NOTE for pre action for next run:
			Before next time to use this py script, need to `git add log` to save the changed "log" for baseline, will compare next log with this baseline,
			otherwise, git diff will only compare next new log with last log'''

		if self.diff == False:
			return "not require for log diff!"
		else:
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
		print "command titles are \n" + str(valueList) + '\n======= above are top level titles =========\n'
		for title in valueList:
			commandList = self.get_commands(pageStr=self.commandTitleStr, title=title)[0]	
			self.append_log(commandList,title)
			self.ocLists.append(commandList)
		self.f.write('================================\n')

if __name__ == '__main__':
	test=oc()

	# >>>>>>>>>>>>>> to see if it's oc or oadm command
	if "oc" in sys.argv:
		test.o = "oc"
		sys.argv.remove("oc")
	if "oadm" in sys.argv:
		test.o = "oadm"
		sys.argv.remove("oadm")   	

	# >>>>>>>>>>>>>> to see if need to output a diff file and open a log file to write
	test.diff = False
	if "diff" in sys.argv: 
		test.diff = True
		sys.argv.remove("diff")

	if len(sys.argv)<2: test.v=logTitle = raw_input("Please input a title for this version of result, suggest '3.2.0.x' :")
	else: test.v=logTitle = sys.argv[1]
	headerList = test.call_command_title("") 

	test.logName = test.o + "_" + test.v + "_cmds.txt"
	test.f=open(test.logName,'w')
	test.insert_cmds_for_titles(headerList) 
	
	# >>>>>>>>>>>>>> write 'oc options'
	ocOptionL = test.get_oc_option_list()
	test.append_log(ocOptionL,'%s options'%test.o)
	print '============== %s options =============='%test.o
	print ocOptionL
	
	# >>>>>>>>>>>>>> for each top level oc command, write all sub-commands and flags
	for oclist in test.ocLists:
		print '\n============================================'
		print oclist
		for ocCmd in oclist:
			outputStr = test.call(ocCmd)
			flags = test.get_flags(outputStr, ocCmd)
	
	# >>>>>>>>>>>>>> save xls, log file, diff file
	test.f.close()
	print "\n\n>>>>>>>>>>> Please check the *_cmds.txt file <<<<<<<<<<< "
