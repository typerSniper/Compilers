from enums import *
import SymTable



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
		Label.UMINUS : '-',
		Label.NOT : '!',
	}
	if x in y:
		return True, y[x]
	else:
		return False, -1


CONDS = [Label.LT, Label.LE, Label.GT, Label.GE, Label.EQ, Label.NE, Label.AND, Label.OR, Label.NOT]
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
		if self.label != Label.FUNCDECL and self.label != Label.FUNCTION:
			self.value = str(value)
		else:
			self.value = value
	def print_without(self, s) :
		print(s, end='')
	def print_tree(self, depth):
		if(self.label==Label.FUNCTION):
			p = self.value
			self.print_without("FUNCTION ")
			print(p.name)
			self.print_without("PARAMS {")
			for k in range(len(p.paramIds)):
				self.print_without('\''+p.paramIds[k] + '\'' +': ')
				self.print_without(p.paramTypes[k])
				if(k!=len(p.paramIds)-1):
					self.print_without(", ")
			print("}")
			self.print_without("RETURNS ")
			print(p.retType)
			self.children[0].print_tree(depth)
			return
		if(self.label==Label.BLOCK):
			for x in self.children:
				x.print_tree(depth)
			return
		# if(self.label==Label.DECL):
		# 	return
		s = ""
		for i in range(depth):
			s = s+"\t"
		if(self.isTerminal):
			disLabel = self.label.name
			if(self.label==Label.INTCONST or self.label==Label.FLOATCONST):
				disLabel = Label.CONST.name
			print(s+ disLabel + "(" + self.value + ")")
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
		elif self.label in CONDS:
			return self.check_declaration(availVars)
		elif self.label == Label.BLOCK:
			q = True
			i=0
			for k in self.children:
				if(k.label==Label.DECL) :
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
			siblings = parent.children[(index+1):]
			for k in siblings:
				if(k.label==Label.DECL) :
					q = q and k.valid_tree(availVars, parent, i)
					break
				q = q and k.valid_tree(availVars, parent, i)
				i+=1
			return q
	def valid_tree(self, scope):
		global scopeList
		if self.label== LABEL.GLOBAL or self.label == Label.FUNCTION:
			scopeCurr = self.value
			q = scopeList.addScope(scopeCurr)
			scopeCurr.setParent(scope)
			for k in self.children and q:
				q = q and k.valid_tree(scopeCurr)
			return q			
		elif self.label == Label.DECL:
			tup = k.children[1].get_name_ind()
			return scope.addVarItem(VarItem(tup[0], DataTypes(typeMapper(k.children[0].label.name.lower()), tup[1])))
		elif self.label == Label.FUNCDECL:
			return scopeList.addScope(self.value)
		elif self.label==BLOCK or self.label==Label.WHILE or self.label==Label.IF:
			q = True
			for k in self.children and q:
				q = q and k.valid_tree(scopeCurr)
			return q
		elif 

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
				g = [True for x in availVars if x[0]==self.value and x[1]==0]
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
			while(curr.label!=Label.VAR):
				if(curr.label==Label.DEREF):
					depth = depth + 1
				elif (curr.label==Label.ADDR):
					depth = depth - 1
				curr = curr.children[0]
			t = (curr.value, depth)
			g = [True  for x in availVars if x[0]==t[0] and ((t[1] <= x[1] and x[1]!=0) or (x[1]==0 and t[1]<x[1])) ]
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
			if not found:
				print("Syntax error at ", end='')
				self.print_statement()
				print()
			return found
	def print_error(self, lineno):
		print("Syntax error at '{1}' on line number {0}".format(str(lineno), str(self.children[0].value) + " ="))

	def print_cfg(self, t_curr):
		if self.label == Label.BLOCK:
			for x in self.children:
				t_curr = x.print_cfg(t_curr)
		elif self.label == Label.WHILE:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			t_curr = self.children[0].unroll_and_print(t_curr)
			print("if(t"+str(t_curr),end='')
			print(") goto <bb", str(b_curr+1)+">")
			print("else goto <bb", str(self.goto_num)+">")
			print()
			for x in self.children[1:]:
				t_curr = x.print_cfg(t_curr)
		elif self.label == Label.IF:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			t_curr = self.children[0].unroll_and_print(t_curr)
			print("if(t"+str(t_curr),end='')
			print(") goto <bb", str(self.children[0].goto_num)+">")
			print("else goto <bb", str(self.goto_num)+">")
			print()
			for x in self.children[1:]:
				t_curr = x.print_cfg(t_curr)
		elif self.label == Label.ASGN:
			if self.block_num != -1:
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
		return t_curr


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
		elif self.label == Label.FLOATCONST or self.label == Label.INTCONST:
			print(self.value, end='')
		elif self.label == Label.UMINUS:
			rhs = self.children[0]
			print(nameMapper(self.label)[1], end='')
			rhs.print_statement()
		elif self.label == Label.NOT:
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
			if self.label == Label.UMINUS or self.label == Label.NOT:
				if self.children[0].will_unroll():
					t1 = self.children[0].unroll_and_print(t_curr)
					t_curr = t1+1
					print("t"+str(t_curr)+" = "+nameMapper(self.label)[1]+"t"+str(t1), end='')
				else:
					t_curr = t_curr+1
					print("t"+str(t_curr)+" = "+nameMapper(self.label)[1], end='')
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
						x.block_num = -1
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
			if len(self.children[1].children) == 0:
				self.children[0].goto_num = goto
			else:
				self.children[0].goto_num = self.block_num + 1
			self.children[1].assign_goto_num(goto)
			if(len(self.children)>=3):
				self.children[2].assign_goto_num(goto)
				self.goto_num = self.children[2].block_num
			else :
				self.goto_num = goto
		elif self.label == Label.WHILE:
			self.goto_num = goto
			self.children[1].assign_goto_num(self.block_num)
	def get_name_ind(self):
		curr = self
		depth = 0
		while(curr.label!=Label.VAR):
			if(curr.label==Label.DEREF):
				depth = depth + 1
			elif (curr.label==Label.ADDR):
				depth = depth - 1
			curr = curr.children[0]
		t = (curr.value, depth)
		return t