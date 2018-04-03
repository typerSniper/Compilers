from enums import *
from SymTable import * 


scopeList = ScopeList()
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
BINOPS = [Label.PLUS, Label.MINUS, Label.MUL, Label.DIV, Label.ASGN]
UNOPS = [Label.UMINUS, Label.DEREF, Label.ADDR] 
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
		if self.label != Label.FUNCDECL and self.label != Label.FUNCTION and self.label!=Label.GLOBAL and self.label != Label.FUNCALL:
			self.value = str(value)
		else:
			self.value = value
	def add_child(self, child):
		self.children.append(child)
	
	def prepend(self, child):
		self.children = [child] + self.children

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
	
	def print_without(self, s) :
		print(s, end='')
	
	def print_tree(self, depth):
		if self.label == Label.GLOBAL:
			for x in self.children:
				x.print_tree(0)
			return
		if(self.label==Label.FUNCTION):
			p = self.value
			self.print_without("FUNCTION ")
			print(p.name)
			self.print_without("PARAMS (")
			p.printParams()
			print(")")
			self.print_without("RETURNS ")
			for i in range(abs(p.retType.indirection)):
				print("*", end='')
			print(p.retType.type.name.lower())
			self.children[0].print_tree(depth+1)
			print()
			return
		if (self.label==Label.FUNCALL):
			s = ""
			for i in range(depth):
				s = s+"\t"
			self.print_without(s)
			self.print_without("CALL "+ self.value+"(")
			print()
			for x in self.children:
				x.print_tree(depth+1)
				if x == self.children[len(self.children)-1] :
					break
				print(s+"\t"+",")
			print(s+" )")
			return	
		if(self.label==Label.BLOCK):
			for x in self.children:
				x.print_tree(depth)
			return
		if(self.label==Label.DECL or self.label==Label.FUNCDECL):
			return
		s = ""
		if(self.label==Label.RETURN):
			depth-=1
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
	# def valid_tree(self, availVars, parent, index):
	# 	if self.label==Label.ASGN :
	# 		return self.check_assign() and self.check_declaration(availVars)
	# 	elif self.label==Label.WHILE or self.label==Label.IF:
	# 		q = True
	# 		i=0
	# 		for k in self.children:
	# 			q = q and k.valid_tree(availVars, self, i)
	# 			if not q:
	# 				break
	# 			i+=1
	# 		return q
	# 	elif self.label in CONDS:
	# 		return self.check_declaration(availVars)
	# 	elif self.label == Label.BLOCK:
	# 		q = True
	# 		i=0
	# 		for k in self.children:
	# 			if(k.label==Label.DECL) :
	# 				q = q and k.valid_tree(availVars, self, i)
	# 				break
	# 			q = q and k.valid_tree(availVars, self, i)
	# 			i+=1
	# 		return q
	# 	elif self.label==Label.DECL :
	# 		q = True
	# 		i=index+1
	# 		new_vars = self.update_vars()
	# 		for x in new_vars:
	# 			if x[0] in [y[0] for y in availVars]:
	# 				print("ERROR: Double declaration for", x[0])
	# 				return False
	# 		availVars = availVars + new_vars
	# 		siblings = parent.children[(index+1):]
	# 		for k in siblings:
	# 			if(k.label==Label.DECL) :
	# 				q = q and k.valid_tree(availVars, parent, i)
	# 				break
	# 			q = q and k.valid_tree(availVars, parent, i)
	# 			i+=1
	# 		return q
	def valid_tree(self, scope):
		global scopeList
		if self.label== Label.GLOBAL or self.label == Label.FUNCTION:
			scopeCurr = self.value
			q = scopeList.addScope(scopeCurr)
			scopeCurr.setParent(scope)
			for k in self.children:
				if not q:
					break
				q = q and k.valid_tree(scopeCurr)
			return q			
		elif self.label == Label.DECL:
			q = True
			for k in self.children[1:]:
				if not q:
					break
				tup = k.get_name_ind()
				q = q and scope.addVarItem(VarItem(tup[0], DataTypes(typeMapper(self.children[0].label.name.lower()), tup[1], True)))
			return q
		elif self.label == Label.FUNCDECL:
			return scopeList.addScope(self.value)
		elif self.label==Label.BLOCK or self.label==Label.WHILE or self.label==Label.IF:
			q = True
			for k in self.children:
				if not q:
					break
				q = q and k.valid_tree(scope)
				#TUKKA
			return q
		elif self.label == Label.ASGN:
			return self.check_assign() and self.getTypeAndCheck(scope)[1]
		elif self.label in BINOPS + UNOPS + CONDS:
			return self.getTypeAndCheck(scope)[1]
		elif self.label == Label.FUNCALL:
			return self.getTypeAndCheck(scope)[1]
		elif self.label == Label.RETURN:
			if(scope.retType.type==DataTypeEnum.VOID):
				if len(self.children) == 0:
					return True
				else:
					print("DEBUG_WRONG_RETURN_TYPE")
					return False
			elif len(self.children) == 1:
				retType = self.children[0].getTypeAndCheck(scope)
				if(retType[1]):
					if (retType[0].isSameType(scope.retType)):
						if(retType[0].usable):
							return True
						else :
							print("DEBUG_DIRECT_USE_NON_POINTER")
					else:
						print("DEBUG_RETURN_TYPE_MISMATCH")
			else:
				print("DEBUG_RETURN_TYPE_MISMATCH")
				return False
		return False

	def getTypeAndCheck(self, scope):
		global scopeList
		if self.label in BINOPS:
			lhsType = self.children[0].getTypeAndCheck(scope)
			rhsType = self.children[1].getTypeAndCheck(scope)
			if(lhsType[1] and rhsType[1]):
				if lhsType[0].isSameType(rhsType[0]) : 
					if rhsType[0].usable and lhsType[0].usable:
						if(lhsType[0].addressable and self.label==Label.ASGN):
							return (lhsType[0], True)
						elif(lhsType[0].indirection==0 and self.label!=Label.ASGN):
							return (lhsType[0], True)
						else :
							print("DEBUG_INVALID_OPERANDS")
					else:
						print("DEBUG_DIRECT_USE_NON_POINTER")
				else:
					print("DEBUG_TYPE_MISMATCH")
			return (None, False)
		elif self.label in UNOPS:
			childType = self.children[0].getTypeAndCheck(scope)
			if childType[1]:
				if self.label == Label.UMINUS and childType[0].indirection == 0 and childType[0].usable:
					return(childType[0], True)
				elif self.label == Label.ADDR and childType[0].addressable:
					childType[0].addressable = False
					childType[0].usable = True
					childType[0].indirection -= 1
					if(self.children[0].label!=Label.VAR):
						print("DEBUG_CANNOT_USE_AMP_DIRECTLY")
						return(None, False)
					return(childType[0], True)
				elif self.label==Label.DEREF and childType[0].indirection<0:
					childType[0].indirection+=1
					childType[0].usable = True
					return(childType[0], True)
				print(childType[0].indirection)
				print("#####DEBUG_CHUNK#######")
				self.print_tree(0)
			return (None, False)
		elif self.label in CONDS:
			lhsType = self.children[0].getTypeAndCheck(scope)
			if not lhsType[0].usable:
				print("DEBUG_DIRECT_USE_NON_POINTER")
				return (None, False)
			if self.label == Label.NOT and lhsType[1]:
				return (lhsType[0], True)
			rhsType = self.children[1].getTypeAndCheck(scope)
			if not rhsType[0].usable:
				print("DEBUG_DIRECT_USE_NON_POINTER")
				return (None, False)
			if(lhsType[1] and rhsType[1]):
				if(self.label in [Label.OR, Label.AND] ):
					return (None, True)
				elif lhsType[0].isSameType(rhsType[0]):
					return (None, True)
				print("#####DEBUG_CHUNK#######")
				self.print_tree(0)				
			return (None, False)
		elif self.label == Label.FUNCALL:
			funcName = str(self.value)
			if(funcName in scopeList.scopeList):
				funcScope = scopeList.scopeList[funcName]
				if len(self.children) == len(funcScope.paramIds):
					q = True
					for k in range(len(self.children)):
						argType = self.children[k].getTypeAndCheck(scope)
						if(argType[1] and argType[0].isSameType(funcScope.paramTypes[k])):
							q = q and True
						else :
							print("DEBUG_TYPE_MISMATCH")
							return (None, False)
					y = funcScope.retType.getCopy()
					y.indirection = -1*y.indirection
					return (y, q)
				else :
					print("DEBUG_NUMBER_OF_ARGS_MISMATCH")
			else :
				print("DEBUG_FUNCNAME_NOT_DEFINED")
			return (None, False)
		elif self.label== Label.INTCONST:
			p = DataTypes(DataTypeEnum.INT, 0, False)
			p.setUsable()
			return (p, True)
		elif self.label== Label.FLOATCONST:
			p = DataTypes(DataTypeEnum.FLOAT, 0, False)
			p.setUsable()
			return (p, True)
		elif self.label == Label.VAR:
			q = scope.getType(self.value)
			if q is not None:
				y = DataTypes(q.type, -1*q.indirection, q.addressable)
				return (y, True)
			print("VARIABLE", self.value, "NOT DEFINED IN THIS SCOPE")
			return(None, False)
			#lhsType(always addressable)-> if *  rhs anything with same type,  
			#	otherwise, rhs must be addressable(that is already handled)
			# uISNG NONE FOR BOOLS AS WELL ATM

	# # def update_vars(self):
	# 	vars_ = []
	# 	for k in self.children:
	# 		if k.label == Label.DVAR:
	# 			c = k.children[0]
	# 			depth = 0
	# 			while True:
	# 				if c.label == Label.VAR:
	# 					vars_.append((c.value, depth))
	# 					break
	# 				else:
	# 					depth+=1
	# 					c=c.children[0]
	# 	return vars_
	
	# def check_declaration(self, availVars):
	# 	g = True
	# 	if self.label == Label.VAR:
	# 		if self.value in [x[0] for x in availVars]:
	# 			g = [True for x in availVars if x[0]==self.value and x[1]==0]
	# 			if len(g) > 0:
	# 				print("Direct use of non-pointer variable")
	# 				return False
	# 			return True
	# 		else:
	# 			print("ERROR:", self.value, "Not Defined")
	# 			return False
	# 	elif self.label == Label.DEREF or self.label == Label.ADDR:
	# 		curr = self
	# 		depth = 0
	# 		while(curr.label!=Label.VAR):
	# 			if(curr.label==Label.DEREF):
	# 				depth = depth + 1
	# 			elif (curr.label==Label.ADDR):
	# 				depth = depth - 1
	# 			curr = curr.children[0]
	# 		t = (curr.value, depth)
	# 		g = [True  for x in availVars if x[0]==t[0] and ((t[1] <= x[1] and x[1]!=0) or (x[1]==0 and t[1]<x[1])) ]
	# 		if len(g):
	# 			return True
	# 		else:
	# 			print("ERROR: TOO MUCH INDIRECTION")
	# 			return False
	# 	for k in self.children:
	# 		g = g and k.check_declaration(availVars)
	# 	return g
	
	
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
				if curr.label == Label.FUNCALL:
					found = True
					break
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
		if self.label == Label.GLOBAL or self.label == Label.BLOCK:
			for x in self.children:
				t_curr = x.print_cfg(t_curr)
		elif self.label == Label.FUNCTION:
			print("function "+ self.value.name+ "(", end='')
			self.value.printParams()
			print(")")
			for x in self.children:
				t_curr = x.print_cfg(t_curr)
			print()
		elif self.label == Label.RETURN:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			if len(self.children) > 0:
				if self.children[0].will_unroll():
					t_curr = self.children[0].unroll_and_print(t_curr)
					print("return t"+str(t_curr))
				else:
					print("return ", end='')
					self.children[0].print_statement()
			else:
				print("return")
		elif self.label == Label.WHILE:
			b_curr = self.block_num
			print("<bb", str(b_curr)+">")
			t_curr = self.children[0].unroll_and_print(t_curr)
			print("if(t"+str(t_curr),end='')
			print(") goto <bb", str(self.children[0].goto_num)+">")
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
		elif self.label == Label.FUNCALL:
			if self.will_unroll():
				t_curr = self.unroll_and_print(t_curr)
			else:
				self.print_statement()
		return t_curr

	def print_statement(self):
		if self.label == Label.ASGN:
			lhs = self.children[0]
			rhs = self.children[1]
			lhs.print_statement()
			print(" = ", end='')
			rhs.print_statement()
		elif self.label == Label.FUNCALL:
			print(self.value, end='(')
			for x in self.children[:-1]:
				x.print_statement()
				print(", ", end='')
			self.children[-1].print_statement()
			print(")", end='')
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
		if self.label == Label.FUNCALL:
			for x in self.children:
				if x.will_unroll():
					return True
		return False

	def unroll_funcall(self, t_curr):
		a = []
		for x in self.children:
			if x.will_unroll():
				t_curr = x.unroll_and_print(t_curr)
				a.append("t"+str(t_curr))
			else:
				a.append(-1)
		return a, t_curr

	def print_funcall(self, rhs_array):
		print(self.value + "(", end='')
		for x in range(len(rhs_array)-1):
			if rhs_array[x] == -1:
				self.children[x].print_statement()
				print(", ", end='')
			else:
				print(rhs_array[x], end=', ')
		if rhs_array[-1] == -1:
			self.children[-1].print_statement()
		else:
			print(rhs_array[-1], end='')
		print(")", end='')

	def funcall_helper_and_unroll(self, index, t_curr):
		if self.children[index].label == Label.FUNCALL:
			rhs_array, t_curr = self.children[index].unroll_funcall(t_curr)
			return True, t_curr, rhs_array
		else:
			t_curr = self.children[index].unroll_and_print(t_curr)
		return False, t_curr, None

	def unroll_and_print(self, t_curr):
		if self.label==Label.ASGN :
			if self.children[1].will_unroll():
				f_h = self.funcall_helper_and_unroll(1, t_curr)
				t_curr = f_h[1]
				self.children[0].print_statement()
				print(' = ', end = '')
				if f_h[0]:
					self.children[1].print_funcall(f_h[2])
					print()
				else:
					print("t"+str(t_curr))
				# if self.children[1].label == Label.FUNCALL:
				# 	rhs_array, t_curr = self.children[1].unroll_funcall(t_curr)
					
					
				# else:
				# 	t_curr = self.children[1].unroll_and_print(t_curr)
				# 	self.children[0].print_statement()
				# 	print(' = ', end = '')
					
				return t_curr
			self.children[0].print_statement()
			print(' = ', end = '')
			self.children[1].print_statement()
		elif self.label == Label.FUNCALL:
			rhs_array, t_curr = self.unroll_funcall(t_curr)
			self.print_funcall(rhs_array)
			print()
		elif nameMapper(self.label)[0]:
			if self.label == Label.UMINUS or self.label == Label.NOT:
				if self.children[0].will_unroll():
					f_h = self.funcall_helper_and_unroll(0, t_curr)
					t1 = f_h[1]
					t_curr = t1+1
					print("t"+str(t_curr)+" = ", end='')
					if f_h[0]:
						self.children[0].print_funcall(f_h[2])
					else:
						print(nameMapper(self.label)[1]+"t"+str(t1), end='')
				else:
					t_curr = t_curr+1
					print("t"+str(t_curr)+" = "+nameMapper(self.label)[1], end='')
					self.children[0].print_statement()
			elif(self.children[0].will_unroll() and self.children[1].will_unroll()):
				f_h_1 = self.funcall_helper_and_unroll(0, t_curr)
				t1 = f_h_1[1]
				t_curr = t1
				f_h_2 = self.funcall_helper_and_unroll(1, t_curr)
				t2 = f_h_2[1]
				t_curr = t2+1
				print("t"+str(t_curr)+" = ", end='')
				if f_h_1[0]:
					self.children[0].print_funcall(f_h_1[2])
				else:
					print("t"+str(t1), end='')
				print(nameMapper(self.label)[1], end='')
				if f_h_2[0]:
					self.children[1].print_funcall(f_h_2[2])
				else:
					print("t"+str(t2), end='')
			elif(not self.children[0].will_unroll() and not self.children[1].will_unroll()):
				t_curr+=1
				print("t"+str(t_curr)+" = ", end='')
				self.children[0].print_statement()
				print(nameMapper(self.label)[1], end='')
				self.children[1].print_statement()
			elif(self.children[0].will_unroll() and not self.children[1].will_unroll()):
				f_h_1 = self.funcall_helper_and_unroll(0, t_curr)
				t1 = f_h_1[1]
				t_curr = t1 + 1
				print("t"+str(t_curr)+" = ", end='')
				if f_h_1[0]:
					self.children[0].print_funcall(f_h_1[2])
				else:
					print("t"+str(t1), end='')
				print(nameMapper(self.label)[1], end='')
				self.children[1].print_statement()
			elif(not self.children[0].will_unroll() and self.children[1].will_unroll()):
				f_h_2 = self.funcall_helper_and_unroll(1, t_curr)
				t2 = f_h_2[1]
				t_curr = t2 + 1
				print("t"+str(t_curr)+" = ", end='')
				self.children[0].print_statement()
				print(nameMapper(self.label)[1], end='')
				if f_h_2[0]:
					self.children[1].print_funcall(f_h_2[2])
				else:
					print("t"+str(t2), end='')
		print()
		return t_curr

	def assign_blocks(self, num):
		if self.label == Label.GLOBAL:
			for x in self.children:
				num = x.assign_blocks(num)
		elif self.label == Label.FUNCDECL:
			return num
		elif self.label == Label.FUNCTION:
			if self.value.name == "main": #BAAD
				self.children[0].children.append(Abstree([], Label.RETURN, False, -1))
			return self.children[0].assign_blocks(num)
		elif self.label == Label.BLOCK:
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
		elif self.label == Label.RETURN:
			num+=1
			self.block_num = num
		return num

	def assign_goto_num(self, goto):
		if self.label == Label.GLOBAL or self.label == Label.FUNCTION:
			for x in self.children:
				x.assign_goto_num(goto)
		elif self.label == Label.BLOCK:
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
				self.children[0].goto_num = self.children[1].block_num
			self.children[1].assign_goto_num(goto)
			if(len(self.children)>=3):
				self.children[2].assign_goto_num(goto)
				self.goto_num = self.children[2].block_num
			else :
				self.goto_num = goto
		elif self.label == Label.WHILE:
			if len(self.children[1].children) == 0:
				self.children[0].goto_num = self.block_num
			else:
				self.children[0].goto_num = self.children[1].block_num
			self.goto_num = goto
			self.children[1].assign_goto_num(self.block_num)












