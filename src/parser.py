#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc
from enums import *
from Abstree import *
from SymTable import *


tree = []
numStatic= 0
numPointer = 0
numAssign =0
correct  = 1
tokens = ('EQUALS', 'LPAREN', 'RPAREN', 'LCPAREN', 'RCPAREN', 
		  'SEMICOL', 'COMMA', 'AMP', 'WORD', 'REF', 'NUMBER',
			'PLUS', 'MINUS', 'DIV', 'IF', 'WHILE', 'ELSE', 'LESSTHAN', 'GREATERTHAN', 'OR', 'NOT'
			, 'INT', 'FLOAT', 'VOID', 'RETURN')

t_ignore = " \t"
t_ignore_comment = "//[^\n]*\n"

t_EQUALS = r'='
t_LESSTHAN = r'<'
t_GREATERTHAN = r'>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOL = r';'
t_COMMA = r','
t_AMP = r'&'
t_OR = r'\|'
t_REF = r'\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_DIV = r'/'
t_LCPAREN = r'{'
t_RCPAREN = r'}'
t_NOT = r'\!'

def t_WORD(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	if t.value in reserved:
		t.type = reserved[t.value]
	return t

prog = []

reserved = {
	'if' : 'IF',
  	'else' : 'ELSE',
	'while' : 'WHILE',
	'int' : 'INT',
	'float' : 'FLOAT',
	'void' : 'VOID',
	'return' : 'RETURN'
}


def t_newline(t):
    r'\n+'
    t.lexer.lineno =  t.lexer.lineno + len(t.value)

def increaseNumAssign(k):
	global numAssign
	numAssign = numAssign + k

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_error(t): 
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# Parsing rules
precedence = (
	('left', 'PLUS', 'MINUS'),
        ('left', 'REF', 'DIV'),
        ('right', 'UMINUS')
)

def p_expression_progS(p):
	'progS : prog'
	p[0] = p[1]
	p[0].print_tree(0)

def p_expression_prog(p):
	"""
	prog : var_decl prog
		 | proc_decl prog
		 | procs prog
		 |
	"""
	if(len(p)==1):
		p[0] = Abstree([], Label.GLOBAL, False, -1)
	elif(len(p)==3):
		p[2].prepend(p[1])
		p[0] = p[2]


def p_expression_var(p):
	"""
	var_decl : DECL SEMICOL  
	"""
	p[0] = p[1]

def p_expression_procDecl(p):
	"""
	proc_decl : INT ID LPAREN PARAM RPAREN SEMICOL 
			| FLOAT ID LPAREN PARAM RPAREN SEMICOL 
			| VOID ID LPAREN PARAM RPAREN SEMICOL 
	"""
	tup = p[2].get_name_ind()
	scope = Scope(tup[0])
	scope.defineFunc(p[4], DataTypes(typeMapper(p[1]), tup[1]))
	p[0] = Abstree([], Label.FUNCDECL, False, scope)

def p_expression_procs(p):
	"""
	procs : INT ID LPAREN PARAM RPAREN LCPAREN BODY RCPAREN  
		   | FLOAT ID LPAREN PARAM RPAREN LCPAREN BODY RCPAREN
		   | VOID ID LPAREN PARAM RPAREN LCPAREN BODY RCPAREN   
	"""
	tup = p[2].get_name_ind()
	scope = Scope(tup[0])
	scope.defineFunc(p[4], DataTypes(typeMapper(p[1]), tup[1]))
	p[0] = Abstree([p[7]], Label.FUNCDECL, False, scope)	

def p_expression_param(p):
	"""
	PARAM : PTYPE ID EPARAM
		  | 
	"""
	if(len(p)==1):
		p[0] = []
	else :
		tup = p[2].get_name_ind()
		item = DataTypes(typeMapper(p[1]), tup[1])
		p[0] = [(tup[0] , item)] + p[3]
def p_expression_eparam(p):
	"""
	EPARAM : COMMA PTYPE ID EPARAM
		   | 
	"""
	if(len(p)==1):
		p[0] = []
	else :
		tup = p[3].get_name_ind()
		item = DataTypes(typeMapper(p[2]), tup[1])
		p[0] = [(tup[0] , item)] + p[4]

def p_expression_ptype(p):
	"""
	PTYPE : INT 
		| FLOAT
	"""
	p[0] = p[1]

# def p_expression_rettype(p):
# 	"""
# 	RETTYPE : INT
# 			| FLOAT
# 			| VOID
# 			| RETTYPE REF
# 	"""



# def p_expression_prog(p):
#         'expression : RETTYPE FUNCNAME LPAREN RPAREN LCPAREN BODY RCPAREN'

#         global tree
#         tree = p[6]

def p_expression_body(p) :
	"""
	BODY : DECL SEMICOL BODY 
			| ASSIGN SEMICOL BODY
			| COMPLETEIF BODY
			| WHILExpr BODY
			| 
	"""
	if(len(p)==1):
		p[0] = Abstree([], Label.BLOCK, False, -1)
	elif(len(p)==4) :
		p[3].prepend(p[1])
		p[0] = p[3]
	elif(len(p)==3):
		p[2].prepend(p[1])
		p[0] = p[2]

def p_expression_decl(p):
	"""
	DECL : INT DECLIST
		 | FLOAT DECLIST
	"""
	p[1] = Abstree([], labMapper(p[1]), True, -1)
	p[0] = Abstree([p[1]], Label.DECL, False, -1)
	for x in reversed(p[2]):
		p[0].add_child(x)

def p_expression_declist(p):
	"""
	DECLIST : ID COMMA DECLIST 
			| ID
	"""
	if len(p)==2:
		p[0] = [p[1]]
	else:
		p[3].append(p[1])
		p[0] = p[3]
def p_expression_id(p) :
	"""
	ID : WORD
	   | REF ID
	"""
	if len(p)==2:
		p[0] = Abstree([], Label.VAR, True, p[1])
	else:
		p[0] = Abstree([p[2]], Label.DEREF, False, -1)
def p_expression_assignId(p) :
	"""
	aID : WORD
		| AMP aID
		| REF aID
	"""
	if(len(p)==2):
		p[0] = Abstree([], Label.VAR, True, p[1])
	elif(len(p)==3):
		if(p[1]=="*"):
			p[0]= Abstree([p[2]], Label.DEREF, False, -1)
		elif(p[1]=="&"):
			p[0]= Abstree([p[2]], Label.ADDR, False, -1)

def p_expression_lhspointer(p):
	"""
	LHS_POINT : REF aID
	"""
	p[0]= Abstree([p[2]], Label.DEREF, False, -1)
def p_expression_assign(p) :
	"""
	ASSIGN : WORD EQUALS Wrhs
		| LHS_POINT EQUALS Wrhs
	"""
	if(isinstance(p[1], str)):
		p[1] = Abstree([], Label.VAR, True, p[1])
	p[0]= Abstree([p[1], p[3]], Label.ASGN, False, -1)

def p_expression_Wrhs1(p):
	"""
		Wrhs : Wrhs PLUS Wrhs
			 | Wrhs MINUS Wrhs
			 | Wrhs REF Wrhs
			 | Wrhs DIV Wrhs
	"""
	p[0]= Abstree([p[1], p[3]], opMapper(p[2]), False, p[2])
def p_expression_Wrhs2(p):
	"""
		Wrhs : aID
			 | Natom
			 | LPAREN Wrhs RPAREN
	"""
	if len(p) == 4:
		p[0] = p[2]
	else:
		p[0] = p[1]
def p_expression_Wrhs3(p):
	"""
		Wrhs : MINUS Wrhs %prec UMINUS
	"""
	p[0]= Abstree([p[2]], Label.UMINUS, False, -1)
def p_expression_Natom(p) :
	"""
	Natom : NUMBER
	"""
	p[0] = Abstree([], Label.CONST, True, p[1])

def p_expression_ifBlock(p) :
	"""
	IFBLOCK : IFBLOCK ASSIGN SEMICOL 
			| IFBLOCK  COMPLETEIF
			| IFBLOCK WHILExpr
			|
	"""
	if(len(p)!=1):
		p[1].add_child(p[2])
		p[0]=p[1]
	else:
		p[0] = Abstree([], Label.BLOCK, False, -1)

def p_expression_whileBlock(p) :
	"""
	WHILEBLOCK : WHILEBLOCK ASSIGN SEMICOL 
			| WHILEBLOCK COMPLETEIF  
			| WHILEBLOCK WHILExpr
			| 

	"""
	if(len(p)==1):
		p[0] = Abstree([], Label.BLOCK, False, -1)
	else :
		p[1].add_child(p[2])
		p[0] = p[1]
def p_expression_if(p):
	"""
	IFExpr : IF LPAREN CondExpr RPAREN ASSIGN SEMICOL
		   | IF LPAREN CondExpr RPAREN LCPAREN IFBLOCK RCPAREN
		   | IFExpr ELSE IF LPAREN CondExpr RPAREN LCPAREN IFBLOCK RCPAREN 
		   | IFExpr ELSE IF LPAREN CondExpr RPAREN ASSIGN SEMICOL 
	"""
	if(len(p)==7):

		p[0] = Abstree([p[3], Abstree([p[5]], Label.BLOCK, False, -1)], Label.IF, False, -1)
	elif(len(p) == 8):
		p[0] = Abstree([p[3], p[6]], Label.IF, False, -1)
	elif len(p) == 9:
		temp = Abstree([p[5], Abstree([p[7]], Label.BLOCK, False, -1)], Label.IF, False, -1)
		curr = p[1]
		while len(curr.children) != 2:
			curr = curr.children[2]
		curr.add_child(temp)
		p[0] = p[1]
	elif len(p) == 10:
		temp = Abstree([p[5], p[8]], Label.IF, False, -1)
		curr = p[1]
		while len(curr.children) != 2:
			curr = curr.children[2]
		curr.add_child(temp)
		p[0] = p[1]
def p_expression_else(p):
	"""
	COMPLETEIF : IFExpr ELSE LCPAREN IFBLOCK RCPAREN
			   | IFExpr ELSE ASSIGN SEMICOL
			   | IFExpr
	"""
	if(len(p)==6):
		curr = p[1]
		while len(curr.children) != 2:
			curr = curr.children[2]
		curr.add_child(p[4])
	elif len(p) == 5:
		curr = p[1]
		while len(curr.children) != 2:
			curr = curr.children[2]
		curr.add_child(Abstree([p[3]], Label.BLOCK, False, -1))
	p[0] = p[1]
def p_expression_while(p):
	"""
	WHILExpr : WHILE LPAREN CondExpr RPAREN ASSIGN SEMICOL 
			| WHILE LPAREN CondExpr RPAREN LCPAREN WHILEBLOCK RCPAREN
	"""
	if(len(p)==7):
		p[0]  = Abstree([p[3], Abstree([p[5]], Label.BLOCK, False, -1)], Label.WHILE, False, -1)
	else:
		p[0] = Abstree([p[3], p[6]], Label.WHILE, False, -1)

def p_expression_condExpr(p):
	"""
	CondExpr : Cond
		| CondExpr AMP AMP Cond
		| CondExpr AMP AMP LPAREN Cond RPAREN
		| CondExpr OR OR Cond 
		| CondExpr OR OR LPAREN Cond RPAREN
		| NOT LPAREN CondExpr RPAREN
		| LPAREN CondExpr RPAREN
	"""
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 4:
		p[0] = p[2]
	elif len(p) == 5:
		if str(p[1]) == "!":
			p[0] = Abstree([p[3]], Label.NOT, False, str(p[1]))
		else:
			p[0] = Abstree([p[1], p[4]], opMapper(p[2]+p[3]), False, str(p[2]+p[3]))
	elif len(p) == 7:
		p[0] = Abstree([p[1], p[5]], opMapper(p[2]+p[3]), False, str(p[2]+p[3]))
def p_expression_cond(p):
	"""
	Cond : Wrhs Compare Wrhs
		| NOT Cond
	"""
	if len(p) == 3:
		p[0] = Abstree([p[2]], Label.NOT, False, "!")
	else:
		p[0] = Abstree([p[1], p[3]], p[2][0], False, p[2][1])

def p_expression_compare(p):
	"""
	Compare : LESSTHAN
			  | GREATERTHAN
			  | LESSTHAN EQUALS
			  | GREATERTHAN EQUALS
			  | EQUALS EQUALS
			  | NOT EQUALS
	"""
	if(len(p)==2):
		p[0] = (opMapper(p[1]), p[1])
	elif(len(p)==3):
		p[0] = (opMapper(str(p[1]+p[2])), str(p[1]+p[2]))

def p_error(p):
	global correct, tree
	correct = 0
	if p:
		print("Syntax error at '{0}' on {1}'{2}'".format(p.value, "line number ", p.lineno))
	else:
		print("Syntax error at EOF")

def process(data):
	lex.lex()
	yacc.yacc()
	yacc.parse(data)

data = ""
if __name__ == "__main__":
	k = sys.argv[1]
	f = open(k, 'r')
	outFile1 = (k.split('/'))[-1] + ".ast"
	outFile2 = (k.split('/'))[-1] + ".cfg"
	data = f.read()
	process(data)
	# done = 1
	# if correct:
	# 	if not tree.valid_tree([], None, None):
	# 		done = 0
	# 	if done :
	# 		sys.stdout = open(outFile1, 'w')
	# 		tree.print_tree(0)
	# 		print()
	# 		sys.stdout = open(outFile2, 'w')
	# 		print()
	# 		tree.add_child(Abstree([], Label.END, True, -1))
	# 		tree.assign_blocks(0)
	# 		tree.assign_goto_num(0)
	# 		tree.print_cfg(-1)