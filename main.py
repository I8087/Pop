# -*- coding: UTF-8 -*-

#import argparse
import os
import sys
import argparse

import pop
from pop.pop_lexer import *
from pop.pop_parser import *
from pop.pop_rpn import *

print("Pop Compiler Version %s | %s" % (pop.__version__,
                                        pop.__copyright__)
      )

# Setup the command line parser stuff.
aparser = argparse.ArgumentParser()
aparser.add_argument("input", help="the file(s) to be compiled")
aparser.add_argument("-o", help="the output file")
aparser.add_argument("-v", help="increase output verbosity",
                     action="store_true")
args = aparser.parse_args()

# Open the input file(s). NOTE: It takes only one file as of right now.
with open(args.input) as file:
    data = file.read().split("\n")
for i in range(len(data)):
    data[i] = data[i].rstrip()

# If everything went good, start the compiling proccess.
a, b, c = Lexer().lexer(data, args.input)
l = Parser().parser(a, b, c)

if l:
    if not args.o:
        args.o = args.input.split(".")[0]
    with open("%s.asm" % args.o, "w") as file:
        file.write("\n".join(l))

# Old batch script now embedded within Python. Update ASAP!
os.system("nasm -f win32 -o %s.obj %s.asm" % (args.o, args.o))
os.system("nasm -f win32 -o prt.obj asm/prt.asm")
os.system("Golink /console /entry __start /fo test.exe prt.obj %s.obj kernel32.dll user32.dll msvcrt.dll" % args.o)
#os.system("del %s.asm" % args.o)
os.system("del %s.obj" % args.o)
os.system("del prt.obj")
