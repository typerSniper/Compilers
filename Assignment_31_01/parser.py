#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc


tokens = ('DTYPE', 'EQUALS', 'LPAREN', 'RPAREN', 'LCPAREN', 'RCPAREN', 
			'RETTYPE', 'FUNCNAME', 'SEMICOL', 'COMMA', 'AMP', 'WORD', 'REF', 'NUMBER')

s =0

t_ignore = " \t\n"
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
        try:
        	print("base identified!")
        except LookupError:
            print("base pain '%s'" % p[1])
            p[0] = 0
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
def p_expression_declist(p):
	"""
	DECLIST : ID COMMA DECLIST 
			| ID
	"""

def p_expression_id(p) :
	"""
	ID : WORD
	   | REF WORD
	"""

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
def p_prim_ref(p):
	"""
	PRIMREF : REF ID EQUALS NUMBER
			| REF ID EQUALS REF ID
			| REF ID EQUALS WORD
			| REF ID EQUALS PRIMREF
			| REF ID EQUALS PRIMWORD
	"""
def p_error(p):
	if p:
		print("syntax error at {0}".format(p.value))
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

# data = []
data = ""
if __name__ == "__main__":
	for line in sys.stdin: 
		data = data + line
	# print(data)
	process(data)
	# print(data)