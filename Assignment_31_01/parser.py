#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc


numStatic= 0
numPointer = 0
numAssign =0
correct  = 1
tokens = ('DTYPE', 'EQUALS', 'LPAREN', 'RPAREN', 'LCPAREN', 'RCPAREN', 
			'RETTYPE', 'FUNCNAME', 'SEMICOL', 'COMMA', 'AMP', 'WORD', 'REF', 'NUMBER')

t_ignore = " \t"
t_ignore_comment = "//[^\n]*\n"

t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOL = r';'
t_COMMA = r','
t_AMP = r'&'
t_REF = r'\*'
t_LCPAREN = r'{'
t_RCPAREN = r'}'
t_WORD = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_newline(t):
    r'\n+'
    t.lexer.lineno =  t.lexer.lineno + len(t.value)

def incraseNumAssign(k):
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
# precedence = (
# 	('left', 'PLUS', 'MINUS'),
#         ('left', 'TIMES', 'DIVIDE'),
#         ('right', 'EXP'),
#         ('right', 'UMINUS'),
# )
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
	# print(split)
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
	p[0] =assigner(p)

def p_expression_id(p) :
	"""
	ID : WORD
	   | REF WORD
	"""
	p[0] =assigner(p)
def p_expression_assign(p) :
	"""
	ASSIGN : PRIMWORD COMMA ASSIGN 
		   | PRIMWORD
		   | PRIMREF
		   | PRIMREF COMMA ASSIGN
	"""

def p_prim_word(p) :
	"""
	PRIMWORD : WORD EQUALS AMP WORD
			| WORD EQUALS WORD
			| WORD EQUALS PRIMWORD
	"""
	incraseNumAssign(1)
def p_prim_ref(p):
	"""
	PRIMREF : REF ID EQUALS NUMBER
			| REF ID EQUALS REF ID
			| REF ID EQUALS WORD
			| REF ID EQUALS PRIMREF
			| REF ID EQUALS PRIMWORD
	"""
	incraseNumAssign(1)
def p_error(p):
	global correct 
	correct = 0
	if p:
		print("syntax error at {0} on {1}{2}".format(p.value, "line number ", p.lineno))
	else:
		print("syntax error at EOF")

def process(data):
	# lexer = lex.lex()
	# lexer.input(data)
	# for tok in lexer:
	# 	print(tok)
	lex.lex()
	yacc.yacc()
	yacc.parse(data)

data = ""
if __name__ == "__main__":
	for line in sys.stdin:
		data = data + line
	process(data)
	if(correct==1):
		print(numStatic)
		print(numPointer)
		print(numAssign)