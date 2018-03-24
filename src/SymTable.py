from enums import Label
from enums import ParseType
from enums import DataTypeEnum
from enums import Label
from enums import opMapper
from enums import typeMapper
from enums import labMapper
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
		self.retType = retType
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


	def isSameScope(self, scope):
		return self.name == scope.name and self.name == scope.name and self.paramTypes == scope.paramTypes and self.retType == scope.retType

class ScopeList:
	def __init__(self):
		self.scopeList = OrderedDict()
	def addScope(self, scope):
		if scope.name in self.scopeList:
			if self.scopeList[scope.name].isDefined or (not scope.isDefined):
				print("DEBUG_FUNCTION REDECLARATION")
				return False
		self.scopeList[scope.name] = scope
		return True
	def printScopeList(self):
		for x in self.scopeList:
			print(x)
			self.scopeList[x].printScope()	


class DataTypes:
	def __init__(self, dataType, indirection, addressable):
		self.indirection = -1*indirection
		self.type = dataType
		self.addressable = True
		if(dataType not in DataTypeEnum):
			print("INVALID DATATYPE")
	def isSameType(self, dataType):
		return self.indirection == dataType.indirection and self.type == dataType.type
	def __repr__(self):
		s = self.type.name.lower()
		for k in range(self.indirection):
			s = s+"*"
		return '\''+ s + '\''











