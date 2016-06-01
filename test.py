import subprocess

class Handler(): 
	def __init__(self):
		pass
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
		commandsL = []
		descriptionL = []
		cmd_dspt_Str = pageStr.split(title+':')[1].split("\n\n")[0].strip()
		cmd_dscpt_Lists = cmd_dspt_Str.split("\n")
		for cmd_dscpt in cmd_dscpt_Lists:
			wordlist = cmd_dscpt.split()
			cmd = wordlist[0]
			wordlist.remove(wordlist[0])
			description = "".join(wordlist)
			descriptionL.append(description)
			commandsL.append(cmd)
		return commandsL

class oc(Handler):
	def __init__(self):
		Handler.__init__(self)
		pass
	def call_command_title(self, *args):
		self.commandTitleStr = self.call(*args)
		self.commandTitleList = self.get_command_title(self.commandTitleStr)
	def call_commands(self,title):
		commandStr = self.call(title)
		print commandStr



if __name__ == '__main__':
	test=oc()
	test.call_command_title("")
	print test.commandTitleList

	commandList = test.get_commands(pageStr=test.commandTitleStr, title=test.commandTitleList[0])
	print commandList