# -*- coding: UTF-8 -*-

import os
import sys
import argparse

import pop
from pop.pop_lexer import *
from pop.pop_parser import *
from pop.pop_rpn import *
from pop.pop_config import *
from pop.pop_math import *

abi = ("win",
       "win32"
       )

print("Pop Compiler Version {0} | {1}".format(pop.__version__,
                                              pop.__copyright__)
      )

# Setup the command line parser stuff.
aparser = argparse.ArgumentParser()
aparser.add_argument("input", help="the file(s) to be compiled",
                     nargs="+")
aparser.add_argument("-a", help="do not discard the assembly file",
                     action="store_true")
aparser.add_argument("-d", help="the build directory")
aparser.add_argument("-o", help="the output file")
aparser.add_argument("-v", help="increase output verbosity",
                     action="store_true")
aparser.add_argument("-f", dest="abi", default="native",
                     choices=abi,
                     help="Builds the program to a certain platform abi.")

args = aparser.parse_args()

# Don't compile if nothing's there!
if not args.input:
    print("No input file(s) given!")
    exit(-1)

# Setup the build directory if there's one!
if args.d:
    os.chdir(args.d)

# Save the builds path and set the compiler path!
build_dir = os.getcwd()

# Special pathing must be used if this is pure python script!
if sys.argv[0].endswith(".py"):
    pop_dir = "\\".join(sys.argv[0].split("\\")[:-2])
elif sys.argv[0].endswith(".exe"):
    pop_dir = "\\".join(sys.executable.split("\\")[:-1])
else:
    print("Unknown file extension!!!")
    exit(-1)

os.chdir(pop_dir)

# We need an output file name!
if not args.o:
    args.o = args.input[0].split(".")[0]

# Get the build options.
options = Config().config()

# List of all the assembly files generated.
asmlist = []

# List of all the object files generated.
# By default prt.obj is included.
objlist = ["\"{0}\\prt.obj\"".format(build_dir)]

for popfile in args.input:
    # Only compile pop source files!
    if not popfile.endswith(".pop"):
        continue

    # Open the input file(s). NOTE: It takes only one file as of right now.
    with open("{0}\{1}".format(build_dir, popfile)) as file:
        data = file.read().split("\n")
    for i in range(len(data)):
        data[i] = data[i].rstrip()

    # Change the working directory.
    os.chdir(build_dir)

    # If everything went good, start the compiling proccess.
    a, b, c = Lexer().lexer(data, popfile)
    l = Parser().parser(a, b, c, options)

    # Change the working directory.
    os.chdir(pop_dir)

    if l:
        with open("{0}\\{1}.asm".format(build_dir, popfile[:-4]), "w") as file:
            file.write("\n".join(l))

        # Assemble the newly produced code.
        os.system("nasm -f win32 -o \"{0}\\{1}.obj\" \"{0}\\{1}.asm\"".format(
            build_dir,
            popfile[:-4])
                  )
        objlist.append("\"{0}\\{1}.obj\"".format(build_dir, popfile[:-4]))
        asmlist.append("\"{0}\\{1}.asm\"".format(build_dir, popfile[:-4]))

# Change the working directory.
os.chdir(pop_dir)

# Assemble the pop runtime.
os.system("nasm -f win32 -o \"{0}\\prt.obj\" asm\\prt.asm".format(build_dir,
                                                                  pop_dir))

if "\\" in args.o and not os.path.exists("{0}\\{1}".format(
        build_dir,
        args.o[:args.o.rfind("\\")])):
    os.mkdir("{0}\\{1}".format(build_dir, args.o[:args.o.rfind("\\")]))
elif not os.path.exists(build_dir):
    os.mkdir(build_dir)

# Link the object files together.
os.system("Golink /console /entry __start /fo \"{0}\\{1}\" "
          "{2} kernel32.dll user32.dll msvcrt.dll".format(build_dir,
                                                          args.o,
                                                          " ".join(objlist)))

# Change the working directory.
os.chdir(build_dir)

# Clean up any leftover assembly files.
if not args.a:
    for i in asmlist:
        os.remove(i[1:-1])

# Clean up any leftover object files.
for i in objlist:
    os.remove(i[1:-1])
