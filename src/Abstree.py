class Abstree: 
	label = ""
	children = []
	isTerminal = False
	value = ""
	def __init__(self, children, label, isTerminal, value):
		self.label = label
		self.children = children
		self.isTerminal = isTerminal
		self.value = value
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
			if(x==self.children[len(self.children)-1]):
				break
			print(s+"\t"+",")
		print(s+")")
	

a = Abstree([], "VAR", True, "a")
c = Abstree([], "CONST", True, "5")
de = Abstree([a], "DEREF", False, "")
assgn = Abstree([de, c], "ASSGN", False, "")
assgn.print_tree(0)