import enum
class Label(enum.Enum):
	VAR = 1
	DEREF = 2
	ADDR = 3
	UMINUS= 4
	CONST = 5
	ASGN = 6 
	MINUS = 7
	PLUS  = 8
	MUL = 9
	DIV = 10
	IF = 11
	WHILE = 14
	BLOCK = 15
	COND = 17
	LT = 18
	LE = 19
	GT = 20
	GE = 21
	EQ = 22
	NE = 23
	DECL = 24
	INT = 25
	DVAR = 26
	AND = 27
	OR = 28
	END = 29
	DEFAULT = 1000


bbCount = 1
tCount = 1  

class Abstree:
	label = Label.DEFAULT
	children = []
	block_num = -1
	goto_num = -1
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
		if(self.label==Label.BLOCK):
			for x in self.children:
				x.print_tree(depth)
			return
		if(self.label==Label.DECL):
			return
		s = ""
		for i in range(depth):
			s = s+"\t"
		if(self.isTerminal):
			print(s+self.label.name + "(" + self.value + ")")
			return
		self.print_without(s)
		print(self.label.name, self.block_num, self.goto_num)
		lbrack = s + "("
		print(lbrack)
		for x in self.children:
			x.print_tree(depth+1)
			if x == self.children[len(self.children)-1] :
				break
			print(s+"\t"+",")
		print(s+")")
	def valid_tree(self, availVars, parent, index):
		if self.label==Label.ASGN :
			return self.check_assign() and self.check_declaration(availVars)
		elif self.label==Label.WHILE or self.label==Label.IF:
			q = True
			i=0
			for k in self.children:
				q = q and k.valid_tree(availVars, self, i)
				if not q:
					break
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
			if self.value in [x[0] for x in availVars]:
				return True
			else:
				print("ERROR:", self.value, "Not Defined")
				return False
		elif self.label == Label.DEREF or self.label == Label.ADDR:
			curr = self
			depth = 0
			while(curr.label!=Label.VAR):
				if(curr.label==Label.DEREF):
					depth = depth + 1
				elif (curr.label==Label.ADDR):
					depth = depth - 1
				curr = curr.children[0]
			t = (curr.value, depth)
			g = [True  for x in availVars if x[0]==t[0] and t[1] > x[1] ]
			if len(g):
				return True
			else:
				print("ERROR: TOO MUCH INDIRECTION")
				return False
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

	# def print_cfg(self, b_curr, b_end, assignList, goto_w, og):
	# 	if self.label == Label.BLOCK:
	# 		for x in self.children:
	# 			b_curr, b_end, assignList, goto_w = x.print_cfg(b_curr, b_end, assignList, goto_w, False)
	# 		if len(assignList) != 0 and og:
	# 			b_curr+=1
	# 			print("goto <bb", str(b_curr)+">")
	# 			print()
	# 			assignList = []
	# 			print("<bb", str(b_curr)+">")
	# 			print("End")
	# 	elif self.label == Label.WHILE:
	# 		b_curr+=1
	# 		if len(assignList) != 0:
	# 			print("goto <bb", str(b_curr)+">")
	# 			print()
	# 			assignList = []
	# 		print("<bb", str(b_curr)+">")
	# 		print("IFBLOCK")
	# 		b_curr+=10
	# 		print("goto <bb", str(b_curr)+">")
	# 		print()
	# 	elif self.label == Label.IF:
	# 		b_curr+=1
	# 		if len(assignList) != 0:
	# 			print("goto <bb", str(b_curr)+">")
	# 			print()
	# 			assignList = []
	# 		print("<bb", str(b_curr)+">")
	# 		#Unroll cond
	# 		print("if(", end='')
	# 		self.children[0].print_statement()
	# 		print(") goto <bb", str(b_curr+1)+">")
	# 		b_next = b_curr + self.find_depth()
	# 		if b_end == -1:
	# 			b_end = b_next + self.children[-1].find_depth() + 1
	# 		print("else goto <bb", str(b_next)+">")
	# 		print()
	# 		b_curr+=1
	# 		for x in self.children[1:]:
	# 			b_curr, temp, assignList, goto_w = x.print_cfg(b_curr, b_end, [],goto_w, False)
	# 			if len(assignList) != 0:
	# 				b_curr+=1
	# 			assignList = []
	# 			if not goto_w:
	# 				print("goto <bb", str(b_end)+">")
	# 				print()
	# 			goto_w = False
	# 		goto_w = True

	# 	elif self.label == Label.ASGN:
	# 		if len(assignList) != 0:
	# 			assignList.append(1)
	# 			self.print_statement()
	# 		else:
	# 			assignList = [1]
	# 			print("<bb", str(b_curr)+">")
	# 			self.print_statement()
	# 		print()
	# 	return b_curr, b_end, assignList, goto_w

	# # def find_depth(self, assignList):
	# # 	if self.label == Label.BLOCK:
	# # 		depth = 1
	# # 		for x in self.children:
	# # 			depth +=x.find_depth()
	# # 		return depth
	# # 	if self.label == Label.IF:
	# # 		if len(self.children) ==2:
	# # 			return 1 + self.children[1].find_depth()
	# # 		else:
	# # 			return 1 + self.children[1].find_depth() + self.children[2].find_depth()
	# # 	if self.label == Label.ASGN:
	# # 		if 
	# # 			assignList = [1]
	# # 			return 0
	# # 		else:
	# # 			assignList.append(1)

	# # 	return 0

	# def find_end(self, b_curr):
	# 	if self.label == Label.IF:
	# 		end = b_curr
	# 		for x in self.children
	# 			end+=x.find_end()

	# def print_statement(self):
	# 	if self.label == Label.ASGN:
	# 		lhs = self.children[0]
	# 		rhs = self.children[1]
	# 		lhs.print_statement()
	# 		print(" = ", end='')
	# 		rhs.print_statement()
	# 	elif self.label == Label.VAR:
	# 		print(self.value, end='')
	# 	elif self.label == Label.ADDR:
	# 		print("&", end='')
	# 		self.children[0].print_statement()
	# 	elif self.label == Label.DEREF:
	# 		print("*", end='')
	# 		self.children[0].print_statement()
	# 	elif self.label == Label.CONST:
	# 		print(self.value, end='')
	# 	elif self.label == Label.NE or self.label == Label.EQ or \
	# 		self.label == Label.LT or self.Label == Label.GT or \
	# 		self.label == Label.LE or self.Label == Label.GE:
	# 		print("COND_HERE", end='')
	# 	elif self.label == Label.AND or self.label == OR:
	# 		print("AND_COND", end='')

	def assign_blocks(self, num):
		if self.label == Label.BLOCK:
			self.block_num = num+1
			g = False
			for x in self.children:
				if x.label == Label.ASGN:
					if g:
						x.block_num = num
					else:
						g = True
						num+=1
						x.block_num = num
				else:
					g = False
					num = x.assign_blocks(num)
		elif self.label == Label.IF:
			num+=1
			self.block_num = num
			for x in self.children[1:]:
				num = x.assign_blocks(num)
		elif self.label == Label.WHILE:
			num+=1
			self.block_num = num
			num = self.children[1].assign_blocks(num)
		elif self.label == Label.END:
			num+=1
			self.block_num = num
		return num

	def assign_goto_num(self, goto):
		if self.label == Label.BLOCK:
			for y in range(len(self.children)):
				x = self.children[y]
				if x.label == Label.ASGN:
					if y+1 < len(self.children) :
						if self.children[y+1].label == Label.ASGN :
							x.goto_num = -1
						else :
							x.goto_num = self.children[y+1].block_num
					else :
						x.goto_num = goto
				else:
					if y+1 < len(self.children) :
						x.assign_goto_num(self.children[y+1].block_num)
					else :
						x.assign_goto_num(goto)
		elif self.label==Label.IF:
			self.children[1].assign_goto_num(goto)
			if(len(self.children)>=3):
				self.children[2].assign_goto_num(goto)
				self.goto_num = self.children[2].block_num
			else :
				self.goto_num = goto
		elif self.label == Label.WHILE:
			self.goto_num = goto
			self.children[1].assign_goto_num(self.block_num)

# def make_cfg(node, assign, assignList):
# 	if(node.label==Label.BLOCK):
# 		for c in range(len(node.children)):
# 			if(node.children[c].label!=Label.DECL):
# 				if node.children[c].label==Label.ASGN:
# 					temp = []
# 					while node.children[c].label == Label.ASGN and c < len(node.children):
# 						temp.append(node.children[c])
# 						c+=1
# 					c-=1
# 					make_cfg()
# 					# if c+1 == node.getNextGoto(c)
# 					# 	node.children[c].make_cfg(True)
# 					# else:
# 					# 	node.children[c].make_cfg(False)
# 				else:
# 					node.children[c].make_cfg(True)
# 	elif (node.label==Label.ASGN):
		
# 		if gotoEnd:

	# def getNextGoto(self, index):
	# 	index = index + 1
	# 	while index < len(self.children):
	# 		if(self.children[index].label==Label.IFSTMT or self.children[index].label==Label.WHILE):
	# 			return index
	# 		index = index + 1

# def make_cfg(node, target, current):
# 	if(node.label==Label.BLOCK):
# 		children = node.children
# 		count = 0
# 		for c in range(len(children)):
# 			if(children[c].label==Label.DECL):
# 				continue
# 			elif c==len(children)-1:
# 				make_cfg(children[c], target, current)
# 			elif children[c].label==Label.ASGN:
# 				make_cfg(children[c], -1, current)
# 				current = -1
# 			elif children[c].label==Label.IFSTMT or children[c].label==Label.WHILE:
# 				make_cfg(children[c], bbCount, current)
# 				current = bbCount
# 				bbCount = bbCount + 1


# 	elif(node.label==Label.ASGN):
# 		if(current==-1):
# 			print("<bb", current, ">")
# 		node.print_assign()
# 		if(target!=-1)
# 			print("goto", "<bb", target, ">")

# 	elif (node.label==Label.IFSTMT):




		