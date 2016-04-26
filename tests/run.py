# This simple script builds every test*.pop file in the directory.

# Import the needed libraries.
import os, sys

# Change the directory to where the compiler is!
os.chdir("build")

# Get a list of test*.exe files.
exefiles = [i for i in os.listdir() if i.startswith("test") and i.endswith(".exe")]

# Tell the user that the test have started!
print("Starting the tests!")

# Build each exe file.
for i in exefiles:
    print("Running {0}...".format(i[:-4]))
    err = os.system(i)
    print("{0} error level is {1}.".format(i[:-4], err))

# Let the user know that the tests are done!
print("All done with the tests!")

# Pause when we're done, just for good measure!
os.system("pause")
