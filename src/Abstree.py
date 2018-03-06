import enum
class Label(enum.Enum):
	VAR = 1
	DEREF = 2
	ADDR = 3
	UMINUS= 4
	CONST = 5
	ASSGN = 6 
	MINUS = 7
	PLUS  = 8
	MUL = 9
	DIV = 10
	IF = 11
	ELSE_IF = 12
	ELSE = 13
	WHILE = 14
	BLOCK = 15
	IFSTMT = 16
	COND = 17 
	LESSTHAN = 18
	LESSTHANEQ = 19 
	GREATERTHAN = 20
	GREATERTHANEQ = 21
	EQ = 22
	DECL = 23
	INT = 24
	DVAR = 25
	DEFAULT = 1000

class Abstree:
	label = Label.DEFAULT
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
			print(s+self.label.name + "(" + self.value + ")")
			return
		self.print_without(s)
		print(self.label.name)
		lbrack = s + "("
		print(lbrack)
		for x in self.children:
			x.print_tree(depth+1)
			if x == self.children[len(self.children)-1] :
				break
			print(s+"\t"+",")
		print(s+")")
	def valid_tree(self, availVars, parent, index):
		if self.label==Label.ASSGN :
			return self.check_assign() and self.check_declaration(availVars)
		elif self.label==Label.IFSTMT or self.label==Label.WHILE or \
			self.label==Label.ELSE_IF or self.label==Label.IF or self.label==Label.ELSE:
			q = True
			i=0
			for k in self.children:
				q = q and k.valid_tree(availVars, self, i)
				i+=1
			return q
		elif self.label==Label.COND:
			return self.check_declaration(availVars)
		elif self.label == Label.BLOCK:
			q = True
			i=0
			for k in self.children:
				if(k.label==Label.DECL) :
					# print("here", i)
					q = q and k.valid_tree(availVars, self, i)
					break 
				q = q and k.valid_tree(availVars, self, i)
				i+=1
			return q
		elif self.label==Label.DECL :
			q = True
			i=index+1
			new_vars = self.update_vars()
			for x in new_vars:
				if x[0] in [y[0] for y in availVars]:
					print("ERROR: Double declaration for", x[0])
					return False
			availVars = availVars + new_vars
			# print(availVars)
			siblings = parent.children[(index+1):]
			for k in siblings:
				if(k.label==Label.DECL) :
					q = q and k.valid_tree(availVars, self, i)
					break
				q = q and k.valid_tree(availVars, self, i)
				i+=1
			return q

	def update_vars(self):
		vars_ = []
		for k in self.children:
			if k.label == Label.DVAR:
				c = k.children[0]
				depth = 0
				while True:
					if c.label == Label.VAR:
						vars_.append((c.value, depth))
						break
					else:
						depth+=1
						c=c.children[0]
		return vars_
	def check_declaration(self, availVars):
		g = True
		if self.label == Label.VAR:
			# print(availVars)
			if self.value in [x[0] for x in availVars]:
				return True
			else:
				print("ERROR:", self.value, "Not Defined")
				return False
		# elif self.label == Label.DEREF:
		# 	curr = self
		# 	depth = 1
		# 	while(curr.label!=Label.VAR):
		# 		depth = depth + 1
		# 		curr = curr.children[0]
		# 	t = (curr.value, depth)
		for k in self.children:
			g = g and k.check_declaration(availVars)
		return g
	def add_child(self, child):
		self.children.append(child)
	def prepend(self, child):
		self.children = [child] + self.children
	def check_assign(self):
		if self.children[0].label==Label.DEREF:
			return True
		else :
			found = False
			frontier = [self.children[1]]
			while True:
				if len(frontier) == 0:
					break
				curr = frontier[0]
				if curr.isTerminal:
					if curr.label == Label.VAR:
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
		print("Syntax error at '{1}' on line number {0}".format(str(lineno), str(self.children[0].value) + " ="))
# a = Abstree([], "VAR", True, "a")
# c = Abstree([], "CONST", True, "5")
# # de = Abstree([a], "UMINUS", False, "")
# assgn = Abstree([a, c], "ASSGN", False, "")
# assgn.print_tree(0)
# print(assgn.valid_tree())