#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc
from Abstree import Abstree
from Abstree import Label

trees = []
numStatic= 0
numPointer = 0
numAssign =0
correct  = 1
tokens = ('DTYPE', 'EQUALS', 'LPAREN', 'RPAREN', 'LCPAREN', 'RCPAREN', 
			'RETTYPE', 'FUNCNAME', 'SEMICOL', 'COMMA', 'AMP', 'WORD', 'REF', 'NUMBER',
			'PLUS', 'MINUS', 'DIV', 'IF', 'WHILE', 'ELSE', 'LESSTHAN', 'GREATERTHAN')

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
t_REF = r'\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_DIV = r'/'
t_LCPAREN = r'{'
t_RCPAREN = r'}'
t_WORD = r'[a-zA-Z_][a-zA-Z0-9_]*'

prog = []

def t_IF(t):
  	r'if'
  	return t

def t_ELSE(t):
  	r'else'
  	return t

def t_WHILE(t):
  	r'while'
  	return t

def opMapper(x):
	return {
		'+' : Label.PLUS,
		'-' : Label.MINUS,
		'*' : Label.MUL,
		'/' : Label.DIV, 
		'<' : Label.LESSTHAN,
		'<=': Label.LESSTHANEQ, 
		'>' : Label.GREATERTHAN,
		'>=': Label.GREATERTHANEQ,
		'==': Label.EQ
	}[x]

def t_newline(t):
    r'\n+'
    t.lexer.lineno =  t.lexer.lineno + len(t.value)

def increaseNumAssign(k):
	global numAssign
	numAssign = numAssign + k
def t_DTYPE(t):
	r'int'
	return t

def t_FUNCNAME(t) :
	r'main'
	return t
def t_RETTYPE(t):
	r'void' 
	return t
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
def p_expression_prog(p):
        'expression : RETTYPE FUNCNAME LPAREN RPAREN LCPAREN BODY RCPAREN'
        p[6].print_tree(0)
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
	DECL : DTYPE DECLIST
	"""
	p[1] = Abstree([], Label.INT, True, -1)
	p[0] = Abstree([p[1]], Label.DECL, False, -1)
	for x in reversed(p[2]):
		p[0].add_child(x)
def p_expression_declist(p):
	"""
	DECLIST : ID COMMA DECLIST 
			| ID
	"""
	if len(p)==2:
		p[0] = [Abstree([p[1]], Label.DVAR, False, -1)]
	else:
		p[3].append(Abstree([p[1]], Label.DVAR, False, -1))
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
	p[0]= Abstree([p[1], p[3]], Label.ASSGN, False, -1)
	# global trees
	# trees.append((p[0], p.lineno(2)))
	# increaseNumAssign(1)

def p_expression_Wrhs1(p):
	"""
		Wrhs : Wrhs PLUS Wrhs
			 | Wrhs MINUS Wrhs
			 | Wrhs REF Wrhs
			 | Wrhs DIV Wrhs
	"""
	p[0]= Abstree([p[1], p[3]], opMapper(p[2]), False, -1)
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
	IFBLOCK :  ASSIGN SEMICOL 
			| LCPAREN ASSIGN SEMICOL BODY RCPAREN
			| LCPAREN DECL SEMICOL BODY RCPAREN
			| LCPAREN  COMPLETEIF BODY RCPAREN
			| LCPAREN WHILExpr BODY RCPAREN
	"""
	if(len(p)==3):
		p[0] = Abstree([p[1]], Label.BLOCK, False, -1)
	else:
		p[4].prepend(p[2])
		p[0] = p[4]
def p_expression_if(p):
	"""
	IFExpr : IF LPAREN Cond RPAREN IFBLOCK
		   | IFExpr ELSE IF LPAREN Cond RPAREN IFBLOCK
	"""
	if(len(p)==6):
		temp = Abstree([p[3], p[5]], Label.IF, False, -1)
		p[0] = Abstree([temp], Label.IFSTMT, False, -1)
	else :
		p[1].add_child(Abstree([p[5], p[7]], Label.ELSE_IF, False, -1))
		p[0] = p[1]
def p_expression_else(p):
	"""
	COMPLETEIF : IFExpr ELSE IFBLOCK
			   | IFExpr
	"""
	if(len(p)==4):
		p[1].add_child(Abstree([p[3]], Label.ELSE, False, -1))
	p[0] = p[1]
def p_expression_while(p):
	"""
	WHILExpr : WHILE LPAREN Cond RPAREN IFBLOCK
	"""
	p[0] = Abstree([p[3], p[5]], Label.WHILE, False, -1)
def p_expression_cond(p):
	"""
	Cond : Wrhs Compare Wrhs
	"""
	p[0] = Abstree([p[1], p[2],p[3]], Label.COND, False, -1)

def p_expression_compare(p):
	"""
	Compare : LESSTHAN
			  | GREATERTHAN
			  | LESSTHAN EQUALS
			  | GREATERTHAN EQUALS
			  | EQUALS EQUALS
	"""
	if(len(p)==2):
		p[0] = Abstree([], opMapper(p[1]), True, -1)
	elif(len(p)==3):
		p[0] = Abstree([], opMapper(str(p[1]+p[2])), True, -1)

def p_error(p):
	global correct, trees 
	correct = 0
	for x in trees:
		if(not x[0].valid_tree()):
			done = 0
			x[0].print_error(x[1])
			trees=[]
			return
	trees=[]
	if p:
		print("Syntax error at '{0}' on {1}'{2}'".format(p.value, "line number ", p.lineno))
	else:
		print("Syntax error at EOF")

def process(data):
	lex.lex()
	# lexer.input(data)
	# for tok in lexer :
	# 	print(tok)
	yacc.yacc()
	yacc.parse(data)

data = ""
if __name__ == "__main__":
	k = sys.argv[1]
	f = open(k, 'r')
	print(k)
	# outFile = "Parser_ast_"+ (k.split('/'))[-1]+".txt"
	data = f.read()
	process(data)
	# done = 1
	# for x in trees:
	# 	if(not x[0].valid_tree()):
	# 		done = 0
	# 		x[0].print_error(x[1])
	# 		break
	# sys.stdout = open(outFile, 'w')
	# if done and correct:
	# 	for x in trees:
	# 		x[0].print_tree(0)
	# 		print()