#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc
from Abstree import Abstree



trees = []
numStatic= 0
numPointer = 0
numAssign =0
correct  = 1
tokens = ('DTYPE', 'EQUALS', 'LPAREN', 'RPAREN', 'LCPAREN', 'RCPAREN', 
			'RETTYPE', 'FUNCNAME', 'SEMICOL', 'COMMA', 'AMP', 'WORD', 'REF', 'NUMBER',
			'PLUS', 'MINUS', 'DIV')

t_ignore = " \t"
t_ignore_comment = "//[^\n]*\n"

t_EQUALS = r'='
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

def opMapper(x):
	return {
		'+' : "PLUS",
		'-' : "MINUS",
		'*' : "MUL",
		'/' : "DIV"
	}[x]

def t_newline(t):
    r'\n+'
    t.lexer.lineno =  t.lexer.lineno + len(t.value)

def increaseNumAssign(k):
	global numAssign
	numAssign = numAssign + k

def assigner(p):
	i =2 
	p[0] = p[1]
	while i<len(p):
		p[0] = p[0] + p[i]
		i=i+1	
	return p[0]
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
def p_expression_body(p) :
	"""
	BODY : DECL SEMICOL BODY 
			| ASSIGN SEMICOL BODY
			| 
	"""
def p_expression_decl(p):
	"""
	DECL : DTYPE DECLIST
	"""
	p[0] =assigner(p)
	split = p[2].split(',')
	for k in split:
		if k.count('*')>0:
			global numPointer
			numPointer = numPointer + 1
		else :
			global numStatic
			numStatic = numStatic + 1
def p_expression_declist(p):
	"""
	DECLIST : ID COMMA DECLIST 
			| ID
	"""
	p[0] = assigner(p)

def p_expression_id(p) :
	"""
	ID : WORD
	   | REF ID
	"""
	p[0] = assigner(p)

def p_expression_assignId(p) :
	"""
	aID : WORD
		| AMP aID
		| REF aID
	"""
	if(len(p)==2):
		p[0] = Abstree([], "VAR", True, p[1])
	elif(len(p)==3):
		if(p[1]=="*"):
			p[0]= Abstree([p[2]], "DEREF", False, -1)
		elif(p[1]=="&"):
			p[0]= Abstree([p[2]], "ADDR", False, -1)

def p_expression_lhspointer(p):
	"""
	LHS_POINT : REF aID
	"""
	p[0]= Abstree([p[2]], "DEREF", False, -1)
def p_expression_assign(p) :
	"""
	ASSIGN : WORD EQUALS Wrhs
		| LHS_POINT EQUALS Wrhs
	"""
	if(isinstance(p[1], str)):
		p[1] = Abstree([], "VAR", True, p[1])
	p[0]= Abstree([p[1], p[3]], "ASSGN", False, -1)
	global trees
	trees.append((p[0], p.lineno))
	increaseNumAssign(1)

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
	"""
	p[0] = p[1]
def p_expression_Wrhs3(p):
	"""
		Wrhs : MINUS Wrhs %prec UMINUS
	"""
	p[0]= Abstree([p[2]], "UMINUS", False, -1)
def p_expression_Natom(p) :
	"""
	Natom : NUMBER
	"""
	p[0] = Abstree([], "CONST", True, p[1])

def p_error(p):
	global correct 
	correct = 0
	if p:
		print("syntax error at '{0}' on {1}'{2}'".format(p.value, "line number ", p.lineno))
	else:
		print("syntax error at EOF")

def process(data):
	lex.lex()
	yacc.yacc()
	yacc.parse(data)

data = ""
if __name__ == "__main__":
	f = open(sys.argv[1], 'r')
	data = f.read()
	process(data)
	done = 1
	for x in trees:
		if(not x[0].valid_tree()):
			done = 0
			x[0].print_error(x[1])
			break
	if done:
		for x in trees:
			x[0].print_tree(0)
			print()
	# if correct==1 :
	# 	print(numStatic)
	# 	print(numPointer)
	# 	print(numAssign)