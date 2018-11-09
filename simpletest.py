#!/usr/bin/env python
import subprocess
import sys, re

class Handler(): 
	def __init__(self):
		self.subGroups = ["vailable Commands:", "daemon sets:", "application flows:"  ]	# for looking for sub commands

	def call(self, *args):
		if type(args[0]) == list:
			command = self.root_cmd + args[0] + ["-h"]
		else:
			command = self.root_cmd + list(args) + ["-h"]
		print command

		# `oc $CMD -h` outputs via stdout, but `oc options` outputs via stderr
		outputTuple = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		output = outputTuple[0] + outputTuple[1]
		return output
	
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
			flags = re.findall(r"(^ +-.+?):", flagStr, re.MULTILINE)
			self.append_log(list=flags, title=self.o +' '+ ocCmd)
		else: # no flags, e.g v3.8 oc adm cordon -h
			self.append_log(list=[], title=self.o +' '+ ocCmd)

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
		output = subprocess.Popen(self.root_cmd + ['options'], stderr=subprocess.PIPE).stderr.read()
		optionL = re.findall(r"(^ +-.+?):", output, re.MULTILINE)
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
	args = ' '.join(sys.argv)
	if "oc" in args and "adm" not in args:
		test.o = "oc"
                test.root_cmd = [sys.argv[1]]
	elif "oc" in args and "adm" in args:
		test.o = "oc adm"
                test.root_cmd = [sys.argv[1]] + ["adm"]
        else:
		print "Usage is wrong"


	# >>>>>>>>>>>>>> to see if need to output a diff file and open a log file to write
	test.diff = False
	if "diff" in sys.argv: 
		test.diff = True
		sys.argv.remove("diff")

	versionOutput = subprocess.Popen([sys.argv[1], 'version'], stdout=subprocess.PIPE).stdout.read()
	test.v = re.findall(r"oc (v.+)", versionOutput)[0]
	headerList = test.call_command_title("") 

	test.logName = '_'.join(test.o.split()) + "_" + test.v + "_cmds.txt"
	test.f=open(test.logName,'w')
	test.insert_cmds_for_titles(headerList) 
	
	# >>>>>>>>>>>>>> for each top level oc command, write all sub-commands and flags
	for oclist in test.ocLists:
		print '\n============================================'
		print oclist
		for ocCmd in oclist:
			outputStr = test.call(ocCmd)
			flags = test.get_flags(outputStr, ocCmd)
	
	# >>>>>>>>>>>>>> write 'oc options'
	ocOptionL = test.get_oc_option_list()
	test.append_log(ocOptionL,'%s options'%test.o)
	print '============== %s options =============='%test.o
	print ocOptionL
	
	# >>>>>>>>>>>>>> save log file, diff file
	test.f.close()
	print "\n\n>>>>>>>>>>> Please check the %s file <<<<<<<<<<< " % test.logName
