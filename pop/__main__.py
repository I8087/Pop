# -*- coding: UTF-8 -*-

#import argparse
import os
import sys
import argparse

import pop
from pop.pop_lexer import *
from pop.pop_parser import *
from pop.pop_rpn import *

print("Pop Compiler Version {0} | {1}".format(pop.__version__,
                                              pop.__copyright__)
      )

# Setup the command line parser stuff.
aparser = argparse.ArgumentParser()
aparser.add_argument("input", help="the file(s) to be compiled",
                     nargs="+")
aparser.add_argument("-d", help="the build directory")
aparser.add_argument("-o", help="the output file")
aparser.add_argument("-v", help="increase output verbosity",
                     action="store_true")
args = aparser.parse_args()

# Don't compile if nothing's there!
if not args.input:
    exit()

# We need an output file name!
if not args.o:
    args.o = args.input[0].split(".")[0]

# List of object files to compile together.
objlist = ["prt.obj"]  # By default prt.obj is included.

for popfile in args.input:
    # Only compile pop source files!
    if not popfile.endswith(".pop"):
        continue

    # Open the input file(s). NOTE: It takes only one file as of right now.
    with open(popfile) as file:
        data = file.read().split("\n")
    for i in range(len(data)):
        data[i] = data[i].rstrip()

    # If everything went good, start the compiling proccess.
    a, b, c = Lexer().lexer(data, popfile)
    l = Parser().parser(a, b, c)

    if l:
        with open("{0}.asm".format(popfile[:-4]), "w") as file:
            file.write("\n".join(l))

        # Assemble the newly produced code.
        os.system("nasm -f win32 -o {0}.obj {0}.asm".format(popfile[:-4]))
        objlist.append("{0}.obj".format(popfile[:-4]))

# Assemble the pop runtime.
os.system("nasm -f win32 -o prt.obj asm/prt.asm")

# Link the object files together.
os.system("Golink /console /entry __start /fo test.exe {0} kernel32.dll user32.dll msvcrt.dll".format(" ".join(objlist)))

# Clean up any leftover object files.
for i in objlist:
    os.remove(i)
