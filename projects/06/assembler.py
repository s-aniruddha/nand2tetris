


def stripspaces(s):
    res = ''
    for i in s:
        if not i.isspace():
            res += i
    return res

def isnumber(s):
    try:
        int(s)
        return True
    except:
        return False

def assembler(infile, outfile):
    symboltable = {
    'R0' : '0',
    'R1' : '1',
    'R2' : '2',
    'R3' : '3',
    'R4' : '4',
    'R5' : '5',
    'R6' : '6',
    'R7' : '7',
    'R8' : '8',
    'R9' : '9',
    'R10' : '10',
    'R11' : '11',
    'R12' : '12',
    'R13' : '13',
    'R14' : '14',
    'R15' : '15',
    'SCREEN' :  '16384',
    'KBD' :  '24576',
    'SP' : '0',
    'LCL' : '1',
    'ARG' : '2',
    'THIS' : '3',
    'THAT' : '4',
    'LOOP' : '4',
    'STOP' : '18',
    'END' : '22',
    'i' : '16',
    'sum' : '17'
    }
    
    with open (infile,"r") as fin:
            linenumber = -1
            for line in fin: #first iteration to find all the labels
                line1 = stripspaces(line)
                if line1 == "":
                    continue
                if line1[0:2] == '//':
                    continue    
                label1 = ''
                
                if line1[0] == '(':
                    for i in line1:
                        if i != "(" and i != ")":
                            label1 += i 
                    symboltable[label1] = str(linenumber + 1) 
                      
                else:
                    linenumber += 1   
    
    with open (infile,"r") as fin:       
            count = 16 
            for line in fin:
                line1 = stripspaces(line)
                if line1 == "":
                    continue
                if line1[0:2] == '//':
                    continue    
                if line1[0] == '@':
                    sym = line1[1:]
                    if (not isnumber(sym)) and (sym not in symboltable):
                        symboltable[sym] = str(count)
                        count += 1


    with open (infile,"r") as fin:
        with open (outfile,"w") as fout:
            for line2 in fin:
                line3 = stripspaces(line2)
                if line3 == "":
                    continue
                elif line3[0:2] == '//':
                    continue    
                elif line3[0] == '@':
                    idx = line3.find("//")
                    if idx == -1:
                        idx = len(line3)
                    sym = line3[1:idx]
                    if sym not in symboltable:
                        fout.write('@' + sym + '\n')
                    else:
                        fout.write('@'+ symboltable[sym]+'\n') 
                elif line3[0] != '(':
                    idx = line3.find("//")
                    if idx == -1:
                        idx = len(line3)
                    fout.write(line3[0:idx]+ '\n') 
            


import sys
# pass input, output filenames from command line
assembler(infile=sys.argv[1],outfile=sys.argv[2])
                             






 


               
