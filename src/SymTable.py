from enums import *
from collections import OrderedDict


class VarItem:
	def __init__(self, name, dataType):
		self.name = name
		self.type = dataType

class Scope: 
	def __init__(self, name):
		self.name = name
		self.varTable = OrderedDict()
		self.isDefined = False
	def setParent(self, parent):
		self.parent = parent
	def addVarItem(self, varItem):
		if varItem.name in self.varTable:
			print("DEBUG_VARIABLE REDECLARATION")
			return False
		self.varTable[varItem.name] = varItem
		return True
	def defineFunc(self, paramList, retType):
		self.paramIds = []
		self.paramTypes = []
		for k in paramList :
			self.varTable[k[0]] = VarItem(k[0], k[1])
			self.paramIds.append(k[0])
			self.paramTypes.append(k[1])
		retType.addressable = False
		self.retType = retType
		self.retType.setUsable()
	def defined(self):
		self.isDefined = True
	def printScope(self):
		for c in self.varTable:
			print(c, end = ' ')
			print(self.varTable[c].type)
	def getType(self, x):
		current = self
		while x not in current.varTable:
			if(current.parent==None):
				return None
			current = current.parent
		return current.varTable[x].type
	def print_without(self, s):
		print(s, end='')
	def isSameScope(self, scope):
		return self.name == scope.name  and self.paramTypes == scope.paramTypes and self.retType == scope.retType
	def printParams(self):	
		for k in range(len(self.paramIds)):
			self.print_without(self.paramTypes[k])
			self.print_without(" "+self.paramIds[k])
			if(k!=len(self.paramIds)-1):
				self.print_without(", ")
	def printVarTable(self):
		s = ''
		for i in range(3):
			s = s+"\t"
		s+="|"
		for x in self.varTable:
			var = self.varTable[x]
			print(var.name, s, end=' ')
			if self.name == "GLOBAL":
				print("global 	", s, end=' ')
			else:
				print("procedure", self.name, s, end=' ')
			print(var.type.type.name.lower(), s, end=' ')
			for i in range(-1*var.type.indirection):
				print("*", end='')
			print()


class ScopeList:
	def __init__(self):
		self.scopeList = OrderedDict()
	def  addScope(self, scope):
		if scope.name in self.scopeList:
			prevScope = self.scopeList[scope.name]
			if(not scope.isSameScope(self.scopeList[scope.name])):
				print("DEBUG_FUNCTION_OVERLOADED")
				return False
			if not scope.isDefined:
				if prevScope.isDefined:
					print("FUNCTION_ALREADY_DEFINED", scope.name)
				else:
					print("FUNCTION_ALREADY_DECLARED", scope.name)
				return False
			elif prevScope.isDefined:
				print("FUNCTION_BEING_REDFINED", scope.name)
				return False
		else :
			if scope.isDefined:
				print("DEFINITION_WITHOUT_DECLARATION", scope.name)
				return False
		if scope.name!="GLOBAL" and scope.retType.type == DataTypeEnum.VOID and scope.retType.indirection!=0:
			print("DEBUG_VOID*_NOT_ALLOWED")
			return False
		if  scope.name!="GLOBAL" and (len(scope.paramIds)>len(set(scope.paramIds))):
			print("DEBUG_TWO_PARAMS_WITH_SAME_ID_IN_", scope.name)
			return False;
		self.scopeList[scope.name] = scope
		return True
	def printScopeList(self):
		print("Procedure Table :-")
		s = ""
		for i in range(3):
			s = s+"\t"
		s+="|"
		l = ""
		for i in range(90):
			l = l + "-"
		print(l)
		print("Name", s,  "Return Type", s, "Parameter List")
		for x in self.scopeList.keys():
			if(x=="GLOBAL"):
				continue
			scope = self.scopeList[x]
			print(scope.name, s, end='  ')
			print(scope.retType, end='')
			print(s, end='  ')
			scope.printParams()
			print()
		print(l)

	def printVarTable(self):
		print("Variable Table :-")
		l = ""
		for i in range(90):
			l = l + "-"
		print(l)
		s = ""
		for i in range(3):
			s = s+"\t"
		s+="|"
		print("Name", s, "Scope", s, "Base Type", s,   "Derived Type")
		print(l)
		for x in self.scopeList.keys():
			self.scopeList[x].printVarTable()
		print(l)
		print(l)




class DataTypes:
	def __init__(self, dataType, indirection, addressable):
		self.indirection = -1*indirection
		self.type = dataType
		self.addressable = True
		self.usable = False
		if self.indirection!=0:
			self.usable = True
		if(dataType not in DataTypeEnum):
			print("INVALID DATATYPE")
	def isSameType(self, dataType):
		return self.indirection == dataType.indirection and self.type == dataType.type
	def setUsable(self):
		self.usable = True
	def getCopy(self):
		newType = DataTypes(self.type, self.indirection, self.addressable)
		newType.addressable = self.addressable
		newType.usable = self.usable
		return newType
	def __repr__(self):
		s = self.type.name.lower()
		for k in range(abs(self.indirection)):
			s = s+"*"
		return s
	def __eq__(self, other):
		return self.isSameType(other)











