import sys
import os
import re
import collections

KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
IDENTIFIER = "IDENTIFIER"
INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"
CONSTRUCTOR = "constructor"
FUNCTION = "function"
METHOD = "method"
VOID = 'void'
TRUE = 'true'
FALSE = 'false'
NULL = 'null'    
THIS = 'this'
STATIC = "static"
FIELD = "field"
ARG = "argument"
VAR = "var"
LOCAL = "local"
CONST = "constant"
ARG = "argument"
LOCAL = "local"
STATIC = "static"
THIS = "this"
THAT = "that"
POINTER = "pointer"
TEMP = "temp"
ADD = "add"
SUB = "sub" 
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or" 
NOT = "not"

# Token patterns for Jack - except for keywords. 
# All keywords are matched as IDENTIFIERs and then keywordSet
# is searched for possible keyword match

tokenPatterns = [
    (r'[ \n\t]+', None),
    (r'//[^\n]*', None),
    (r'/\*[\s\S]*?\*/', None),
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

# the set of all keywords in Jack
keywordsSet = {
    'class',  
    'constructor',
    'function',
    'method',
    'field', 
    'static', 
    'var',
    'int', 
    'char',
    'boolean',
    'void',
    'true',
    'false',
    'null',
    'this',
    'let',
    'do',
    'if',
    'else',
    'while',
    'return',
}

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
                    # keywords are matched as IDENTIFIERs and so check it in keywordsSet
                    if (tag == IDENTIFIER) and (text in keywordsSet):
                        tokens.append((text, KEYWORD))
                    else:
                        # some non-keyword (actual) identifier
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

        self.tokenList = lex(self.characters, tokenPatterns)
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

    def goBack(self):
        self.currentToken -= 1
        self._tokenString = self.tokenList[self.currentToken][0]
        self._tokenType = self.tokenList[self.currentToken][1]

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

        elif self.tokenType() == INT_CONST:
            val = int(self._tokenString)
            if val > 32767:
                raise Exception("too large int value: " + str(val))
            return val

        else:
            return self._tokenString

Symbol = collections.namedtuple("Symbol",["name","type","kind","runningIndex"])

class SymbolTable:
    def __init__(self):
        self.staticIndex = 0
        self.fieldIndex = 0
        self.argumentIndex = 0
        self.varIndex = 0
        self.classDict = dict()
        self.subroutineDict = dict()
    
    def startSubroutine(self):
        self.subroutineDict = dict()
        self.argumentIndex = 0
        self.varIndex = 0
 
    def define(self, name, typ, kind):
        if kind == STATIC:
            identifier = Symbol(name, typ, kind, self.staticIndex)
            self.classDict[name] = identifier
            self.staticIndex += 1        
        elif kind == FIELD:
            identifier = Symbol(name, typ, kind, self.fieldIndex)
            self.classDict[name] = identifier
            self.fieldIndex += 1
        elif kind == ARG:
            identifier = Symbol(name, typ, kind, self.argumentIndex)
            self.subroutineDict[name] = identifier
            self.argumentIndex += 1
        elif kind == VAR:
            identifier = Symbol(name, typ, kind, self.varIndex)            
            self.subroutineDict[name] = identifier
            self.varIndex += 1
    
    def getSegment(self, name):
        if name in self.classDict and self.classDict[name].kind == STATIC:
            return "static"
        elif name in self.classDict and self.classDict[name].kind == FIELD:
            return "this"
        elif name in self.subroutineDict and self.subroutineDict[name].kind == ARG:
            return "argument"
        elif name in self.subroutineDict and self.subroutineDict[name].kind == VAR:
            return "local"
        else:
            return ""

    def varCount(self, kind):
        if kind == STATIC:
            return self.staticIndex 
        elif kind == FIELD:
            return self.fieldIndex 
        elif kind == ARG:
            return self.argumentIndex 
        elif kind == VAR:
            return self.varIndex 
    
    def  kindOf(self, name):
        if (name in self.subroutineDict):
            return self.subroutineDict[name].kind
        elif (name in self.classDict):
            return self.classDict[name].kind
        else:
            return None    

    def  typeOf(self, name):    
        if (name in self.subroutineDict):
            return self.subroutineDict[name].type
        elif (name in self.classDict):
            return self.classDict[name].type
        else:
            return ""

    def indexOf(self, name):
        if (name in self.subroutineDict):
            return self.subroutineDict[name].runningIndex
        elif (name in self.classDict):
            return self.classDict[name].runningIndex

class VMWriter:
    def __init__(self, fout):
        self.fout = fout
    
    def writePush(self, segment, index):
        self.fout.write("push " + segment + ' ' +str(index) + '\n')

    def writePop(self, segment, index):
        self.fout.write("pop " + segment + ' ' +str(index) + '\n')   
    
    def writeArithmetic(self, command):
        self.fout.write(command + '\n')

    def writeLabel(self, label):
        self.fout.write('label '+ label +'\n')

    def writeGoto(self, label):
        self.fout.write("goto "+ label + '\n')

    def writeIf(self, label):
        self.fout.write("if-goto "+ label + '\n')
    
    def writeCall(self, name, nArgs):
        self.fout.write("call " + name + ' ' + str(nArgs) + '\n')
    
    def writeFunction(self, name, nLocals):
        self.fout.write("function " + name + ' ' +str(nLocals) + '\n')
    
    def writeReturn(self):
        self.fout.write( "return\n" )

class CompilationEngine:
    def __init__(self, tokenizer, fout):
        self.tokenizer = tokenizer
        self.fout = fout #output stream 
        self.writer = VMWriter(self.fout)
        self.op = ['+' , '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=']
        self.unaryOp =  ['-' , '~']
        self.KeywordConstant = ['true' , 'false' , 'null' , 'this']
        self.labelIndex = 0
        self.symbolTable = SymbolTable()
        self.currentClass = ''
        self.currentSubroutine = ''
        self.compileClass()
    
    def currentFunction(self):
        if (len(self.currentClass) != 0 and len(self.currentSubroutine) !=0):
            return self.currentClass + "." + self.currentSubroutine    
        else:    
            return ""
    
    def expectToken(self, tokenType, tokenStr = None, adv = True):
        if adv:
            self.tokenizer.advance()     
        if self.tokenizer.tokenType() != tokenType:
            print(self.tokenizer.tokenString())
            raise Exception("expected " + tokenType)
        if tokenStr and tokenStr != self.tokenizer.tokenString():
            print(self.tokenizer.tokenString())
            raise Exception("expected " + tokenStr)
            
        else:
            return True
        
    def expectNotokens(self):
        if self.tokenizer.hasMoreTokens():
            raise Exception("EOF expected, but still there are tokens")

    def compileType(self):
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == KEYWORD and (self.tokenizer.keyWord() == 'int' or
                self.tokenizer.keyWord() == 'char' or self.tokenizer.keyWord() == 'boolean' or 
                self.tokenizer.keyWord() == 'void')):
            return self.tokenizer.tokenString()
        elif (self.tokenizer.tokenType() == IDENTIFIER):
            return self.tokenizer.tokenString()

    def compileClass(self):
        self.expectToken(KEYWORD, "class")
        if self.expectToken(IDENTIFIER):
            self.currentClass = self.tokenizer.identifier()
        self.expectToken(SYMBOL, "{")
        self.compileClassVarDec()
        self.compileSubroutine()
        self.tokenizer.advance()
        self.expectToken(SYMBOL, "}",False)   
        self.expectNotokens()
    
    def compileClassVarDec(self):
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == '}'):
            self.tokenizer.goBack()
            return
        if (self.tokenizer.keyWord() == CONSTRUCTOR or  \
                self.tokenizer.keyWord() == FUNCTION or \
                self.tokenizer.keyWord() == METHOD):
            self.tokenizer.goBack()
            return

        if self.tokenizer.tokenString() == 'field':
            kind = FIELD
        elif self.tokenizer.tokenString() == 'static':
            kind = STATIC
        typ = self.compileType()    
        self.tokenizer.advance()
        self.symbolTable.define(self.tokenizer.identifier(), typ, kind)
        self.tokenizer.advance()
        while (True):
            if (self.tokenizer.symbol() == ';'):
                break
            self.expectToken(SYMBOL, ",", adv = False)
            self.tokenizer.advance()
            self.symbolTable.define(self.tokenizer.identifier(),typ, kind)
            self.tokenizer.advance()
        self.compileClassVarDec() 

    def compileSubroutine(self):
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == '}'):
            self.tokenizer.goBack()
            return  
        
        subroutineKind =  self.tokenizer.keyWord()
        self.symbolTable.startSubroutine()
        if (subroutineKind == METHOD):
            self.symbolTable.define("this",self.currentClass, ARG)
        returnType = self.compileType()    
        self.tokenizer.advance()
        self.currentSubroutine = self.tokenizer.identifier()
        self.expectToken(SYMBOL, "(")
        self.compileParameterList()
        self.expectToken(SYMBOL, ")")
        self.compileSubroutineBody(subroutineKind)
        self.compileSubroutine()

    def compileParameterList(self): 
        self.tokenizer.advance() 
        if (self.tokenizer.symbol() == ')'):
            self.tokenizer.goBack()
            return 
        self.tokenizer.goBack()
        typ = self.compileType()
        self.tokenizer.advance()
        self.symbolTable.define(self.tokenizer.identifier(), typ, ARG)
        self.tokenizer.advance()
        while True:
            if (self.tokenizer.symbol() == ')'):
                self.tokenizer.goBack()
                break
            self.expectToken(SYMBOL, ",", False)
            typ = self.compileType()
            self.tokenizer.advance()
            self.symbolTable.define(self.tokenizer.identifier(), typ, ARG)
            self.tokenizer.advance()

    def compileSubroutineBody(self,subroutineKind): 
        self.expectToken(SYMBOL, '{')
        self.tokenizer.advance()
        if (self.tokenizer.tokenString() != '}'):
            self.compileVarDec() 
            self.writeFunctionDec(subroutineKind)
            self.compileStatements()       
    
    def compileVarDec(self):
        if (self.tokenizer.keyWord() != VAR):
            self.tokenizer.goBack()
            return
        typ = self.compileType()    
        self.tokenizer.advance()
        self.symbolTable.define(self.tokenizer.identifier(),typ, VAR)
        self.tokenizer.advance()
        while (True):
            if (self.tokenizer.symbol() == ';'):
                break
            self.expectToken(SYMBOL, ",", adv = False)
            self.tokenizer.advance()
            self.symbolTable.define(self.tokenizer.identifier(),typ, VAR)
            self.tokenizer.advance()
        self.tokenizer.advance()
        self.compileVarDec()
    
    def writeFunctionDec(self,subroutineKind):
        self.writer.writeFunction(self.currentFunction(), self.symbolTable.varCount(VAR))
        if (subroutineKind == METHOD):
            self.writer.writePush(ARG, 0)
            self.writer.writePop(POINTER,0)
        elif (subroutineKind == CONSTRUCTOR):
            self.writer.writePush(CONST,self.symbolTable.varCount(FIELD))
            self.writer.writeCall("Memory.alloc", 1)
            self.writer.writePop(POINTER,0)
    
    def compileStatements(self):
        self.tokenizer.advance() 
        while (self.tokenizer.tokenString() == 'let' or 
                self.tokenizer.tokenString() == 'if' or self.tokenizer.tokenString() == 'while' or 
                self.tokenizer.tokenString() == 'do' or self.tokenizer.tokenString() == 'return'):
            if self.tokenizer.tokenString() == 'let':
                self.compileLet()
                self.tokenizer.advance() 
            elif self.tokenizer.tokenString() == 'if':
                self.compileIf()  
                self.tokenizer.advance() 
            elif self.tokenizer.tokenString() == 'while':
                self.compileWhile()
                self.tokenizer.advance() 
            elif self.tokenizer.tokenString() == 'do':
                self.compileDo()   
                self.tokenizer.advance() 
            elif self.tokenizer.tokenString() == 'return':
                self.compileReturn()
                self.tokenizer.advance() 

    def compileLet(self):
        self.expectToken(KEYWORD,"let",adv = False)
        self.tokenizer.advance()
        varName = self.tokenizer.tokenString()
        self.tokenizer.advance() 
        isArray = False
        if self.tokenizer.tokenString() == '[':
            isArray = True
            self.writer.writePush(self.symbolTable.getSegment(varName), \
                self.symbolTable.indexOf(varName))
            self.compileExpression()
            self.expectToken(SYMBOL, ']')
            self.writer.writeArithmetic(ADD)
        if isArray:
            self.tokenizer.advance()
        # this is R-value expression
        self.compileExpression()
        self.expectToken(SYMBOL, ';')
        if isArray:
            self.writer.writePop(TEMP,0)
            self.writer.writePop(POINTER,1)
            self.writer.writePush(TEMP,0)
            self.writer.writePop(THAT,0)
        else:
            self.writer.writePop(self.symbolTable.getSegment(varName), \
                self.symbolTable.indexOf(varName))

    def compileDo(self):
        self.expectToken(KEYWORD,"do",adv = False)
        self.compileSubroutineCall()
        self.expectToken(SYMBOL,';')
        self.writer.writePop(TEMP,0)
    
    def compileSubroutineCall(self):
        self.expectToken(IDENTIFIER)
        name = self.tokenizer.identifier()
        nArgs = 0
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == '('):
            self.writer.writePush(POINTER,0)
            nArgs = self.compileExpressionList() + 1
            self.expectToken(SYMBOL,')')
            self.writer.writeCall(self.currentClass + '.' + name, nArgs)
        elif (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == '.'):
            objName = name
            self.expectToken(IDENTIFIER)
            name = self.tokenizer.identifier()
            typ = self.symbolTable.typeOf(objName)

            if (typ == ""):
                name = objName + "." + name
            else:
                nArgs = 1
                self.writer.writePush(self.symbolTable.getSegment(objName), \
                    self.symbolTable.indexOf(objName))
                name = self.symbolTable.typeOf(objName) + "." + name

            self.expectToken(SYMBOL,'(')
            nArgs += self.compileExpressionList()
            self.expectToken(SYMBOL,')')
            self.writer.writeCall(name,nArgs)

    def compileReturn(self):
        self.expectToken(KEYWORD, "return", adv = False)
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == ';'):
            self.writer.writePush(CONST,0)
        else: 
            self.tokenizer.goBack()    
            self.compileExpression()
            self.expectToken(SYMBOL,';')
        self.writer.writeReturn()

    def compileExpressionList(self):
        nArgs = 0
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == ')'):
            self.tokenizer.goBack()
        else: 
            nArgs = 1
            self.tokenizer.goBack()
            self.compileExpression()
            while True:
                self.tokenizer.advance()
                if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == ','):
                    self.compileExpression()
                    nArgs += 1
                else: 
                    self.tokenizer.goBack()
                    break
        return nArgs
    
    def compileExpression(self):
        self.compileTerm()
        while (True):
            self.tokenizer.advance()
            if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.tokenString() in self.op):
                opCmd = ""

                if self.tokenizer.symbol() == '+':
                    opCmd = "add"
                elif self.tokenizer.symbol() == '-':
                    opCmd = "sub"
                elif self.tokenizer.symbol() == '*':
                    opCmd = "call Math.multiply 2"
                elif self.tokenizer.symbol() =='/':
                    opCmd = "call Math.divide 2"
                elif self.tokenizer.symbol() =='<':
                    opCmd = "lt"
                elif self.tokenizer.symbol() == '>':
                    opCmd = "gt"
                elif self.tokenizer.symbol() == '=':
                    opCmd = "eq"
                elif self.tokenizer.symbol() == '&':
                    opCmd = "and"
                elif self.tokenizer.symbol() == '|':
                    opCmd = "or" 
                self.compileTerm()
                self.writer.writeArithmetic(opCmd)
            else:
                self.tokenizer.goBack()
                break

    def compileTerm(self):
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == IDENTIFIER):
            tempId = self.tokenizer.identifier()
            self.tokenizer.advance()
            if (self.tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == '['):
                #this is an array entry
                self.writer.writePush(self.symbolTable.getSegment(tempId), self.symbolTable.indexOf(tempId))
                self.compileExpression()
                self.expectToken(SYMBOL,']')
                self.writer.writeArithmetic(ADD)
                self.writer.writePop(POINTER,1)
                self.writer.writePush(THAT,0)

            elif (self.tokenizer.tokenType() == SYMBOL and (self.tokenizer.symbol() == '(' or 
                    self.tokenizer.symbol() == '.')):
                self.tokenizer.goBack();
                self.tokenizer.goBack()
                self.compileSubroutineCall()
            else: 
                self.tokenizer.goBack()
                self.writer.writePush(self.symbolTable.getSegment(tempId), \
                    self.symbolTable.indexOf(tempId))
        else:
            #integerConstant|stringConstant|keywordConstant|'(' expression ')'|unaryOp term
            if (self.tokenizer.tokenType() == INT_CONST):
                self.writer.writePush(CONST,self.tokenizer.intVal())
            elif (self.tokenizer.tokenType() == STRING_CONST):
                string = self.tokenizer.stringVal()
                self.writer.writePush(CONST, len(string))
                self.writer.writeCall("String.new",1)
                for i in range(len(string)):
                    self.writer.writePush(CONST, ord(string[i]))
                    self.writer.writeCall("String.appendChar",2)
            elif(self.tokenizer.tokenType() == KEYWORD and self.tokenizer.keyWord() == TRUE):
                self.writer.writePush(CONST,0)
                self.writer.writeArithmetic(NOT)
            elif(self.tokenizer.tokenType() == KEYWORD and self.tokenizer.keyWord() == THIS):
                self.writer.writePush(POINTER,0)
            elif(self.tokenizer.tokenType() == KEYWORD and (self.tokenizer.keyWord() == FALSE or 
                     self.tokenizer.keyWord() == NULL)):
                self.writer.writePush(CONST,0)
            elif (tokenizer.tokenType() == SYMBOL and self.tokenizer.symbol() == '('):
                self.compileExpression()
                self.expectToken(SYMBOL,')')
            elif (self.tokenizer.tokenType() == SYMBOL and (self.tokenizer.symbol() == '-' or 
                      self.tokenizer.symbol() == '~')):
                s = self.tokenizer.symbol()
                self.compileTerm()
                if (s == '-'):
                    self.writer.writeArithmetic(NEG)
                else:
                    self.writer.writeArithmetic(NOT)
                
    def newLabel(self):
        label = "LABEL_" + str(self.labelIndex)
        self.labelIndex += 1
        return label

    def compileIf(self):
        self.expectToken(KEYWORD,"if",adv = False) 
        elseLabel = self.newLabel()
        endLabel = self.newLabel()
        self.expectToken(SYMBOL,'(')
        self.compileExpression()
        self.expectToken(SYMBOL,')')
        self.writer.writeArithmetic(NOT)
        self.writer.writeIf(elseLabel)
        self.expectToken(SYMBOL,'{')
        self.compileStatements()
        self.expectToken(SYMBOL,'}', False)
        self.writer.writeGoto(endLabel)
        self.writer.writeLabel(elseLabel)
        self.tokenizer.advance()
        if (self.tokenizer.tokenType() == KEYWORD and self.tokenizer.keyWord() == "else"):
            self.expectToken(SYMBOL,'{')
            self.compileStatements()
            self.expectToken(SYMBOL,'}', False)
        else:
            self.tokenizer.goBack()
        self.writer.writeLabel(endLabel)

    def compileWhile(self):
        self.expectToken(KEYWORD,"while",adv = False) 
        continueLabel = self.newLabel()
        topLabel = self.newLabel()
        self.writer.writeLabel(topLabel)
        self.expectToken(SYMBOL,'(')
        self.compileExpression()
        self.expectToken(SYMBOL,')')
        self.writer.writeArithmetic(NOT)
        self.writer.writeIf(continueLabel)
        self.expectToken(SYMBOL,'{')
        self.compileStatements()
        self.expectToken(SYMBOL,'}',False)
        self.writer.writeGoto(topLabel)
        self.writer.writeLabel(continueLabel)

inputPath = os.path.abspath(sys.argv[1])

if os.path.isdir(inputPath):
    # process each input .jack file
    for infile in os.listdir(inputPath):
        if infile.endswith(".jack"):
            idx = infile.find(".jack")
            fileNameWithoutExt = infile[0:idx]
            tokenizer = JackTokenizer(inputPath + os.sep + infile)
            outPath = inputPath + os.sep + fileNameWithoutExt + ".vm"
            with open(outPath, "w") as fout:
                CompilationEngine(tokenizer, fout)
else: # input is single .jack file
    idx = inputPath.find(".jack")
    fileNameWithoutExt = inputPath[0:idx]
    tokenizer = JackTokenizer(inputPath)
    with open(fileNameWithoutExt + ".vm", "w") as fout:
        CompilationEngine(tokenizer, fout)
