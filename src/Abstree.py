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
def nameMapper(x):
	y = {
		Label.PLUS :  ' + '  ,
		Label.MINUS :  ' - '  ,
		Label.MUL :  ' * '  ,
		Label.DIV :  ' / '  ,
		Label.LT :  ' < '  ,
		Label.LE :  ' <= ' ,
		Label.GT :  ' > '  ,
		Label.GE :  ' >= ' ,
		Label.EQ :  ' == ' ,
		Label.AND :  ' && ' ,
		Label.OR :  ' || ' ,
		Label.NE :  ' != ', 
		Label.UMINUS : ' - '
	}
	if x in y:
		return True, y[x]
	else:
		return False, -1


CONDS = [Label.LT, Label.LE, Label.GT, Label.GE, Label.EQ, Label.NE, Label.AND, Label.OR ]
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
		# print("here", self.label)
		if self.label==Label.ASGN :
			# print("here")
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
		elif self.label in CONDS:
			return self.check_declaration(availVars)
		elif self.label == Label.BLOCK:
			q = True
			i=0
			for k in self.children:
				if(k.label==Label.DECL) :
					# print("here")
					q = q and k.valid_tree(availVars, self, i)
					break
				q = q and k.valid_tree(availVars, self, i)
				i+=1
			return q
		elif self.label==Label.DECL :
			q = True
			i=index+1
			new_vars = self.update_vars()
			# print(new_vars)
			for x in new_vars:
				if x[0] in [y[0] for y in availVars]:
					print("ERROR: Double declaration for", x[0])
					return False
			availVars = availVars + new_vars
			# print(availVars)
			siblings = parent.children[(index+1):]
			for k in siblings:
				# print("pop", k.label)
				if(k.label==Label.DECL) :
					q = q and k.valid_tree(availVars, parent, i)
					break
				q = q and k.valid_tree(availVars, parent, i)
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
		# if self.label == Label.ASGN or self.label in CONDS:
		# 	if self.children[0].label == Label.VAR and
		g = True
		# print("here")
		if self.label == Label.VAR:
			if self.value in [x[0] for x in availVars]:
				g = [True for x in availVars if x[0]==self.value and x[1]==0]
				# print("HERE", g, self.value)
				if len(g) > 0:
					print("Direct use of non-pointer variable")
					return False
				return True
			else:
				print("ERROR:", self.value, "Not Defined")
				return False
		elif self.label == Label.DEREF or self.label == Label.ADDR:
			curr = self
			depth = 0
			# print("DEBUG_here")
			while(curr.label!=Label.VAR):
				if(curr.label==Label.DEREF):
					depth = depth + 1
				elif (curr.label==Label.ADDR):
					depth = depth - 1
				curr = curr.children[0]
			t = (curr.value, depth)
			# print(t)
			g = [True  for x in availVars if x[0]==t[0] and ((t[1] <= x[1] and x[1]!=0) or (x[1]==0 and t[1]<x[1])) ]
			# print(t[0], g)
			if len(g):
				return True
			else:
				print("ERROR: TOO MUCH INDIRECTION")
				return False
		for k in self.children:
			# print("DEBUG_here", k.label.name)
			g = g and k.check_declaration(availVars)
		return g
	# def getNodeDepth(self, node):
	# 	depth
	# 	while(curr.label!=Label.VAR):
	# 			if(curr.label==Label.DEREF):
	# 				depth = depth + 1
	# 			elif (curr.label==Label.ADDR):
	# 				depth = depth - 1
	# 			curr = curr.children[0]
	# 	return depth
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
			if not found:
				print("Syntax error at ", end='')
				self.print_statement()
				print()
			return found
	def print_error(self, lineno):
		print("Syntax error at '{1}' on line number {0}".format(str(lineno), str(self.children[0].value) + " ="))

	def print_cfg(self, b_curr, t_curr):
		if self.label == Label.BLOCK:
			for x in self.children:
				b_curr, t_curr = x.print_cfg(b_curr, t_curr)
		elif self.label == Label.WHILE:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			t_curr = self.children[0].unroll_and_print(t_curr)
			print("if(t"+str(t_curr),end='')
			print(") goto <bb", str(b_curr+1)+">")
			print("else goto <bb", str(self.goto_num)+">")
			print()
			for x in self.children[1:]:
				b_curr, t_curr = x.print_cfg(b_curr, t_curr)
		elif self.label == Label.IF:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			t_curr = self.children[0].unroll_and_print(t_curr)
			print("if(t"+str(t_curr),end='')
			print(") goto <bb", str(b_curr+1)+">")
			print("else goto <bb", str(self.goto_num)+">")
			print()
			for x in self.children[1:]:
				b_curr, t_curr = x.print_cfg(b_curr, t_curr)
		elif self.label == Label.ASGN:
			if self.block_num != b_curr:
				b_curr = self.block_num
				print("<bb", str(b_curr)+">")
			t_curr = self.unroll_and_print(t_curr)
			if self.goto_num != -1:
					print("goto <bb", str(self.goto_num)+">")
					print()
		elif self.label == Label.END:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			print("End")
		return b_curr, t_curr


	def print_statement(self):
		if self.label == Label.ASGN:
			lhs = self.children[0]
			rhs = self.children[1]
			lhs.print_statement()
			print(" = ", end='')
			rhs.print_statement()
		elif self.label == Label.VAR:
			print(self.value, end='')
		elif self.label == Label.ADDR:
			print("&", end='')
			self.children[0].print_statement()
		elif self.label == Label.DEREF:
			print("*", end='')
			self.children[0].print_statement()
		elif self.label == Label.CONST:
			print(self.value, end='')
		elif self.label == Label.UMINUS:
			rhs = self.children[0]
			print(nameMapper(self.label)[1], end='')
			rhs.print_statement()
		elif nameMapper(self.label)[0]:
			lhs = self.children[0]
			rhs = self.children[1]
			lhs.print_statement()
			print(nameMapper(self.label)[1], end='')
			rhs.print_statement()

	def will_unroll(self):
		if nameMapper(self.label)[0] :
			for x in self.children:
				if (nameMapper(self.label)[0]):
					return True
		return False
	def unroll_and_print(self, t_curr):
		if self.label==Label.ASGN :
			if self.children[1].will_unroll():
				t_curr = self.children[1].unroll_and_print(t_curr)
				self.children[0].print_statement()
				print(" = "+"t"+str(t_curr))
				return t_curr
			self.children[0].print_statement()
			print(' = ', end = '')
			self.children[1].print_statement()
		elif nameMapper(self.label)[0]:
			if self.label == Label.UMINUS:
				if self.children[0].will_unroll():
					t1 = self.children[0].unroll_and_print(t_curr)
					t_curr = t1+1
					print("t"+str(t_curr)+"="+nameMapper(self.label)[1]+"t"+str(t1), end='')
				else:
					t_curr = t_curr+1
					print("t"+str(t_curr)+"="+nameMapper(self.label)[1], end='')
					self.children[0].print_statement()
			elif(self.children[0].will_unroll() and self.children[1].will_unroll()):
				t1 = self.children[0].unroll_and_print(t_curr)
				t_curr = t1
				t2 = self.children[1].unroll_and_print(t_curr)
				t_curr = t2+1
				print("t"+str(t_curr)+" = "+"t"+str(t1)+nameMapper(self.label)[1]+"t"+str(t2), end='')
			elif(not self.children[0].will_unroll() and not self.children[1].will_unroll()):
				t_curr+=1
				print("t"+str(t_curr)+" = ", end='')
				self.children[0].print_statement()
				print(nameMapper(self.label)[1], end='')
				self.children[1].print_statement()

			elif(self.children[0].will_unroll() and not self.children[1].will_unroll()):
				t1 = self.children[0].unroll_and_print(t_curr)
				t_curr = t1 + 1
				print("t"+str(t_curr)+" = "+"t"+str(t1)+nameMapper(self.label)[1], end='')
				self.children[1].print_statement()
			elif(not self.children[0].will_unroll() and self.children[1].will_unroll()):
				t2 = self.children[1].unroll_and_print(t_curr)
				t_curr = t2 + 1
				print("t"+str(t_curr)+" = ", end='')
				self.children[0].print_statement()
				print(nameMapper(self.label)[1]+"t"+str(t2), end='')
		print()
		return t_curr

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




		