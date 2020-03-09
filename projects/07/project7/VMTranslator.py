 
def codewriter(words,labelcount, fout):
        fout.write("//")
        for i in words:
              fout.write(i + ' ')
        fout.write('\n')      #writes appropriate comment statements
        if words[0] == "push":
            location = words[1]
            offset = words[2]
            if location == "constant":
                fout.write('@'+ offset + '\n' + 'D=A' + '\n')
            elif location == "local":
                fout.write('@' + 'LCL' + '\n' + 'D=M' + '\n' + '@' + offset + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif location == "argument":
                fout.write('@'+ 'ARG' + '\n' + 'D=M' + '\n' + '@' + offset + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif location == "this": 
                fout.write('@'+ 'THIS' + '\n' + 'D=M' + '\n' + '@' + offset + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif location == "that": 
                fout.write('@'+ 'THAT' + '\n' + 'D=M' + '\n' + '@' + offset + '\n' + 'A=D+A' + '\n' + 'D=M' + '\n')  
            elif location == "static":
                fout.write('@'+'foo.' + offset + '\n' + 'D=M' + '\n') 
            elif location == "temp":
                fout.write('@'+ 'R5' + '\n' + 'D=M' + '\n'+ '@' + str(int(offset) + 5) + '\n' +'A=D+A' + '\n' +'D=M'  +'\n')
            elif location == "pointer":
                if offset == '0':
                    fout.write('@' + 'THIS' + '\n' + 'D=M' + '\n')
                else:
                    fout.write('@' + 'THAT' + '\n' + 'D=M' + '\n')
            fout.write('@SP' + '\n' + 'A=M' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'M=M+1' + '\n') 

        elif words[0] == "pop":
            location1 = words[1]
            offset1 = words[2]
            if location1 == "local":
                fout.write('@' + 'LCL' + '\n' + 'D=M' + '\n' + '@' + offset1 + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n')  
            elif location1 == "argument": 
                fout.write('@'+ 'ARG' + '\n' + 'D=M' + '\n' + '@' + offset1 + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif location1 == "this": 
                fout.write('@'+ 'THIS' + '\n' + 'D=M' + '\n' + '@' + offset1 + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif location1 == "that": 
                fout.write('@'+ 'THAT' + '\n' + 'D=M' + '\n' + '@' + offset1 + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif location1 == "static":
                fout.write('@'+'foo.' + offset1 + '\n' + 'D=A' + '\n' + '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif location1 == "temp":
                fout.write('@'+ 'R5' + '\n' + 'D=M' + '\n' + '@' + str(int(offset1) + 5) + '\n' + 'D=D+A' +'\n'+ '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
            elif location1 == "pointer":
                if offset1 == '0':
                    fout.write('@' + 'THIS' + '\n' + 'D=A' + '\n' + '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 
                else:
                    fout.write('@' + 'THAT' + '\n' + 'D=A' + '\n' + '@R13' + '\n' + 'M=D' + '\n' + '@SP' + '\n' + 'AM=M-1' + '\n' + 'D=M' + '\n' + '@R13' '\n' + 'A=M' + '\n' + 'M=D' + '\n') 

        else:
            operation = words[0]
            if operation == 'add':
                 fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'M=D+M'+ '\n')
            elif operation == 'sub':
                 fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'M=M-D' + '\n')    
            elif operation == 'neg':
                 fout.write('@SP' + '\n' +  'A=M-1' + '\n' + 'M=-M'+'\n')                   
            elif operation == 'and':
                 fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'M=D&M')
            elif operation == 'or':
                 fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' +  '\n'+ 'M=D|M')              
            elif operation == 'not':
                 fout.write('@SP' + '\n' +  'A=M-1' + '\n' + 'M=!M'+'\n') 
            else:
                 fout.write('@SP' + '\n' +  'AM=M-1' + '\n' + 'D=M' + '\n' + 'A=A-1' + '\n' + 'MD=M-D' + '\n' + '@TRUE' + str(labelcount) + '\n' + 'D;') 
                 if operation == 'eq':
                   fout.write('JEQ' + '\n')
                 elif operation == 'lt':
                   fout.write('JLT' + '\n')
                 elif operation == 'gt':
                   fout.write('JGT' + '\n')            
                 fout.write('(FALSE' + str(labelcount) + ')' + '\n' + '@SP'  + '\n' + 'A=M-1' + '\n' + 'M=0' + '\n' + '@NEXT'+ str(labelcount) + '\n' + '0;JMP' + '\n') 
                 fout.write('(TRUE' + str(labelcount) + ')' + '\n' + '@SP'  + '\n' + 'A=M-1' + '\n' + 'M=-1' + '\n' + '@NEXT'+ str(labelcount) + '\n' + '0;JMP' + '\n')
                 fout.write('(NEXT' + str(labelcount) + ')' + '\n') 
            labelcount = labelcount + 1
     
        return labelcount


def VM1(infile, outfile):
    lines = []
    labelcount = 0
    with open (infile,"r") as fin:
        for line in fin:
            if line == "" or line == "\n":
                continue
            if line[0:2] == '//': #handle comments and empty lines
                continue   
            lines.append(line) 

    with open (outfile,"w") as fout:
        for i in lines:
            words = i.split() #list of words
            labelcount = codewriter(words, labelcount,fout)
 


import sys
# pass input filename as command line argument
infile = sys.argv[1]
idx = infile.find(".vm");
outfile = infile[0:idx] + ".asm"
VM1(infile, outfile)