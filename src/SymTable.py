from enums import Label
from enums import ParseType
from enums import DataTypeEnum
from enums import Label
from enums import opMapper
from enums import typeMapper
from enums import labMapper

class VarItem:
	def __init__(self, name, dataType):
		self.name = name
		self.type = dataType

class Scope: 
	def __init__(self, name):
		self.name = name
		self.varTable = {}
		self.isDefined = False
	def addVarItem(self, varItem):
		self.varTable[varItem.name] = varItem
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
	def isSameScope(self, scope):
		return self.name == scope.name and self.name == scope.name and self.paramTypes == scope.paramTypes and self.retType == scope.retType

class ScopeList:
	def __init__(self):
		self.scopeList = {}
	def addScope(self, scope):
		if scope.name in self.scopeList:
			if self.scopeList[scope.name].isSameScope(scope):
				if self.scopeList[scope.name].isDefined or (not scope.isDefined):
					print("DEBUG_REDECLARATION")
					return False
		self.scopeList[scope.name] = scope
		return True

class DataTypes:
	def __init__(self, dataType, indirection):
		self.indirection = indirection
		self.type = dataType
		if(dataType not in DataTypeEnum):
			print("INVALID DATATYPE")
	def isSameType(dataType):
		return self.indirection == dataType.indirection and self.type == dataType.type