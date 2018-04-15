import global_
from enums import *

# if global on rhs -> lw
# on lhs -> 

class VarMaps:
	def __init__(self):
		self.maps = {} #var to register
		self.regUsed = []
	def getMinUsable(self):
		x = 0
		while 1:
			if x not in self.regUsed:
				self.regUsed.append(x)
				return x
			x+=1
	def freeReg(self, x):
		if x in self.maps:
			self.regUsed.remove(self.maps[x])
			del self.maps[x]
			return
		print("SOMETHING WENT WRONG")

	def addMapping(self, x):
		self.maps[x] = self.getMinUsable()
		return self.maps[x]
	def freeTempReg(self, x):
		self.regUsed.remove(x)
	def freeNamedReg(self, x):
		self.freeTempReg(int(''.join(filter(str.isdigit, str(x)))))

varMapping = VarMaps()

def regStringMapper(x):
	if x>=0:
		return "$s"+str(x)
	else :
		if x==-1:
			return "$sp"
		elif x==-2:
			return "$fp"
		elif x==-3:
			return "$ra"
		elif x==-4:
			return "$v1"

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
		self.pSet.printLoadStore(False, regStringMapper(-3), regStringMapper(-1), 0)
		self.pSet.printLoadStore(False, regStringMapper(-2), regStringMapper(-1), -4)
		self.pSet.printOps("sub", regStringMapper(-2), regStringMapper(-1), 8)
		localSpace =  global_.scopeList.scopeList[self.value].getLocalSpace()
		self.pSet.printOps("sub", regStringMapper(-1), regStringMapper(-1), localSpace+8)
		global_.scopeList.scopeList[funcName].scope_width = localSpace
	def printEpilogue(self):
		print("epilogue_"+self.value+":")
		localSpace =  global_.scopeList.scopeList[self.value].getLocalSpace()
		self.pSet.printOps("add", regStringMapper(-1), regStringMapper(-1), localSpace+8)
		self.pSet.printLoadStore(True, regStringMapper(-2), regStringMapper(-1), -4)
		self.pSet.printLoadStore(True, regStringMapper(-3), regStringMapper(-1), 0)
		self.pSet.printJumpReg(regStringMapper(-3))
	def getVar(self, funcName):
		offset = global_.scopeList.scopeList[funcName].getOffset(self.value)
		if offset is None:
			return True, None
		regNum = varMapping.getMinUsable()
		self.pSet.printLoadStore(True, regStringMapper(regNum), regStringMapper(-1), offset)
		return False, regStringMapper(regNum)
	def getAtom(self, funcName):
		name = ""
		isGlobal = False
		if self.label==Label.VAR:
			# print("DEBUG++", isGlobal)
			isGlobal, name = self.getVar(funcName)
			# print("DEBUG++", isGlobal)
		elif self.label == Label.TEMP:
			name = regStringMapper(varMapping.maps[self.value])
		elif self.label == Label.FLOATCONST or self.label == Label.INTCONST:
			name = self.getImm(self.value)
		if isGlobal:
			name = "global_"+self.value
			temp = varMapping.getMinUsable()
			self.pSet.printLoadStoreGlobal(True, regStringMapper(temp), name)
			name = regStringMapper(temp)
		return name
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
			if offset is None:
				name = "global_"+curr.value
				tempReg = varMapping.getMinUsable()
				self.pSet.printLoadAddress(regStringMapper(tempReg), name)
				return regStringMapper(tempReg)
			else:
				tempReg = varMapping.getMinUsable()
				self.pSet.printOps("addi", regStringMapper(tempReg), regStringMapper(-1), offset)
				return regStringMapper(tempReg)
		elif ind > 0:
			name = curr.getAtom(funcName)
			curr_name = name
			while ind != 0:
				tempReg = varMapping.getMinUsable()
				self.pSet.printLoadStore(True, regStringMapper(tempReg), curr_name, 0)
				varMapping.freeNamedReg(curr_name)
				curr_name = regStringMapper(tempReg)
				ind -= 1
			return curr_name

	def getImm(self, x):
		reg = varMapping.getMinUsable()
		self.pSet.printLoadImm(regStringMapper(reg), x)
		return regStringMapper(reg)
	def printNode(self, funcName):
		p = "\t"
		if self.label == Label.BLOCK_NUM:
			print()
			print("label"+str(self.value)+":")
		elif self.label == Label.FUNCTION:
			print(self.value+":")
		elif self.label == Label.ASGN:
			lhs = self.children[0]
			rhs = self.children[1]
			finReg = self.resolve_reg(rhs, funcName)
			if len(lhs.children) == 0:
				if lhs.label == Label.TEMP:
					lhsReg = varMapping.addMapping(lhs.value)
					self.pSet.printMove(regStringMapper(lhsReg), finReg)
					varMapping.freeNamedReg(finReg)
				else:
					offset = global_.scopeList.scopeList[funcName].getOffset(lhs.value)
					if offset is None:
						lhsString = "global_"+lhs.value
						self.pSet.printLoadStoreGlobal(False, finReg, lhsString) #he sure
					else:
						self.pSet.printLoadStore(False, finReg, regStringMapper(-1), offset)
					varMapping.freeNamedReg(finReg)
			else:
				tempReg = lhs.children[0].getTerminal(funcName)
				self.pSet.printLoadStore(False, finReg, tempReg, 0)
				varMapping.freeNamedReg(finReg)
				varMapping.freeNamedReg(tempReg)
		elif self.label == Label.RETURN:
			if len(self.children) > 0:
				finReg = self.resolve_reg(self.children[0], funcName)
				self.pSet.printMove(regStringMapper(-4), finReg)
				varMapping.freeNamedReg(finReg)
		elif self.label == Label.GOTO_NUM:
			self.pSet.printJump(self.value)
		elif self.label == Label.IF:
			j_label = self.children[1].value
			t_reg = self.children[0].getTerminal(funcName)
			self.pSet.printBNE(t_reg, "$0", j_label)
			varMapping.freeNamedReg(t_reg)
		elif self.label == Label.ELSE:
			self.children[0].printNode(funcName)
	def resolve_reg(self, rhs, funcName):
		finReg = -1
		if rhs.label == Label.FUNCALL: # he says
			num_args = len(rhs.children) #ASSUMPTION SIZE ARG IS ALWAYS 4
			p_offset = 0 ##TUKKA
			for x in range(num_args):
				x_name = rhs.children[x].getTerminal(funcName)
				self.pSet.printLoadStore(False, x_name, regStringMapper(-1), p_offset)
				varMapping.freeNamedReg(x_name)
				p_offset+=4
			self.pSet.printOps("sub", regStringMapper(-1), regStringMapper(-1), num_args*4)
			self.pSet.printJal(rhs.value)
			self.pSet.printOps("add", regStringMapper(-1), regStringMapper(-1), num_args*4)
			tempReg = varMapping.getMinUsable()
			self.pSet.printMove(regStringMapper(tempReg), regStringMapper(-4))
			# varMapping.freeNamedReg()
			finReg = regStringMapper(tempReg)
		elif len(rhs.children)==2:
			lhs_1 = rhs.children[0]
			rhs_1 = rhs.children[1]
			lhs_name = lhs_1.getTerminal(funcName) 
			rhs_name = rhs_1.getTerminal(funcName)
			operator_ = instMapper(rhs.label)
			tempReg = -1
			if len(operator_)==1 and rhs.label!=Label.GT:
				tempReg = varMapping.getMinUsable()
				self.pSet.printOps(operator_[0], regStringMapper(tempReg), lhs_name, rhs_name)
				varMapping.freeNamedReg(lhs_name)
				varMapping.freeNamedReg(rhs_name)
			elif rhs.label==Label.GT:
				tempReg = varMapping.getMinUsable()
				self.pSet.printOps(operator_[0], regStringMapper(tempReg), rhs_name, lhs_name)
				varMapping.freeNamedReg(lhs_name)
				varMapping.freeNamedReg(rhs_name)
			else :
				tempReg = varMapping.getMinUsable()
				if rhs.label==Label.LE:
					self.pSet.printOps(operator_[0], regStringMapper(tempReg), rhs_name, lhs_name)
				else :
					assert(rhs.label==Label.GE)
					self.pSet.printOps(operator_[0], regStringMapper(tempReg), lhs_name, rhs_name)
				varMapping.freeNamedReg(lhs_name)
				varMapping.freeNamedReg(rhs_name)
				tempReg2 = varMapping.getMinUsable()
				self.pSet.printNot(regStringMapper(tempReg2), regStringMapper(tempReg))
				varMapping.freeNamedReg(tempReg)
				tempReg = tempReg2
			finReg = regStringMapper(tempReg)
		elif len(rhs.children) == 1:
			tempReg = -1
			if rhs.label == Label.UMINUS:
				lhs_name = rhs.children[0].getTerminal()
				tempReg = varMapping.getMinUsable()
				tempReg2 = self.getImm(-1)
				self.pSet.printOps("mul", regStringMapper(tempReg), lhs_name, tempReg2)
				varMapping.freeNamedReg(lhs_name)
				varMapping.freeNamedReg(tempReg2)				
			elif rhs.label == Label.NOT:
				lhs_name = rhs.children[0].getTerminal()
				tempReg = varMapping.getMinUsable()
				self.pSet.printNot(regStringMapper(tempReg), lhs_name)
				varMapping.freeNamedReg(lhs_name)
			else:
				return rhs.getTerminal(funcName) 
			finReg = regStringMapper(tempReg)
		else :
			return rhs.getTerminal(funcName)
		return finReg

class InstructionSet:
	def __init__(self):
		self.emp = True
	def printLoadStore(self, isLoad, firstReg, secondReg, offset):
		s = "\tsw"
		if isLoad:
			s = "\tlw"
		print(s, firstReg+ "," ,str(offset)+"("+secondReg+")")
	def printLoadImm(self, reg, c):
		print("\tli", reg+",", c)
	def printOps(self, opLabel, firstReg, secondReg, thirdReg):
		s = opLabel
		s = "\t" + s
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
		print("\tmove", reg1+",", reg2)
	def printLoadStoreGlobal(self, isLoad, reg, glob):
		s = "\tsw"
		if isLoad:
			s = "\tlw"
		print(s, reg+",", glob)
	def printLoadAddress(self, reg, glob):
		print("\tla", reg+",", glob)



def printMips(index, funcName):
	currNode = global_.cfg[index]
	if currNode.label == Label.FUNCTION:
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
		return j
	else :
		currNode.printNode(funcName)
		return index + 1
