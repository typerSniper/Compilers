import global_
from enums import *

# if global on rhs -> lw
# on lhs -> 

class VarMaps:
	def __init__(self):
		self.maps = {} #var to register
		self.regUsedInt = []
		self.regUsedFloat = []
		self.tempTypes = {}
	def getMinUsable(self, type_):
		x = 0
		if type_.isFloat():
			x = self.regUsedFloat
			y = 10
		else:
			x = self.regUsedInt
			y = 0
		while 1:
			if y not in x:
				x.append(y)
				return y
			y+=1
	def addMapping(self, x, type_):
		self.maps[x] = self.getMinUsable(type_)
		self.tempTypes[x] = type_
		return self.maps[x]
	def freeTempReg(self, x, type_):
		if not type_.isFloat():
			self.regUsedInt.remove(x)
		else:
			self.regUsedFloat.remove(x)
	def freeNamedReg(self, x, type_):
		self.freeTempReg(int(''.join(filter(str.isdigit, str(x)))), type_)


class VarType:
	def __init__(self, type_, indir):
		self.type = type_
		self.ind = indir
	def isFloat(self):
		return self.type == DataTypeEnum.FLOAT and self.ind == 0

varMapping = VarMaps()

def regStringMapper(x, type_):
	if x >= 0:
		if not type_.isFloat():
			return "$s"+str(x)
		else:
			return "$f"+str(x)
	else :
		if x==-1:
			return "$sp"
		elif x==-2:
			return "$fp"
		elif x==-3:
			return "$ra"
		elif x==-4:
			return "$v1"

CONDS = [Label.LT, Label.LE, Label.GT, Label.GE, Label.EQ, Label.NE, Label.AND, Label.OR, Label.NOT]

class CFG:
	def __init__(self, children, label, isInner, value):
		self.label = label
		self.children = children
		self.value = value
		self.pSet = InstructionSet()
	def print_tree(self):
		print(self.label, self.value,end = ' ')
		i = 0
		for x in self.children:
			print("CHILD ", i, end = ' ')
			x.print_tree()
			i= i + 1
		print()
	def printPrologue(self, funcName):
		self.pSet.printLoadStore(False, regStringMapper(-3, None), regStringMapper(-1, None), 0, )
		self.pSet.printLoadStore(False, regStringMapper(-2, None), regStringMapper(-1, None), -4)
		self.pSet.printOps("sub", regStringMapper(-2, None), regStringMapper(-1, None), 8)
		localSpace =  global_.scopeList.scopeList[self.value].getLocalSpace()
		self.pSet.printOps("sub", regStringMapper(-1, None), regStringMapper(-1, None), localSpace+8)
		global_.scopeList.scopeList[funcName].scope_width = localSpace
	def printEpilogue(self):
		print("epilogue_"+self.value+":")
		localSpace =  global_.scopeList.scopeList[self.value].getLocalSpace()
		self.pSet.printOps("add", regStringMapper(-1, None), regStringMapper(-1, None), localSpace+8)
		self.pSet.printLoadStore(True, regStringMapper(-2, None), regStringMapper(-1, None), -4)
		self.pSet.printLoadStore(True, regStringMapper(-3, None), regStringMapper(-1, None), 0)
		self.pSet.printJumpReg(regStringMapper(-3, None))

	def getVar(self, funcName):
		offset = global_.scopeList.scopeList[funcName].getOffset(self.value)
		if offset is None:
			return True, None, None
		type_ = global_.scopeList.scopeList[funcName].varTable[self.value].type
		type_ = VarType(type_.type, type_.indirection)
		regNum = varMapping.getMinUsable(type_)
		self.pSet.printLoadStore(True, regStringMapper(regNum, type_), regStringMapper(-1, None), offset)
		return False, regStringMapper(regNum, type_), type_

	def getAtom(self, funcName):
		name = ""
		isGlobal = False
		type_ = None
		if self.label==Label.VAR:
			isGlobal, name, type_ = self.getVar(funcName)
		elif self.label == Label.TEMP:
			type_ = varMapping.tempTypes[self.value]
			name = regStringMapper(varMapping.maps[self.value], type_)
		elif self.label == Label.FLOATCONST or self.label == Label.INTCONST:
			if self.label == Label.FLOATCONST:
				type_ = VarType(DataTypeEnum.FLOAT, 0)
			else:
				type_ = VarType(DataTypeEnum.INT, 0)
			name = self.getImm(self.value, type_)
		if isGlobal:
			name = "global_"+self.value
			type_ = global_.scopeList.scopeList["GLOBAL"].varTable[self.value].type
			type_ = VarType(type_.type, type_.indirection)
			temp = varMapping.getMinUsable(type_)
			self.pSet.printLoadStoreGlobal(True, regStringMapper(temp, type_), name)
			name = regStringMapper(temp, type_)
		return name, type_

	def getTerminal(self, funcName):
		curr = self
		ind = 0
		while len(curr.children) > 0:
			if curr.label == Label.DEREF:
				ind +=1
			else:
				ind -=1
			curr = curr.children[0]
		if ind == 0:
			return curr.getAtom(funcName)
		elif ind < 0:
			offset = global_.scopeList.scopeList[funcName].getOffset(curr.value)
			tempReg = varMapping.getMinUsable(VarType(DataTypeEnum.INT, 0))
			if offset is None:
				name = "global_"+curr.value
				self.pSet.printLoadAddress(regStringMapper(tempReg, VarType(DataTypeEnum.INT, 0)), name)
			else:
				self.pSet.printOps("addi", regStringMapper(tempReg, VarType(DataTypeEnum.INT, 0)), regStringMapper(-1, None), offset)
			return regStringMapper(tempReg, VarType(DataTypeEnum.INT, 0)), VarType(DataTypeEnum.INT, 0)
		elif ind > 0:
			name, type_ = curr.getAtom(funcName)
			f = False
			if -1*type_.ind == ind:
				f = True
			curr_name = name
			type_1 = VarType(DataTypeEnum.INT, 0)
			type_2 = VarType(type_.type, type_.ind+ind)
			while ind != 0:
				if ind == 1 and f:
					tempReg = varMapping.getMinUsable(type_2)
					self.pSet.printLoadStore(True, regStringMapper(tempReg, type_2), curr_name, 0)
					varMapping.freeNamedReg(curr_name, type_1)
					curr_name = regStringMapper(tempReg, type_2)
				else:
					tempReg = varMapping.getMinUsable(type_1)
					self.pSet.printLoadStore(True, regStringMapper(tempReg, type_1), curr_name, 0)
					varMapping.freeNamedReg(curr_name, type_1)
					curr_name = regStringMapper(tempReg, type_1)
				ind -= 1
			return curr_name, type_2

	def getImm(self, x, type_):
		reg = varMapping.getMinUsable(type_)
		self.pSet.printLoadImm(regStringMapper(reg, type_), x)
		return regStringMapper(reg, type_)

	def printNode(self, funcName):
		p = "\t"
		if self.label == Label.BLOCK_NUM:
			print()
			print("label"+str(self.value)+":")
		elif self.label == Label.FUNCALL:
			finReg, type_ = self.resolve_reg(self.funcName)
		elif self.label == Label.FUNCTION:
			print(self.value+":")
		elif self.label == Label.ASGN:
			lhs = self.children[0]
			rhs = self.children[1]
			finReg, type_ = self.resolve_reg(rhs, funcName)
			if len(lhs.children) == 0:
				if lhs.label == Label.TEMP:
					lhsReg = varMapping.addMapping(lhs.value, type_)
					self.pSet.printMove(regStringMapper(lhsReg, type_), finReg)
					varMapping.freeNamedReg(finReg, type_)
				else:
					offset = global_.scopeList.scopeList[funcName].getOffset(lhs.value)
					if offset is None:
						lhsString = "global_"+lhs.value
						self.pSet.printLoadStoreGlobal(False, finReg, lhsString) #he sure
					else:
						self.pSet.printLoadStore(False, finReg, regStringMapper(-1, None), offset)
					varMapping.freeNamedReg(finReg, type_)
			else:
				tempReg, type_lhs = lhs.children[0].getTerminal(funcName)
				self.pSet.printLoadStore(False, finReg, tempReg, 0)
				varMapping.freeNamedReg(finReg, type_)
				varMapping.freeNamedReg(tempReg, type_lhs)
		elif self.label == Label.RETURN:
			if len(self.children) > 0:
				finReg, type_ = self.resolve_reg(self.children[0], funcName)
				self.pSet.printMove(regStringMapper(-4, None), finReg)
				varMapping.freeNamedReg(finReg, type_)
		elif self.label == Label.GOTO_NUM:
			self.pSet.printJump(self.value)
		elif self.label == Label.IF:
			j_label = self.children[1].value
			t_reg, type_ = self.children[0].getTerminal(funcName)
			self.pSet.printBNE(t_reg, "$0", j_label)
			varMapping.freeNamedReg(t_reg, type_)
		elif self.label == Label.ELSE:
			self.children[0].printNode(funcName)
	def resolve_reg(self, rhs, funcName):
		finReg = -1
		type_fin = None
		if rhs.label == Label.FUNCALL: # he says
			num_args = len(rhs.children) #ASSUMPTION SIZE ARG IS ALWAYS 4
			p_offset = -1*(len(rhs.children)-1)*4 ##TUKKA
			for x in range(num_args):
				x_name, x_type = rhs.children[x].getTerminal(funcName)
				self.pSet.printLoadStore(False, x_name, regStringMapper(-1, None), p_offset)
				varMapping.freeNamedReg(x_name, x_type)
				p_offset+=4
			self.pSet.printOps("sub", regStringMapper(-1, None), regStringMapper(-1, None), num_args*4)
			self.pSet.printJal(rhs.value)
			self.pSet.printOps("add", regStringMapper(-1, None), regStringMapper(-1, None), num_args*4)
			ret_type = global_.scopeList.scopeList[rhs.value].retType
			ret_type = VarType(ret_type.type, ret_type.indirection) 
			tempReg = varMapping.getMinUsable(ret_type)
			# print(funcName)
			self.pSet.printMove(regStringMapper(tempReg, ret_type), regStringMapper(-4, None))
			finReg = regStringMapper(tempReg, ret_type)
			type_fin = ret_type
		elif len(rhs.children)==2:
			lhs_1 = rhs.children[0]
			rhs_1 = rhs.children[1]
			lhs_name, type_1 = lhs_1.getTerminal(funcName) 
			rhs_name, type_2 = rhs_1.getTerminal(funcName)
			operator_ = instMapper(rhs.label)
			tempReg = -1
			type_rhs = None
			if rhs.label in CONDS:
				type_rhs = VarType(DataTypeEnum.INT, 0)
			else:
				type_rhs = type_1
			if len(operator_)==1 and rhs.label!=Label.GT:
				tempReg = varMapping.getMinUsable(type_rhs)
				self.pSet.printOps(operator_[0], regStringMapper(tempReg, type_rhs), lhs_name, rhs_name)
				varMapping.freeNamedReg(lhs_name, type_1)
				varMapping.freeNamedReg(rhs_name, type_2)
			elif rhs.label==Label.GT:
				tempReg = varMapping.getMinUsable(type_rhs)
				self.pSet.printOps(operator_[0], regStringMapper(tempReg, type_rhs), rhs_name, lhs_name)
				varMapping.freeNamedReg(lhs_name, type_1)
				varMapping.freeNamedReg(rhs_name, type_2)
			else :
				tempReg = varMapping.getMinUsable(type_rhs)
				if rhs.label==Label.LE:
					self.pSet.printOps(operator_[0], regStringMapper(tempReg, type_rhs), rhs_name, lhs_name)
				else :
					assert(rhs.label==Label.GE)
					self.pSet.printOps(operator_[0], regStringMapper(tempReg, type_rhs), lhs_name, rhs_name)
				varMapping.freeNamedReg(lhs_name, type_1)
				varMapping.freeNamedReg(rhs_name, type_2)
				tempReg2 = varMapping.getMinUsable(VarType(DataTypeEnum.INT, 0))
				self.pSet.printNot(regStringMapper(tempReg2, VarType(DataTypeEnum.INT, 0)), regStringMapper(tempReg, type_rhs))
				varMapping.freeNamedReg(tempReg, VarType(DataTypeEnum.INT, 0))
				tempReg = tempReg2
			finReg = regStringMapper(tempReg, type_rhs)
			type_fin = type_rhs
		elif len(rhs.children) == 1:
			tempReg = -1
			if rhs.label == Label.UMINUS:
				lhs_name, type_1 = rhs.children[0].getTerminal(funcName)
				tempReg = varMapping.getMinUsable(type_1)
				if not type_1.isFloat():
					tempReg2 = self.getImm(-1, type_1)
				else:
					tempReg2 = self.getImm(-1.0, type_1)
				self.pSet.printOps("mul", regStringMapper(tempReg, type_1), lhs_name, tempReg2)
				varMapping.freeNamedReg(lhs_name, type_1)
				varMapping.freeNamedReg(tempReg2, type_1)	
				type_fin = type_1			
			elif rhs.label == Label.NOT:
				# print("DEBUG+", rhs.children[0].label)
				lhs_name, type_1 = rhs.children[0].getTerminal(funcName)
				# print("DEBUG+", lhs_name)
				type_fin = VarType(DataTypeEnum.INT, 0)
				tempReg = varMapping.getMinUsable(type_fin)
				self.pSet.printNot(regStringMapper(tempReg, type_fin), lhs_name)
				varMapping.freeNamedReg(lhs_name, type_1)
			else:
				return rhs.getTerminal(funcName) 
			finReg = regStringMapper(tempReg, type_fin)
		else :
			return rhs.getTerminal(funcName)
		return finReg, type_fin

def isFloat(reg):
	return 'f' in str(reg) and 'p' not in str(reg)


class InstructionSet:
	def __init__(self):
		self.emp = True
	def printLoadStore(self, isLoad, firstReg, secondReg, offset):
		s = ''
		if isFloat(firstReg) or isFloat(secondReg):
			s = "\ts.s"
			if isLoad:
				s = "\tl.s"
		else:
			s = "\tsw"
			if isLoad:
				s = "\tlw"
		print(s, firstReg+ "," ,str(offset)+"("+secondReg+")")
	def printLoadImm(self, reg, c):
		if isFloat(reg):
			print("\tli.s", reg+",", c)
		else:
			print("\tli", reg+",", c)
	def printOps(self, opLabel, firstReg, secondReg, thirdReg):
		s = opLabel
		s = "\t" + s
		if isFloat(firstReg):
			s+='.s'
		print(s, firstReg+ "," ,secondReg+",", thirdReg)
	def printBNE(self, firstReg, secondReg, label_no):
		print("\tbne", firstReg+",", secondReg+",", "label"+str(label_no))
	def printJumpReg(self, regName):
		print("\tjr", regName)
	def printJump(self, label_no):
		print("\tj", "label"+str(label_no))
	def printJal(self, funcName):
		print("\tjal", funcName)
	def printNot(self, reg1, reg2):
		print("\tnot", reg1+",", reg2)
	def printMove(self, reg1, reg2):
		if isFloat(reg1) or isFloat(reg2):
			print("\tmove.s", reg1+",", reg2)
		else:
			print("\tmove", reg1+",", reg2)
	def printLoadStoreGlobal(self, isLoad, reg, glob):
		s = ''
		if isFloat(reg):
			s = "\tsw.s"
			if isLoad:
				s = "\tlw.s"
		else:
			s = "\tsw"
			if isLoad:
				s = "\tlw"
		print(s, reg+",", glob)
	def printLoadAddress(self, reg, glob):
		print("\tla", reg+",", glob)


def print_global():
	print()
	print("\t.data")
	print_list = []
	for var in global_.scopeList.scopeList["GLOBAL"].varTable.values():
		print_list.append(var.name)
	print_list.sort()
	for x in print_list:
		print("global_"+x+":\t", end='') 
		p = global_.scopeList.scopeList["GLOBAL"].varTable[x].type
		if p.type == DataTypeEnum.FLOAT and p.indirection != 0:
			print(".space\t8")
		else:
			print(".word"+"\t0")
	print()


def printMips(index, funcName):
	currNode = global_.cfg[index]
	if currNode.label == Label.FUNCTION:
		print("\t.text")
		print("\t.globl", currNode.value)
		currNode.printNode(currNode.value)
		funcName = currNode.value
		funcEnd = global_.funcIndices[currNode.value][1]
		j = index + 1
		currNode.printPrologue(funcName)
		#Add Prologue
		while j <= funcEnd:
			printMips(j, funcName)
			j+=1
		#ADD Epilogue
		print("\tj epilogue_"+funcName)
		print()
		currNode.printEpilogue()
		print()
		return j
	else :
		currNode.printNode(funcName)
		return index + 1
