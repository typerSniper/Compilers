import enum

class ParseType(enum.Enum):
	VarItem = 1
	Scope = 2
	ScopeList = 3
	Abstree = 4
	DECL = 5
class DataTypeEnum(enum.Enum):
	INT = 1
	FLOAT = 2
	VOID = 3
	BOOLEAN = 4


# //int a -> -1, direct0[x]
# //int * -> 0, -1, +ve max == indirection @everypointx
class Label(enum.Enum):
	VAR = 1
	DEREF = 2
	ADDR = 3
	UMINUS= 4
	INTCONST = 5
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
	NOT = 30
	GLOBAL = 31
	FUNCDECL = 32
	FLOAT = 33
	FUNCTION = 34
	FLOATCONST = 35
	CONST = 36
	RETURN = 37
	FUNCALL = 38
	BLOCK_NUM = 39
	TEMP = 40
	ELSE = 41
	GOTO_NUM = 42
	DEFAULT = 1000
def opMapper(x):
	return {
		'+' : Label.PLUS,
		'-' : Label.MINUS,
		'*' : Label.MUL,
		'/' : Label.DIV, 
		'<' : Label.LT,
		'<=': Label.LE, 
		'>' : Label.GT,
		'>=': Label.GE,
		'==': Label.EQ,
		'&&': Label.AND,
		'||': Label.OR,
		'!=': Label.NE,
		'!' : Label.NOT,
	}[x]

def instMapper(x):
	if x == Label.LE:
		return ['slt', 'not'] #rev
	if x == Label.GT:
		return ['slt'] #rev
	if x == Label.GE:
		return ['slt', 'not']

	return {
		Label.PLUS : ['add'],
		Label.MINUS : ['sub'],
		Label.MUL : ['mul'],
		Label.DIV : ['div'],
		Label.LT : ['slt'],
		Label.EQ : ['seq'],
		Label.AND : ['and'],
		Label.OR : ['or'],
		Label.NE : ['sne'],
		Label.NOT: ['not']
	}[x]

def sizeMapper(x): 
	return {
		DataTypeEnum.INT : 4,
		DataTypeEnum.FLOAT : 4
	}[x]


def typeMapper(x):
	return {
	'int' : DataTypeEnum.INT,
	'float' : DataTypeEnum.FLOAT,
	'void' : DataTypeEnum.VOID
	}[x]

def labMapper(x):
	return { 
	'int' : Label.INT,
	'float' : Label.FLOAT,
	}[x]