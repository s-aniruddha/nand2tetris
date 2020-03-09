import sys
import os
import re

KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
IDENTIFIER = "IDENTIFIER"
INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"

fullTokenList = [
    (r'[ \n\t]+', None),
    (r'//[^\n]*', None),
    (r'/\*[\s\S]*?\*/', None),
    (r'class', KEYWORD), 
    (r'constructor' , KEYWORD),
    (r'function' , KEYWORD),
    (r'method', KEYWORD),
    (r'field', KEYWORD),
    (r'static', KEYWORD),
    (r'var', KEYWORD),
    (r'int', KEYWORD),
    (r'char', KEYWORD),
    (r'boolean', KEYWORD),
    (r'void', KEYWORD),
    (r'true', KEYWORD),
    (r'false', KEYWORD),
    (r'null', KEYWORD),
    (r'this', KEYWORD),
    (r'let', KEYWORD),
    (r'do', KEYWORD),
    (r'if', KEYWORD),
    (r'else', KEYWORD),
    (r'while', KEYWORD),
    (r'return', KEYWORD),
    (r'\{', SYMBOL),
    (r'\}', SYMBOL),
    (r'\(', SYMBOL),
    (r'\)', SYMBOL),
    (r'\[', SYMBOL),
    (r'\]', SYMBOL), 
    (r'\.', SYMBOL),
    (r',', SYMBOL),
    (r';', SYMBOL),
    (r'\+', SYMBOL),
    (r'\*', SYMBOL),
    (r'-', SYMBOL),
    (r'/', SYMBOL),
    (r'&', SYMBOL),
    (r'\|', SYMBOL),
    (r'<', SYMBOL),
    (r'>', SYMBOL),
    (r'=', SYMBOL),
    (r'~',SYMBOL),
    (r'[0-9]+',INT_CONST),
    (r'"[^"\n]*"', STRING_CONST),
    (r'[A-Za-z_][A-Za-z0-9_]*', IDENTIFIER) 
]



def lex(characters, token_exprs):
    pos = 0
    tokens = []
    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    tokens.append((text, tag))
                break
        if not match:
            raise Exception('Illegal character: %s at %d\n' % (characters[pos], pos))
        else:
            pos = match.end(0)
    return tokens


class JackTokenizer :
    def __init__(self, inputFile):
        with open(inputFile, "r") as file:
            self.characters = file.read()

        self.tokenList = lex(self.characters, fullTokenList)
        self.numberOfTokens = len(self.tokenList)
        self._tokenType = None
        self._tokenString = None
        self.currentToken = -1
        

    def hasMoreTokens (self):
        return self.currentToken < self.numberOfTokens - 1
    
    def advance(self):
        if self.hasMoreTokens():
            self.currentToken += 1
            self._tokenString = self.tokenList[self.currentToken][0]
            self._tokenType = self.tokenList[self.currentToken][1]
        else:
            self._tokenString = None
            self._tokenType = None
        
    def tokenType(self):
        return self._tokenType

    def keyWord(self):
        if self.tokenType() == KEYWORD:
            return self._tokenString

    def symbol(self):
        if self.tokenType() == SYMBOL:
            return self._tokenString

    def identifier(self):
        if self.tokenType() == IDENTIFIER:
            return self._tokenString

    def intVal(self):
        if self.tokenType() == INT_CONST:
            val = int(self._tokenString)
            if val > 32767:
                raise Exception("too large int value: " + str(val))
            return val
    
    def stringVal(self):
        if self.tokenType() == STRING_CONST:
            return self.tokenString()

    def tokenString(self):
        if self.tokenType() == STRING_CONST:
            return self._tokenString[1:-1]
        else:
            return self._tokenString


class CompilationEngine:
    def __init__(self, tokenizer, fout):
        self.tokenizer = tokenizer
        self.fout = fout #output stream 
        self.op = ['+' , '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=']
        self.unaryOp =  ['-' , '~']
        self.KeywordConstant = ['true' , 'false' , 'null' , 'this']
        self.CompileClass()
        

    def expectToken(self, tokenType, tokenStr = None, adv = True):
        if adv:
            self.tokenizer.advance()
        if self.tokenizer.tokenType() != tokenType:
            raise Exception("expected " + tokenType)
        if tokenStr and tokenStr != self.tokenizer.tokenString():
            raise Exception("expected " + tokenStr)
        if self.tokenizer.tokenType() == INT_CONST:
            self.fout.write("<integerConstant> ")
            self.fout.write(str(self.tokenizer.intVal()))
            self.fout.write(" </integerConstant>\n")
        elif self.tokenizer.tokenType() == STRING_CONST:
            self.fout.write("<stringConstant> ")
            self.fout.write(self.tokenizer.tokenString())
            self.fout.write(" </stringConstant>\n")
        else:
            self.fout.write("<" + tokenType.lower() + "> ")
            self.fout.write(self.tokenizer.tokenString())
            self.fout.write(" </" +  tokenType.lower() +">\n")

    def expectNotokens(self):
        if self.tokenizer.hasMoreTokens():
            raise Exception("EOF expected, but still there are tokens")

    def compileType(self):
        self.tokenizer.advance()
        if (tokenizer.tokenType() == KEYWORD and (tokenizer.keyWord() == 'int' 
            or tokenizer.keyWord() == 'char' or tokenizer.keyWord() == 'boolean' or tokenizer.keyWord() == 'void')):
            self.expectToken(KEYWORD,adv = False)
        elif (tokenizer.tokenType() == IDENTIFIER):
            self.expectToken(IDENTIFIER,adv = False)


    def CompileClass(self):
        self.fout.write("<class>\n")
        self.expectToken(KEYWORD, "class")
        self.expectToken(IDENTIFIER)
        self.expectToken(SYMBOL, "{")
        self.tokenizer.advance()
        while self.tokenizer.tokenString() == 'field' or self.tokenizer.tokenString() == 'static' :
            self.CompileClassVarDec()
        while self.tokenizer.tokenString() == 'constructor' or self.tokenizer.tokenString() == 'function'  or self.tokenizer.tokenString() == 'method':
            self.CompileSubroutine()
        self.expectToken(SYMBOL, "}",False) 
        self.fout.write("</class>\n")  
        self.expectNotokens()
    
    def CompileClassVarDec(self):
        self.fout.write("<classVarDec>\n") 
        if self.tokenizer.tokenString() == 'field':
            self.expectToken(KEYWORD, "field", False)
        elif self.tokenizer.tokenString() == 'static':
            self.expectToken(KEYWORD, "static",False)
        self.compileType()                
        self.expectToken(IDENTIFIER)
        self.tokenizer.advance()    
        while self.tokenizer.tokenString() == ',':       
            self.expectToken(SYMBOL, ",",False)
            self.expectToken(IDENTIFIER)
            self.tokenizer.advance()   
        self.expectToken(SYMBOL, ";",False)
        self.fout.write("</classVarDec>\n")
        self.tokenizer.advance()    

    def CompileSubroutine(self):
        self.fout.write("<subroutineDec>\n")
        if self.tokenizer.tokenString() == 'constructor':
            self.expectToken(KEYWORD, "constructor", False)
        elif self.tokenizer.tokenString() == 'function':
            self.expectToken(KEYWORD, "function",False)
        elif self.tokenizer.tokenString() == 'method':
            self.expectToken(KEYWORD, "method",False)  
        self.compileType()          
        self.expectToken(IDENTIFIER)
        self.expectToken(SYMBOL, '(')
        self.tokenizer.advance()
        if self.tokenizer.tokenString() != ')':
            self.compileParameterList() 
        else:
            self.fout.write("<parameterList>\n")
            self.fout.write("</parameterList>\n")    
        self.expectToken(SYMBOL, ')', False)
        self.CompileSubroutineBody()
        self.fout.write("</subroutineDec>\n")    
        self.tokenizer.advance()

    def CompileSubroutineBody(self):
        self.fout.write("<subroutineBody>\n")
        self.expectToken(SYMBOL, '{') 
        self.tokenizer.advance()
        while(self.tokenizer.tokenString() == "var"):
            self.fout.write("<varDec>\n") 
            self.expectToken(KEYWORD,adv = False)
            self.compileType()
            self.expectToken(IDENTIFIER)
            self.tokenizer.advance()
            while self.tokenizer.tokenString() == ',':       
                self.expectToken(SYMBOL, ",",False)
                self.expectToken(IDENTIFIER)
                self.tokenizer.advance()
            self.expectToken(SYMBOL, ";",False)
            self.fout.write("</varDec>\n") 

            self.tokenizer.advance()
        self.compileStatements()
        self.expectToken(SYMBOL, '}',False)
        self.fout.write("</subroutineBody>\n")

    def compileStatements(self): 
        self.fout.write("<statements>\n")
        while (self.tokenizer.tokenString() == 'let' or 
                self.tokenizer.tokenString() == 'if' or self.tokenizer.tokenString() == 'while' or 
                self.tokenizer.tokenString() == 'do' or self.tokenizer.tokenString() == 'return'):
            if self.tokenizer.tokenString() == 'let':
                self.compileLet()
            elif self.tokenizer.tokenString() == 'if':
                self.compileIf()  
            elif self.tokenizer.tokenString() == 'while':
                self.compileWhile()
            elif self.tokenizer.tokenString() == 'do':
                self.compileDo()   
            else:
                self.compileReturn()
        self.fout.write("</statements>\n")
                  

    def compileParameterList(self):
        self.fout.write("<parameterList>\n")    
        if self.tokenizer.tokenType() == KEYWORD:
            self.expectToken(KEYWORD,adv = False)
        elif self.tokenizer.tokenType() == IDENTIFIER:
            self.expectToken(IDENTIFIER,adv = False)              
        self.expectToken(IDENTIFIER) 
        self.tokenizer.advance()    
        while self.tokenizer.tokenString() == ',':       
            self.expectToken(SYMBOL, ",",False)
            self.compileType()
            self.expectToken(IDENTIFIER)
            self.tokenizer.advance()      
        self.fout.write("</parameterList>\n")   

    def compileLet(self):
        self.fout.write("<letStatement>\n")
        self.expectToken(KEYWORD,"let",adv = False)
        self.expectToken(IDENTIFIER)
        self.tokenizer.advance()
        if(self.tokenizer.tokenString() == '['):
            self.expectToken(SYMBOL,"[",adv = False)   
            self.compileExpression()
            self.expectToken(SYMBOL,"]",adv = False)
            self.tokenizer.advance()
        self.expectToken(SYMBOL,"=",False)    
        self.compileExpression()
        self.expectToken(SYMBOL,";",adv = False)
        self.tokenizer.advance()
        self.fout.write("</letStatement>\n")

    def compileIf(self):
        self.fout.write("<ifStatement>\n")
        self.expectToken(KEYWORD,"if",adv = False)
        self.expectToken(SYMBOL,"(")
        self.compileExpression()
        self.expectToken(SYMBOL,')',False)
        self.expectToken(SYMBOL,"{")
        self.tokenizer.advance()
        self.compileStatements()
        self.expectToken(SYMBOL, '}',False)
        self.tokenizer.advance()
        if self.tokenizer.tokenString() == 'else':
            self.expectToken(KEYWORD,"else",adv = False)
            self.expectToken(SYMBOL,"{")
            self.tokenizer.advance()
            self.compileStatements()
            self.expectToken(SYMBOL, '}',False)
            self.tokenizer.advance()
        self.fout.write("</ifStatement>\n")

    def compileWhile(self):
        self.fout.write("<whileStatement>\n")
        self.expectToken(KEYWORD,"while",adv = False) 
        self.expectToken(SYMBOL,"(")
        self.compileExpression()
        self.expectToken(SYMBOL,')',False)  
        self.expectToken(SYMBOL,"{")
        self.tokenizer.advance()
        self.compileStatements()
        self.expectToken(SYMBOL, '}',False)
        self.tokenizer.advance() 
        self.fout.write("</whileStatement>\n")  

    def compileDo(self):
        self.fout.write("<doStatement>\n")
        self.expectToken(KEYWORD,"do",adv = False)    
        self.expectToken(IDENTIFIER)
        self.tokenizer.advance()
        if self.tokenizer.tokenString() == '.':
            self.expectToken(SYMBOL, '.',False)
            self.expectToken(IDENTIFIER)
            self.tokenizer.advance()
        self.expectToken(SYMBOL,"(",False)
        self.compileExpressionList()
        
        self.expectToken(SYMBOL,")",False)
        self.expectToken(SYMBOL,";")
        self.fout.write("</doStatement>\n")
        self.tokenizer.advance()

    def compileReturn(self):
        self.fout.write("<returnStatement>\n")
        self.expectToken(KEYWORD,"return",adv = False)
        self.tokenizer.advance()    
        if self.tokenizer.tokenString() != ';':
            self.compileExpression(False)
        self.expectToken(SYMBOL,';',False)
        self.tokenizer.advance()
        self.fout.write("</returnStatement>\n")    

    def compileExpressionList(self):
        self.fout.write("<expressionList>\n")
        self.tokenizer.advance()    
        if self.tokenizer.tokenString() != ')':
            self.compileExpression(False)  
            while self.tokenizer.tokenString() == ',':
                self.expectToken(SYMBOL,adv = False)
                self.compileExpression()
        self.fout.write("</expressionList>\n")    

    
    def compileExpression(self,adv = True):
        if adv:
            self.tokenizer.advance()
        self.fout.write("<expression>\n")
        self.compileTerm()
        while self.tokenizer.tokenString() in self.op:
            if self.tokenizer.tokenString() == '<':
                self.fout.write("<" + SYMBOL.lower() + ">")
                self.fout.write(" &lt; ")
                self.fout.write("</" +  SYMBOL.lower() +">\n") 
            elif self.tokenizer.tokenString() == '>':
                self.fout.write("<" + SYMBOL.lower() + ">")
                self.fout.write(" &gt; ")
                self.fout.write("</" + SYMBOL.lower() +">\n")  
            elif self.tokenizer.tokenString() == '&':
                self.fout.write("<" + SYMBOL.lower() + ">")
                self.fout.write(" &amp; ")
                self.fout.write("</" + SYMBOL.lower() +">\n")               
            else:    
                self.expectToken(SYMBOL,adv=False)
            self.tokenizer.advance()
            self.compileTerm()

        self.fout.write("</expression>\n")    
    
    def compileTerm(self):
        if self.tokenizer.tokenString() in self.unaryOp:
            self.fout.write("<term>\n")
            self.expectToken(SYMBOL,adv=False)
            self.tokenizer.advance()
            self.compileTerm()
            self.fout.write("</term>\n")
        elif self.tokenizer.tokenString() == '(':
            self.fout.write("<term>\n")
            self.expectToken(SYMBOL,adv=False)
            self.compileExpression()
            self.expectToken(SYMBOL,')',False)
            self.tokenizer.advance()
            self.fout.write("</term>\n")
        elif self.tokenizer.tokenType() == INT_CONST:
            self.fout.write("<term>\n")
            self.expectToken(INT_CONST,adv=False)
            self.tokenizer.advance()
            self.fout.write("</term>\n")
        elif self.tokenizer.tokenType() == STRING_CONST:
            self.fout.write("<term>\n")
            self.expectToken(STRING_CONST,adv=False)
            self.tokenizer.advance()
            self.fout.write("</term>\n")
        elif self.tokenizer.tokenString() in self.KeywordConstant:
            self.fout.write("<term>\n")
            self.expectToken(KEYWORD,adv=False)
            self.tokenizer.advance()
            self.fout.write("</term>\n")
        elif self.tokenizer._tokenType == IDENTIFIER:
            self.fout.write("<term>\n")
            self.expectToken(IDENTIFIER,adv=False)
            self.tokenizer.advance()
            if self.tokenizer.tokenString() == '[':
                self.expectToken(SYMBOL,adv=False)
                self.compileExpression()
                self.expectToken(SYMBOL,']',False)
                self.tokenizer.advance()
            elif self.tokenizer.tokenString() == '(':
                self.expectToken(SYMBOL,adv=False)
                self.compileExpressionList()
                self.expectToken(SYMBOL,')',False)
                self.tokenizer.advance()   
            elif self.tokenizer.tokenString() == '.':
                self.expectToken(SYMBOL, '.',False)
                self.expectToken(IDENTIFIER)
                self.tokenizer.advance()
                self.expectToken(SYMBOL,"(",False)
                self.compileExpressionList()
                self.expectToken(SYMBOL,")",False)
                self.tokenizer.advance()
            self.fout.write("</term>\n")

inputPath = os.path.abspath(sys.argv[1])

if os.path.isdir(inputPath):
    # process each input .jack file
    for infile in os.listdir(inputPath):
        if infile.endswith(".jack"):
            idx = infile.find(".jack")
            fileNameWithoutExt = infile[0:idx]
            tokenizer = JackTokenizer(inputPath + os.sep + infile)
            outPath = inputPath + os.sep + fileNameWithoutExt + ".xml"
            with open(outPath, "w") as fout:
                CompilationEngine(tokenizer, fout)
else: # input is single .jack file
    idx = inputPath.find(".jack")
    fileNameWithoutExt = inputPath[0:idx]
    tokenizer = JackTokenizer(inputPath)
    with open(fileNameWithoutExt + ".xml", "w") as fout:
        CompilationEngine(tokenizer, fout)