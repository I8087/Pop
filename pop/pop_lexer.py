"""
    Pop is a programming language that's a mix between C and
    Python. I've also added a lot of my own specifications, as well.
    The goal is to create a Pythonic language that allows for
    low-level functions, while creating a high-level language.

    Copyright (c) Nathan Yodock 2014-2016. All Rights Reserved.
"""

# TODO:
# * Make this script PEP 8 compliant.
# * Turn the operators list into a tuple.

# Integer name change?
# int8, int16, int32, int64?

# Floats will be as followed:
# float8, float16, float32, float64

# Import these needed libraries.
import string

# List of lexer tokens. (outdated)
# INDENT = The current indentation level.
# DATATYPE = This is a datatype keyword.
# NUMBER = A number.
# STRING = A string.
# VARIABLE = A variable that holds a value.


class Lexer():
    """This class contains the compilers' lexer."""

    def __init__(self):
        """This function is called when the class is constructed."""

        # A dictionary containing the size of integers in bytes.
        self.datasize = {"byte": 1, "short": 2, "int": 4, "long": 8}

        # List of operators in string form. Larger to smaller.
        # NOTE: Turn this into a tuple for a relative 7x speed increase.
        self.operators = [">>=", "<<=", "+=", "-=", "*=", "//=", "/=", "%=",
                          "&=", "|=", "^=", "<<", ">>", "==", "!=", "//",
                          "-", "+", "*", "/", "%", "(", ")", "[", "]",
                          ",", "=", ":", "&", "|", "^", "."]

        # Boolean keywords.
        # not, and, or

        # List of (un)needed operators (from C, Python, and Pop).
        # "~", "&&", "||", "<", "<=", ">", ">=", "@"

        # Possible use.
        # "!"

        # These aren't going to be used.
        # "++", "--", "?", "$"

    # Returns a list of tokens.
    def lexer(self, pram1, pram3="__main__.pop"):
        """This function creates a list for the praser.
           pram1 = A list containing each line of the program.
           pram3 = File name of the source code.
        """

        # pram1 = Data to lex in a list of lines.
        pram2 = []
        functions = []
        function = False
        function_name = ""
        function_datatype = ""
        function_signed = False
        function_decs = ""
        externc = False
        function_at = 0

        a, b, lines = self.count_lines(pram1, pram3)

        pram1 = self.build_lines(pram1)


        # Reset the count from the previous loop.
        count = 0

        for line in pram1:
            count += 1

            # Empty line and comments do not mess up
            # the indentation levels with the file.
            if line and not line.lstrip().startswith("#"):
                n = len(line)
                line = line.lstrip()
                pram2.append(["INDENT", n - len(line)])
            else:
                pram2.append(["INDENT", -1])
                line = ""

            if function:
                # Add function decorators...
                if not externc and not function_decs:
                    function_name += "_E"
                elif not externc:
                    function_name += function_decs

                for i in function_decs:
                    if i == "_":
                        continue

                    if i != "L":
                        function_at += 4
                    else:
                        function_at += 8

                functions.append([function_signed,
                                  function_datatype,
                                  function_name + "@%d" % function_at])
                function = False
                function_name = ""
                function_datatype = ""
                function_signed = False
                function_decs = ""
                function_at = 0
            externc = False

            # Keep looping until the string is empty.
            while line:

                if line.startswith("#"):
                    line = ""

                # Datatypes start here.
                elif line.startswith("func "):
                    pram2.append(["NAMESPACE", "FUNCTION"])
                    line = line[4:].strip()
                    function = True

                elif line.startswith("empty "):
                    pram2.append(["DATATYPE", "EMPTY"])
                    line = line[5:].strip()
                    if function and not function_datatype:
                        function_datatype = "EMPTY"
                    elif function:
                        function_decs += "_E"

                elif line.startswith("bool "):
                    pram2.append(["DATATYPE", "BOOL"])
                    line = line[4:].strip()
                    if function and not function_datatype:
                        function_datatype = "BOOL"
                    elif function:
                        function_decs += "_G"

                elif line.startswith("byte "):
                    pram2.append(["DATATYPE", "BYTE"])
                    line = line[4:].strip()
                    if function and not function_datatype:
                        function_datatype = "BYTE"
                    elif function:
                        function_decs += "_B"

                elif line.startswith("short "):
                    pram2.append(["DATATYPE", "SHORT"])
                    line = line[5:].strip()
                    if function and not function_datatype:
                        function_datatype = "SHORT"
                    elif function:
                        function_decs += "_S"

                elif line.startswith("int "):
                    pram2.append(["DATATYPE", "INT"])
                    line = line[3:].strip()
                    if function and not function_datatype:
                        function_datatype = "INT"
                    elif function:
                        function_decs += "_I"

                elif line.startswith("long "):
                    pram2.append(["DATATYPE", "LONG"])
                    line = line[4:].strip()
                    if function and not function_datatype:
                        function_datatype = "LONG"
                    elif function:
                        function_decs += "_L"

                elif line.startswith("string "):
                    pram2.append(["DATATYPE", "STRING"])
                    line = line[6:].strip()
                    if function and not function_datatype:
                        function_datatype = "STRING"
                    elif function:
                        function_decs += "_A"

                elif line.startswith("struct "):
                    pram2.append(["DATATYPE", "STRUCT"])
                    line = line[6:].strip()
                    if function and not function_datatype:
                        function_datatype = "STRUCT"
                    elif function:
                        function_decs += "_F"

                elif line.startswith("unsigned "):
                    pram2.append(["DATATYPE", "UNSIGNED"])
                    line = line[8:].strip()
                    if function:
                        function_signed = False

                elif line.startswith("signed "):
                    pram2.append(["DATATYPE", "SIGNED"])
                    line = line[6:].strip()
                    if function:
                        function_signed = True

                # Booleans start here.
                elif line.startswith("True ") or line == "True":
                    pram2.append(["BOOLEAN", "True"])
                    line = line[4:].strip()
                elif line.startswith("False ") or line == "False":
                    pram2.append(["BOOLEAN", "False"])
                    line = line[5:].strip()

                # Declares start here.
                elif line.startswith("externc "):
                    pram2.append(["STATEMENT", "EXTERNC"])
                    line = line[7:].strip()
                    externc = True

                elif line.startswith("extern "):
                    pram2.append(["STATEMENT", "EXTERN"])
                    line = line[6:].strip()

                # Statements start here.
                elif line == "return" or line[:7] == "return ":
                    pram2.append(["STATEMENT", "RETURN"])
                    line = line[6:].strip()

                elif line == "exit" or line[:5] == "exit ":
                    pram2.append(["STATEMENT", "EXIT"])
                    line = line[4:].strip()

                elif line == "pass" or line[:5] == "pass ":
                    pram2.append(["STATEMENT", "PASS"])
                    line = line[4:].strip()

                elif line == "nop" or line[:4] == "nop ":
                    pram2.append(["STATEMENT", "NOP"])
                    line = line[3:].strip()

                elif line.startswith("if "):
                    pram2.append(["STATEMENT", "IF"])
                    line = line[2:].strip()

                elif line.startswith("else ") or line[:4] == "else":
                    pram2.append(["STATEMENT", "ELSE"])
                    line = line[4:].strip()

                elif line.startswith("while "):
                    pram2.append(["STATEMENT", "WHILE"])
                    line = line[5:].strip()

                # Character literals start here.
                elif line[0] == "'":
                    line = line[1:]
                    n = 0
                    while line[0] != "'":

                        if ord(line[0]) <= 0xFF:
                            n <<= 8  # Shift a byte.

                            # Escape characters are proccessed by the compiler,
                            # not by a lib function.
                            if line[0] == "\\":

                                # Common escape characters supported.
                                if line[1] == "0":
                                    pass  # NUL
                                elif line[1] == "a":
                                    n += 0x07  # BEL
                                elif line[1] == "b":
                                    n += 0x08  # BS
                                elif line[1] == "t":
                                    n += 0x09  # HT
                                elif line[1] == "n":
                                    n += 0x0A  # LF
                                elif line[1] == "v":
                                    n += 0x0B  # VT
                                elif line[1] == "f":
                                    n += 0x0C  # FF
                                elif line[1] == "r":
                                    n += 0x0D  # CR
                                elif line[1] == "e":
                                    n += 0x1B  # ESC
                                elif line[1] == "\"":
                                    n += 0x22  # "
                                elif line[1] == "\'":
                                    n += 0x27  # '
                                elif line[1] == "\\":
                                    n += 0x5C  # \
                                else:
                                    self.lexer_error(
                                        "Unknown escape character!", count)
                                    exit(-1)

                                # Remove both characters.
                                line = line[2:]

                            # No escape characters; procced as normal.
                            else:
                                n += ord(line[0])
                                line = line[1:]

                        else:
                            self.lexer_error(
                                "Character exceeds the size of a byte!", count)
                            exit(-1)

                        # If the line is empty, then raise an error.
                        if not line:
                            self.lexer_error(
                                "Expected a closing single"
                                " quotation mark (')!", count)
                            exit(-1)

                    # Finish up.
                    pram2.append(["NUMBER", str(n)])

                    # Don't forget the ending single quotation mark.
                    line = line[1:].strip()

                # String literals start here.
                elif line[0] == "\"":
                    line = line[1:]  # Remove excess quotation mark.
                    n = "\""
                    while line[0] != "\"":
                        n += line[0]
                        line = line[1:]

                    n += "\""  # Add the remaining quotation mark.

                    # Finish up.
                    pram2.append(["STRING", n])

                    # Don't forget the ending single quotation mark.
                    line = line[1:].strip()

                # Check to see if it's an operator.
                elif (line[:1] in self.operators or
                      line[:2] in self.operators or
                      line[:3] in self.operators):

                    for i in self.operators:
                        if line.startswith(i):
                            pram2.append(["OPERATOR", i])
                            line = line[len(i):].strip()

                # Numbers start here.
                elif line[0] in string.digits:
                    if self.contains(line, self.operators+[" "]):
                        n = self.find_first(line, self.operators+[" "])
                        pram2.append(["NUMBER", line[:line.find(n)].strip()])
                        line = line[line.find(n):].strip()
                    else:
                        pram2.append(["NUMBER", line])
                        line = ""

                # Namespace start here.
                elif line[0] in string.ascii_letters:
                    if self.contains(line, self.operators+[" "]):
                        n = self.find_first(line, self.operators+[" "])
                        name = line[:line.find(n)].strip()
                        line = line[line.find(n):].strip()
                    else:
                        name = line
                        line = ""

                    if function and not function_name:
                        function_name = name

                    pram2.append(["NAMESPACE", name])
                else:
                    self.lexer_error("Unknown token!", count)
                    exit(1)
        pram2.append(["INDENT", 0])

        return pram2, functions, lines

    def internal_error(self, pram1, pram2):
        """This function is used when there's an internal error.
           pram1 = An error message to display.
           pram2 = The function in which the error occurred in.
        """

        print("Internal Lexer Error in '%s': %s" % (pram2, pram1))

    def lexer_error(self, pram1, pram2):
        """This function displays an error message caused by
           the programmer's code, not the compiler.
           pram1 = The error string.
           pram2 = The line number.
        """

        # Prints a formatted error string.
        print("Lexer Error @ %d: %s" % (pram2, pram1))

    def find_first(self, pram1, pram2):
        """Finds the substring closest to the left-hand side.
           pram1 = String to check.
           pram2 = List of strings to check for.
        """

        if not(pram1) or not(pram2):
            return False
        closest = ["", len(pram1)]  # Keep track of closest data.
        for i in pram2:
            n = pram1.find(i)
            if (n < closest[1]) and (n != -1):
                closest = [i, n]
        if closest[1] == -1:
            return False
        return closest[0]

    def contains(self, pram1, pram2):
        """Checks to see if a list of strings has at least one
           substring in another string to check for.
           pram1 = String to check.
           pram2 = List of strings to check for.
        """
        for i in pram2:
            if i in pram1:
                return True
        return False

    def count_lines(self, pram1, pram2="__main__.pop", pram3=0, pram4={}):
        """Creates a special file to line dictionary.
           pram1 = Lines
           pram2 = File name.
           pram3 = Current line. NOTE: Start at 0
           pram4 = The dictionary build. NOTE: Start at {}
        """

        temp = []

        for line in pram1:
            pram3 += 1
            # Count our lines.
            if pram2 not in pram4.keys():
                pram4[pram2] = []
            pram4[pram2].append(pram3)

            if line.startswith("import "):
                line = line[7:].strip()
                try:
                    with open(line, "r") as file:
                        data = file.read().split("\n")
                    for i in range(len(data)):
                        data[i] = data[i].rstrip()
                    discard, pram3, pram4 = self.count_lines(data, line, pram3, pram4)
                except:
                    self.lexer_error("Failed to import '%s'!" % line, pram3)
                    exit(0)
            elif " import " in line:
                self.lexer_error("Import error!", pram3)
                exit(0)

        return pram2, pram3, pram4

    def build_lines(self, pram1):
        count = 0
        temp = []
        for line in pram1:
            count += 1
            if line.startswith("import "):
                line = line[7:].strip()
                try:
                    with open(line, "r") as file:
                        data = file.read().split("\n")
                    for i in range(len(data)):
                        data[i] = data[i].rstrip()
                    temp.extend(self.build_lines(data))
                except:
                    self.lexer_error("Failed to import '%s'!" % line, count)
                    exit(0)
            elif " import " in line:
                self.lexer_error("Import error!", count)
                exit(0)
            else:
                temp.append(line)

        return temp
