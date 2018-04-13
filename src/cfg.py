varMapping = VarMaps()

def regStringMapper(x):
	if x>=0
		return "$s"+str(x)
	else :
		if x==-1:
			return "$sp"
		elif x==-2
			return "$fp"
		elif x==-3
			return "$ra"

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
	def printPrologue(self):
		self.pSet.printLoadStore(False, regStringMapper(-3), regStringMapper(-1), 0)
		self.pSet.printLoadStore(False, regStringMapper(-2), regStringMapper(-1), -4)
		self.pSet.printOps("sub", regStringMapper(-2), regStringMapper(-1), 8)
		localSpace =  scopeList.scopeList[self.value].getLocalSpace()
		self.pSet.printOps("sub", regStringMapper(-1), regStringMapper(-1), localSpace)
	def printEpilogue(self):
		localSpace =  scopeList.scopeList[self.value].getLocalSpace()
		self.pSet.printOps("add", regStringMapper(-1), regStringMapper(-1), localSpace)
		self.pSet.printLoadStore(True, regStringMapper(-2), regStringMapper(-1), -4)
		self.pSet.printLoadStore(True, regStringMapper(-3), regStringMapper(-1), 0)
		self.pSet.printJumpReg(regStringMapper(-3))
	def getVar(self, funcName):
		offset = scopeList.scopeList[funcName].getOffset(self.value)
		if offset is None:
			return True
		regNum = varMapping.addMapping(self.value)
		self.pSet.printLoadStore(True, regStringMapper(regNum), regStringMapper(-1), offset)
		return False
	def getTerminal(self, funcName):
		name = ""
		isGlobal = False
		if self.label != Label.TEMP:
			isGlobal = self.getVar(funcName)
		if isGlobal:
			name = "global_"+self.value
		else:
			if self.label in [Label.FLOATCONST, Label.INTCONST]:
				return self.getImm(self.value)
			else:
				name = regStringMapper(varMapping.maps[self.value])
		return (name, isGlobal)
	def getImm(self, x):
		reg = varMapping.getMinUsable()
		self.pSet.printLoadImm(reg, x)
		return regStringMapper(reg), False
	def printNode(self, funcName):
		p = "\t"
		if self.label == Label.BLOCK_NUM:
			print("label", self.value, ":")
		elif self.label == Label.FUNCTION:
			print(self.value, ":")
		elif self.label == Label.ASGN:
			rhs = self.children[1]
			finReg = -1
			if rhs.label == Label.FUNCALL:
				num_args = len(rhs.children) #ASSUMPTION SIZE ARG IS ALWAYS 4
				p_offset = -4*(num_args-1)
				for x in num_args:
					x_name, isGlobal = x.getTerminal()
					self.pSet.printLoadStore(False, x_name, regStringMapper(-1), offset)
					if not isGlobal:
						varMapping.freeNamedReg(x_name)
					offset+=4
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
				finReg = tempReg
			elif len(rhs.children) == 1:
				lhs_1 = rhs.children[0]
				tempReg = -1
				if rhs.label != Label.ADDR
					lhs_name, isGlobal = lhs_1.getTerminal(funcName)
				if rhs.label == Label.DEREF:
					tempReg = varMapping.getMinUsable()
					self.pSet.printLoadStore(True, regStringMapper(tempReg), lhs_name, 0)
					if not isGlobal:
						varMapping.freeNamedReg(lhs_name)
				elif rhs.label == Label.ADDR:
					tempReg = varMapping.getMinUsable()
					assert(lhs_1.label == Label.VAR)
					offset = scopeList.scopeList[funcName].getOffset(lhs_1.value)
					tempReg2 = self.getImm(offset)[0]
					self.pSet.printOps("add", regStringMapper(tempReg), regStringMapper(-1), tempReg2)
					varMapping.freeNamedReg(tempReg2)
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
				finReg = tempReg
			else :
				rhs_name, isGlobal = rhs.getTerminal(funcName)
				finReg = rhs_name

				

		# elif self.label == Label.IF:
		# 	condReg = tempToReg(self.children[0].value)
			

class InstructionSet:
	def __init__(self):
		self.emp = True
	def printLoadStore(isLoad, firstReg, secondReg, offset):
		s = "\tsw"
		if isLoad:
			s = "\tlw"
		print(s, firstReg+ "," ,str(offset)+"("+secondReg+")")
	def printLoadImm(self, reg, c):
		print("\tli", reg+",", c)
	def printOps(opLabel, firstReg, secondReg, thirdReg):
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
		print("\tmove", reg1, reg2)


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
		self.freeTempReg(int(filter(str.isdigit, str1)))
def printMips(index):
	currNode = cfg[index]
	currNode.printNode()
	if currNode.label == Label.FUNCTION:
		funcEnd = funcIndices[currNode.value][1]
		j = index + 1
		#Add Prologue
		while j <= funcEnd:
			printMips(j)
			j+=1
		#ADD Epilogue
		return j
	else :
		return index + 1
