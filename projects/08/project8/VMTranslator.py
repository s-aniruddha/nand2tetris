import sys
import os

# command types
C_INVALID = -1
C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2
C_LABEL = 3
C_GOTO = 4
C_IF = 5
C_FUNCTION = 6
C_RETURN = 7
C_CALL = 8

# dictionary to map a command name to command type
commandDict =  { 
    'add'      : C_ARITHMETIC, 
    'sub'      : C_ARITHMETIC, 
    'neg'      : C_ARITHMETIC, 
    'gt'       : C_ARITHMETIC,
    'lt'       : C_ARITHMETIC,
    'eq'       : C_ARITHMETIC, 
    'and'      : C_ARITHMETIC,
    'or'       : C_ARITHMETIC,
    'not'      : C_ARITHMETIC,
    'push'     : C_PUSH,
    'pop'      : C_POP,
    'label'    : C_LABEL,
    'goto'     : C_GOTO,
    'if-goto'  : C_IF,
    'function' : C_FUNCTION,
    'return'   : C_RETURN,
    'call'     : C_CALL
}

class Parser:
    def __init__(self, inputFileName):
        # input file lines
        self.lines = []
        with open(inputFileName, "r") as inputFile:
            # read all lines but ignore empty lines and comment lines
            for line in inputFile:
                if line == "" or line == "\n":
                    continue
                if line[0:2] == '//':
                    continue   
                self.lines.append(line)
        self.currentLine = 0
        self._commandType = C_INVALID
        self._commandName = ""
        self._arg0 = ""
        self._arg1 = -1

    def hasMoreCommands(self):
        return self.currentLine < len(self.lines)

    def advance(self):
        # split the words of the current line
        words = self.lines[self.currentLine].split()
        # first word is command
        self._commandName = words[0]
        # map command name to type
        self._commandType = commandDict[self._commandName]

        # read first argument if available
        if len(words) > 1:
            self._arg0 = words[1]
        else:
            self._arg0 = None
        
        # read second argument if available
        if len(words) > 2:
            try:
                self._arg1 = int(words[2])
            except:
                self._arg1 = -1
        else:
            self._arg1 = -1

        # advance to the next line
        self.currentLine += 1

    def commandName(self):
        return self._commandName

    def commandType(self):
        return self._commandType

    def arg0(self):
        return self._arg0

    def arg1(self):
        return self._arg1

class CodeWriter:
    def __init__(self, fout):
        self.fout = fout
        self.labelCount = 0
        self.currentFunctionName = ""
        self.returnIndex = 0

    def setFileName(self, fileName):
        self.fileName = fileName

    def writeArithmetic(self, command): 
        if command == 'add':
            fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'M=D+M'+ '\n')
        elif command == 'sub':
            fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'M=M-D' + '\n')    
        elif command == 'neg':
            fout.write('@SP' + '\n' +  'A=M-1' + '\n' + 'M=-M'+'\n')                   
        elif command == 'and':
            fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'M=D&M')
        elif command == 'or':
            fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' +  '\n'+ 'M=D|M')              
        elif command == 'not':
            fout.write('@SP' + '\n' +  'A=M-1' + '\n' + 'M=!M'+'\n') 
        else:
            fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'MD=M-D' + '\n' + '@TRUE' + str(self.labelCount) + '\n' + 'D;')
            if command == 'eq':
                fout.write('JEQ' + '\n')
            elif command == 'lt':
                fout.write('JLT' + '\n')
            elif command == 'gt':
                fout.write('JGT' + '\n')            
            fout.write('(FALSE' + str(self.labelCount) + ')' + '\n' + '@SP'  + '\n' + 'A=M-1' + '\n' + 'M=0' + '\n' + '@NEXT'+ str(self.labelCount) + '\n' + '0;JMP' + '\n') 
            fout.write('(TRUE' + str(self.labelCount) + ')' + '\n' + '@SP'  + '\n' + 'A=M-1' + '\n' + 'M=-1' + '\n' + '@NEXT'+ str(self.labelCount) + '\n' + '0;JMP' + '\n')
            fout.write('(NEXT' + str(self.labelCount) + ')' + '\n') 
            self.labelCount += 1
    
    def writePushPop(self, commandType, segment, index):
        indexStr = str(index)
        if (commandType == C_PUSH):
            if segment == "constant":
                fout.write('@'+ indexStr + '\n' + 'D=A' + '\n')
            elif segment == "local":
                fout.write('@' + 'LCL' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif segment == "argument":
                fout.write('@'+ 'ARG' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif segment == "this": 
                fout.write('@'+ 'THIS' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif segment == "that": 
                fout.write('@'+ 'THAT' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif segment == "static":
                fout.write('@'+ self.fileName + indexStr + '\n' + 'D=M' + '\n') 
            elif segment == "temp":
                fout.write('@'+ 'R5' + '\n' + 'D=A' + '\n'+ '@' + str(index) + '\n' +'A=D+A' + '\n' +'D=M'  +'\n')
            elif segment == "pointer":
                if index == 0:
                    fout.write('@' + 'THIS' + '\n' + 'D=M' + '\n')
                else:
                    fout.write('@' + 'THAT' + '\n' + 'D=M' + '\n')
            fout.write('@SP' + '\n' + 'A=M' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'M=M+1' + '\n') 
        elif commandType == C_POP:
            if segment == "local":
                fout.write('@' + 'LCL' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n')  
            elif segment == "argument": 
                fout.write('@'+ 'ARG' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif segment == "this": 
                fout.write('@'+ 'THIS' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif segment == "that": 
                fout.write('@'+ 'THAT' + '\n' + 'D=M' + '\n' + '@' + indexStr + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif segment == "static":
                fout.write('@'+ self.fileName + indexStr + '\n' + 'D=A' + '\n' + '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif segment == "temp":
                fout.write('@'+ 'R5' + '\n' + 'D=A' + '\n' + '@' + str(index) + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif segment == "pointer":
                if index == 0:
                    fout.write('@' + 'THIS' + '\n' + 'D=A' + '\n' + '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
                else:
                    fout.write('@' + 'THAT' + '\n' + 'D=A' + '\n' + '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 


    def close(self):
        pass

    def writeInit(self):
        fout.write('@256\nD=A\n@SP\nM=D\n')
        self.writeCall("Sys.init", 0)


    def writeLabel(self, label):
        fout.write('(' + self.currentFunctionName + '$' + label + ')\n')
    
    def writeGoto(self, label):
        fout.write('@' + self.currentFunctionName + '$'  + label + '\n' + '0;JMP\n')
    
    def writeIf(self, label):
        fout.write(
            "@SP\n" +
            "AM=M-1\n" +
            "D=M\n" +
            "A=A-1\n" +
            "@" + self.currentFunctionName + '$' + label + '\n' + 'D;JNE\n')

    def writeCall(self, functionName, numArgs):
        # push return address
        fout.write('@' + "returnaddress" + str(self.returnIndex) + '\nD=A\n')
        fout.write('@SP\nA=M\nM=D\n@SP\nM=M+1\n')

        # save LCL, ARG, THIS, THAT
        fout.write('@' + "LCL" + '\nD=M\n')
        fout.write('@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        fout.write('@' + "ARG" + '\nD=M\n')
        fout.write('@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        fout.write('@' + "THIS" + '\nD=M\n')
        fout.write('@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        fout.write('@' + "THAT" + '\nD=M\n')
        fout.write('@SP\nA=M\nM=D\n@SP\nM=M+1\n') 
    
        fout.write('@' + "SP" + '\nD=M\n')
        fout.write('@5' + '\nD=D-A\n')  
        fout.write('@' + str(numArgs) + "\nD=D-A\n")           
        fout.write('@' + "ARG" + '\nM=D\n')
        fout.write('@' + "SP" + '\nD=M\n')
        fout.write('@' + "LCL" + '\nM=D\n')
        fout.write('@' + functionName + '\n0;JMP\n') 
        fout.write('(' + "returnaddress" + str(self.returnIndex) + ')\n')
        self.returnIndex += 1 

    def writeReturn(self):
        fout.write('@' + "LCL" + '\nD=M\n') 
        fout.write('@' + "R11" + '\nM=D\n')

        fout.write('@5\nA=D-A\nD=M\n') 
        fout.write('@' + "R12" + '\nM=D\n')   

        fout.write('@ARG\nD=M\n@0\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n') 

        fout.write('@ARG\nD=M\n@SP\nM=D+1\n')

        fout.write("@R11\nD=M-1\nAM=D\nD=M\n")
        fout.write('@' + "THAT" + '\nM=D\n') 

        fout.write('@R11\nD=M-1\nAM=D\nD=M\n') 
        fout.write('@' + "THIS" + '\nM=D\n')   

        fout.write('@R11\nD=M-1\nAM=D\nD=M\n') 
        fout.write('@' + "ARG" + '\nM=D\n')

        fout.write('@R11\nD=M-1\nAM=D\nD=M\n') 
        fout.write('@' + "LCL" + '\nM=D\n') 
            
        fout.write('@R12\nA=M\n0;JMP\n')                         

    def writeFunction(self, functionName, numLocals):
        self.currentFunctionName = functionName
        fout.write('('+ functionName + ')\n')    
        for i in range(numLocals):
            self.writePushPop(C_PUSH, "constant", 0)

def translate(parser, codeWriter):
    while parser.hasMoreCommands():
        parser.advance()
        commandType = parser.commandType()
        if commandType == C_ARITHMETIC:
            codeWriter.writeArithmetic(parser.commandName())
        elif commandType == C_POP or commandType == C_PUSH:
            codeWriter.writePushPop(commandType, parser.arg0(), parser.arg1())
        elif commandType == C_LABEL:
            codeWriter.writeLabel(parser.arg0())
        elif commandType == C_GOTO:
            codeWriter.writeGoto(parser.arg0())
        elif commandType == C_IF:
            codeWriter.writeIf(parser.arg0())
        elif commandType == C_FUNCTION:
            codeWriter.writeFunction(parser.arg0(), parser.arg1())
        elif commandType == C_CALL:
            codeWriter.writeCall(parser.arg0(), parser.arg1())   
        elif commandType == C_RETURN:
            codeWriter.writeReturn()

# main

inputPath = os.path.abspath(sys.argv[1])

if os.path.isdir(inputPath):
    outPath = inputPath + os.sep + os.path.basename(inputPath) + ".asm"

    with open (outPath, "w") as fout:
        codeWriter = CodeWriter(fout)
        codeWriter.writeInit()
        # process each input .vm file
        for infile in os.listdir(inputPath):
            if infile.endswith(".vm"):
                idx = infile.find(".vm")
                fileNameWithoutExt = infile[0:idx]
                parser = Parser(inputPath + os.sep + infile)
                codeWriter.setFileName(fileNameWithoutExt)
                translate(parser, codeWriter)

else: # input is single .vm file
    idx = inputPath.find(".vm")
    fileNameWithoutExt = inputPath[0:idx]
    outPath = fileNameWithoutExt + ".asm"
    parser = Parser(inputPath)
    with open(outPath, "w") as fout:
        codeWriter = CodeWriter(fout)
        codeWriter.setFileName(fileNameWithoutExt)
        translate(parser, codeWriter)


