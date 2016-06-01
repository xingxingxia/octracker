import subprocess, xlwt, xlrd, sys
from xlutils.copy import copy

class Handler(): 
	def __init__(self):
		self.start_row = 1
	def call(self, *args):
		command = ["oc"] + list(args) + ["-h"]
		outputStr = subprocess.check_output(command)
		return outputStr
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

	def open_sheet(self,sheetName):
		try:
			book = xlrd.open_workbook("octracker.xls",formatting_info=True)
			tablesheet = book.sheet_by_name(sheetName)
		except:
			book = xlwt.Workbook()
			book.add_sheet(sheetName)
			book.save("octracker.xls")
			book = xlrd.open_workbook("octracker.xls",formatting_info=True)
			tablesheet = book.sheet_by_name(sheetName)
		return book
	

class oc(Handler):
	def __init__(self):
		Handler.__init__(self)
		pass
	def call_command_title(self, *args):
		self.commandTitleStr = self.call(*args)
		titles = self.get_command_title(self.commandTitleStr)
		return titles

	def insert_cmds_for_titles(self, sheet, titles,colWriteNum):
		print "command titles are \n" + str(titles) + '\n================\n'
		for title in titles:
			commandList = self.get_commands(pageStr=self.commandTitleStr, title=title)[0]		
			for index in range(len(commandList)):
				sheet.write(self.start_row+index, colWriteNum, commandList[index])
			self.start_row = self.start_row + index +1


if __name__ == '__main__':
	test=oc()
	commandTitleList = test.call_command_title("")  #	whole command page - test.commandTitleStr
	if len(sys.argv)<2: 
		colWriteNum=0
	else:
		colWriteNum=int(sys.argv[1])-1

	book = test.open_sheet("all")
	editBook = copy(book)
	ocSheet = editBook.get_sheet(0)
	test.insert_cmds_for_titles(ocSheet, commandTitleList, colWriteNum)
	editBook.save("octracker.xls")




