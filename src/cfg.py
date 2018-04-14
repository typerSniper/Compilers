import global_
from enums import *

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
		self.freeTempReg(int(''.join(filter(str.isdigit, x))))

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
		print(self.label, end = ' ')
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
			return True
		regNum = varMapping.addMapping(self.value)
		self.pSet.printLoadStore(True, regStringMapper(regNum), regStringMapper(-1), offset)
		return False
	def getTerminal(self, funcName):
		name = ""
		isGlobal = False
		if self.label != Label.TEMP and self.label != Label.FLOATCONST and self.label != Label.INTCONST:
			isGlobal = self.getVar(funcName)
		if isGlobal:
			print(self.label)
			name = "global_"+self.value
		else:
			if self.label in [Label.FLOATCONST, Label.INTCONST]:
				return self.getImm(self.value)
			else:
				name = regStringMapper(varMapping.maps[self.value])
		return (name, isGlobal)
	def getImm(self, x):
		reg = varMapping.getMinUsable()
		self.pSet.printLoadImm(regStringMapper(reg), x)
		return regStringMapper(reg), False
	def printNode(self, funcName):
		p = "\t"
		if self.label == Label.BLOCK_NUM:
			print()
			print("label"+str(self.value), ":")
		elif self.label == Label.FUNCTION:
			print(self.value, ":")
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
						lhsString = "global_"+self.value
						print("Stored in Global") #TODO
					else:
						self.pSet.printLoadStore(False, finReg, regStringMapper(-1), offset)
					varMapping.freeNamedReg(finReg)
					# lhs_name, isGlobal = rhs.getTerminal(funcName)
					# self.pSet.printMove(rhs_name, finReg)
					# varMapping.freeNamedReg(finReg)
			else:
				curr = lhs
				while len(curr.children) > 0:
					curr = curr.children[0]
				lhs = curr
				if lhs.label == Label.VAR:
					name, isGlobal = lhs.getTerminal(funcName)
					if isGlobal:
						self.pSet.printLoadStore(False, finReg, "global_"+name, 0)
					else:
						self.pSet.printLoadStore(False, finReg, name, 0)
				else:
					print("\tIDK") #TODO
				# print("\tLINE WRITTEN") 
				
		elif self.label == Label.RETURN:
			if len(self.children) > 0:
				finReg = self.resolve_reg(self.children[0], funcName)
				self.pSet.printMove(regStringMapper(-4), finReg)
				varMapping.freeNamedReg(finReg)
		elif self.label == Label.GOTO_NUM:
			print("\tj", "label"+str(self.value))
		# elif self.label == Label.IF:
		# 	condReg = tempToReg(self.children[0].value)
	def resolve_reg(self, rhs, funcName):
		finReg = -1
		if rhs.label == Label.FUNCALL:
			num_args = len(rhs.children) #ASSUMPTION SIZE ARG IS ALWAYS 4
			p_offset = -4*(num_args-1)
			for x in range(num_args):
				x_name, isGlobal = rhs.children[x].getTerminal(funcName)
				self.pSet.printLoadStore(False, x_name, regStringMapper(-1), p_offset)
				if not isGlobal:
					varMapping.freeNamedReg(x_name)
				p_offset+=4
			liReg = self.getImm(num_args*4)[0]
			self.pSet.printOps("sub", regStringMapper(-1), regStringMapper(-1), liReg)
			varMapping.freeNamedReg(liReg)
			self.pSet.printJal(rhs.value)
			liReg = self.getImm(num_args*4)[0]
			self.pSet.printOps("add", regStringMapper(-1), regStringMapper(-1), liReg)
			varMapping.freeNamedReg(liReg)
			tempReg = varMapping.getMinUsable()
		elif len(rhs.children)==2:
			lhs_1 = rhs.children[0]
			rhs_1 = rhs.children[1]
			lhs_name, isGlobalL = lhs_1.getTerminal(funcName) 
			rhs_name, isGlobalR = rhs_1.getTerminal(funcName)
			operator_ = instMapper(rhs.label)
			tempReg = -1
			if len(operator_)==1 and rhs.label!=Label.GT:
				tempReg = varMapping.getMinUsable()
				self.pSet.printOps(operator_[0], regStringMapper(tempReg), lhs_name, rhs_name)
				if not isGlobalL:
					varMapping.freeNamedReg(lhs_name)
				if not isGlobalR:
					varMapping.freeNamedReg(rhs_name)
			elif rhs.label==Label.GT:
				tempReg = varMapping.getMinUsable()
				self.pSet.printOps(operator_[0], regStringMapper(tempReg), rhs_name, lhs_name)
				if not isGlobalL:
					varMapping.freeNamedReg(lhs_name)
				if not isGlobalR:
					varMapping.freeNamedReg(rhs_name)
			else :
				if rhs.label==Label.LE:
					tempReg = varMapping.getMinUsable()
					self.pSet.printOps(operator_[0], regStringMapper(tempReg), rhs_name, lhs_name)
					if not isGlobalL:
						varMapping.freeNamedReg(lhs_name)
					if not isGlobalR:
						varMapping.freeNamedReg(rhs_name)
					tempReg2 = varMapping.getMinUsable()
					self.pSet.printNot(regStringMapper(tempReg2), regStringMapper(tempReg))
					varMapping.freeTempReg(tempReg)
					tempReg = tempReg2
			finReg = regStringMapper(tempReg)
		elif len(rhs.children) == 1:
			lhs_1 = rhs.children[0]
			tempReg = -1
			if rhs.label != Label.ADDR:
				lhs_name, isGlobal = lhs_1.getTerminal(funcName)
			if rhs.label == Label.DEREF:
				tempReg = varMapping.getMinUsable()
				self.pSet.printLoadStore(True, regStringMapper(tempReg), lhs_name, 0)
				if not isGlobal:
					varMapping.freeNamedReg(lhs_name)
			elif rhs.label == Label.ADDR:
				# print("HERE")
				tempReg = varMapping.getMinUsable()
				assert(lhs_1.label == Label.VAR)
				offset = global_.scopeList.scopeList[funcName].getOffset(lhs_1.value)
				# print(global_.scopeList.scopeList[funcName].scope_width)
				# tempReg2 = self.getImm(offset)[0]
				self.pSet.printOps("addi", regStringMapper(tempReg), regStringMapper(-1), offset)
				# varMapping.freeNamedReg(tempReg2)
			elif rhs.label == Label.UMINUS:
				tempReg = varMapping.getMinUsable()
				tempReg2 = self.getImm(-1)[0]
				self.pSet.printOps("mul", regStringMapper(tempReg), lhs_name, tempReg2)
				if not isGlobal:
					varMapping.freeNamedReg(lhs_name)
				varMapping.freeNamedReg(tempReg2)				
			elif rhs.label == Label.NOT:
				tempReg = varMapping.getMinUsable()
				self.pSet.printNot(regStringMapper(tempReg), lhs_name)
				if not isGlobal:
					varMapping.freeNamedReg(lhs_name)
			finReg = regStringMapper(tempReg)
		else :
			# print("here")
			rhs_name, isGlobal = rhs.getTerminal(funcName)
			finReg = rhs_name
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
	def printJumpReg(self, regName):
		print("\tjr", regName)
	def printNot(self, reg1, reg2):
		print("\tnot", reg1+",", reg2)
	def printJal(self, funcName):
		print("\tjal", funcName)
	def printMove(self, reg1, reg2):
		print("\tmove", reg1+",", reg2)

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
