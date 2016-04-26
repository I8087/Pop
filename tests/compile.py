# This simple script builds every test*.pop file in the directory.

# Import the needed libraries.
import os, sys

# Change the directory to where the compiler is!
os.chdir("\\".join(sys.argv[0].split("\\")[:-2]))

# Get a list of test*.pop files.
popfiles = [i[:-4] for i in os.listdir("tests") if i.startswith("test") and i.endswith(".pop")]

# Build each pop file.
for i in popfiles:
    os.system("py -3.4 -m pop -d tests -o build\\{0}.exe {0}.pop".format(i))

# Pause when we're done, just for good measure!
os.system("pause")
