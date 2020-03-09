# opcode table from chapter 6 of "nand2tetris book"

comptable = {
    '0' : '0101010',
    '1' : '0111111',
    '-1': '0111010',
    'D' : '0001100',
    'A' : '0110000',
    '!D': '0001101',
    '!A': '0110001',
    '-D': '0001111',
    '-A': '0110011',
    'D+1':'0011111',
    'A+1':'0110111',
    'D-1':'0001110',
    'A-1':'0110010',
    'D+A':'0000010',
    'D-A':'0010011',
    'A-D':'0000111',
    'D&A':'0000000',
    'D|A':'0010101',
    'M' : '1110000',
    '!M': '1110001',
    '-M': '1110011',
    'M+1':'1110111',
    'M-1':'1110010',
    'D+M':'1000010',
    'D-M':'1010011',
    'M-D':'1000111',
    'D&M':'1000000',
    'D|M':'1010101'
    }

# strip whitespaces everywhere in a given string
def stripspaces(s):
    res = ''
    for i in s:
        if not i.isspace():
            res += i
    return res

# assemble code from input file (infile) and generate machine code into outfile
def assemblerns(infile, outfile):

    print("assembling -> ", infile)
    print("output -> ", outfile)

    with open (infile,"r") as fin:
        with open (outfile,"w") as fout:
            for line in fin:
                line = stripspaces(line)

                # ignore empty lines
                if line == "":
                    continue        
                elif len(line) >= 2 and line[0:2] == r"//": # ignore comment lines
                    continue
                elif line[0] == '@' : # A command
                    binary = bin(int(line[1:]))
                    excesszero = 16 - len(binary[2:])
                    # make sure that is 16 bit length
                    for i in range(excesszero):
                        fout.write('0')
                    fout.write( binary[2:] + '\n')
                else: # C command
                      list1 = line.split('=')
                      d1 = '0'
                      d2 = '0'
                      d3 = '0'
                      if len(list1) == 2:
                          if 'A' in list1[0]:
                              d1 = '1'
                          if 'D' in list1[0]:
                              d2 = '1'
                          if 'M' in list1[0]:
                              d3 = '1' 
                          list2 = list1[1].split(';')
                      else:
                          list2 = list1[0].split(';')

                      j1 = '0'
                      j2 = '0'
                      j3 = '0'
                      if len(list2) == 2:
                            if 'J' in list2[1] :
                                if 'G' in list2[1] or 'M' in list2[1] or 'N' in list2[1] :
                                    j3 = '1'
                                if 'L' in list2[1] or 'M' in list2[1] or 'N' in list2[1] :  
                                    j1 = '1'   
                                if  'M' in list2[1] or ('E' in list2[1] and 'N' not in list2[1]) :    
                                    j2 = '1'
                      ac1c2c3c4c5c6 = comptable[list2[0]]
                      fout.write( "111" + ac1c2c3c4c5c6 + d1 + d2 + d3 + j1 + j2 + j3 + '\n') 


import sys

# pass input, output filenames from command line
assemblerns(infile=sys.argv[1], outfile=sys.argv[2])
                     

                      
                      

                           



                         






                  
