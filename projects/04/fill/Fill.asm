// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(CHECK)

@SCREEN
D=A
@addr
M=D

@i
M=0

@8191
D=A
@n
M=D

@KBD
D=M      
@FILL
D;JGT
@UNFILL
0;JMP



(FILL)
@i
D=M
@n
D=D-M
@CHECK
D;JGT

@addr
A=M
M=-1

@i
M=M+1
@addr
M=M+1
@FILL
0;JMP



(UNFILL)
@i
D=M
@n
D=D-M
@CHECK
D;JGT

@addr
A=M
M=0

@i
M=M+1
@addr
M=M+1
@UNFILL
0;JMP












