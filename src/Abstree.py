class Abstree:
	label = ""
	children = []
	isTerminal = False
	value = ""
	def __init__(self, children, label, isTerminal, value):
		self.label = label
		self.children = children
		self.isTerminal = isTerminal
		self.value = str(value)
	def print_without(self, s) :
		print(s, end='')
	def print_tree(self, depth):
		s = ""
		for i in range(depth):
			s = s+"\t"
		if(self.isTerminal):
			print(s+self.label + "(" + self.value + ")")
			return
		self.print_without(s)
		print(self.label)
		lbrack = s + "("
		print(lbrack)
		for x in self.children:
			x.print_tree(depth+1)
			if x == self.children[len(self.children)-1] :
				break
			print(s+"\t"+",")
		print(s+")")
	def valid_tree(self):
		if self.label=="ASSGN" :
			return self.check_assign()
	def check_assign(self):
		if self.children[0].label=="DEREF":
			return True
		else :
			found = False
			frontier = [self.children[1]]
			while True:
				if len(frontier) == 0:
					break
				curr = frontier[0]
				if curr.isTerminal:
					if curr.label == "VAR":
						found = True
						break
					else:
						frontier.remove(curr)
				else:
					for k in curr.children:
						frontier.append(k)
					frontier.remove(curr)
			return found
	def print_error(self, lineno):
		print("syntax error at lineno'{0}' due to {1}".format(str(lineno), str(self.children[0].value) + " ="))
# a = Abstree([], "VAR", True, "a")
# c = Abstree([], "CONST", True, "5")
# # de = Abstree([a], "UMINUS", False, "")
# assgn = Abstree([a, c], "ASSGN", False, "")
# assgn.print_tree(0)
# print(assgn.valid_tree())