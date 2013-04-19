#!/usr/bin/env python

import pyeda

# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
#
# Class-based example contributed to PLY by David McNab
# -----------------------------------------------------------------------------

import sys
sys.path.insert(0,"../..")

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
import os

class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()
    variables = list()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = { }
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        #print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run(self):
        while 1:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s: continue
            yacc.parse(s)

    
class Calc(Parser):

    tokens = (
        'NAME','CONST',
        'OR','NEG','AND','XOR','EQUALS',
        'LPAREN','RPAREN',
        )

    # Tokens

    t_OR      = r'\+'
    t_NEG   = r'-'
    t_AND   = r'\*'
    t_XOR   = r'\^'
    t_CONST   = r'1|0'
    t_EQUALS  = r'='
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

  

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left','OR'),
        ('left','AND','XOR'),      
        ('right','UMINUS'),
        ('left' , 'LPAREN', 'RPAREN')
        )

#    def p_statement_assign(self, p):
#        'statement : NAME EQUALS expression'
#        self.names[p[1]] = p[3]

    def p_statement_expr(self, p):
        'statement : expression'
        f = p[1]
        print(f)
        f = f.to_cnf()
        print(f)

    def p_expression_and(self, p):
        """
        expression : expression AND expression
        """        
        
        p[0] = pyeda.And(p[1]*p[3]) 
        # Could be 
        # p[0] = p[1]*p[3] # pyeda And operator here !

    def p_expression_or(self, p):
        """
        expression : expression OR expression
        """        
        p[0] = pyeda.Or(p[1]*p[3]) 
        # p[0] = p[1] + p[3]  # pyeda Or  operator here !

    def p_expression_xor(self, p):
        """
        expression : expression XOR expression
        """        
        p[0] = pyeda.Xor(p[1],p[3])


    def p_expression_uminus(self, p):
        'expression : NEG expression %prec UMINUS'
        p[0] = -p[2]

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_name(self, p):
        'expression : NAME'
        
        # p[0] = pyeda.var(p[1],namespace='testing')
        p[0] = pyeda.var(p[1])

#    def p_expression_number(self, p):
#        'expression : NUMBER'
#        p[0] = p[1]
#
#    def p_expression_name(self, p):
#        'expression : NAME'
#        try:
#            p[0] = self.names[p[1]]
#        except LookupError:
#            print("Undefined name '%s'" % p[1])
#            p[0] = 0

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    calc = Calc()
    calc.run()


