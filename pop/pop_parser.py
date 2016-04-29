# Notice the word 'we' in my comments... obvious signs of insanity...

from pop.pop_rpn import *


class Parser():
    """This class contains the praser for Pop."""

    def __init__(self):

        # NOTE: I'm sure this class constructor has been over-abused.
        #       Clean it up!


        # Holds the text section.
        self.out = ["; This code was compiled via the pop compiler.",
                    "; It is machine generated, so it may look messy.",
                    "; Edit this source code at your own risk!",
                    "",
                    "%define True 1",  # Really? I know BOOL is a subtype of INT but still...
                    "%define False 0",
                    ""]

        self.out_offset = len(self.out)

        self.data = []  # Holds the data section.
        self.rodata = []  # Holds the rodata section. TBD.

        # Holds the externs.
        self.externs = ["___IndexError",
                        "___exit",
                        "___malloc",
                        "___free",
                        "___strlen",
                        "___strcpy",
                        "___strinit",
                        "___strcat",
                        "___striter",
                        "___strindex"]

        self.indent_level = -1
        self.indent = []  # Holds a dictionary of indentation levels.
        self.line = -1

        # STRUCT info
        self.structs = {}  # This holds a list of all the global structures.
        self.current_structs = []  # This holds a list of current structure indentations.

        # Setup function values.
        self.function = False
        self.function_signed = False
        self.function_datatype = ""
        self.function_namespace = ""
        self.function_line = 0
        self.functions = []
        self.if_done = False  # Flag for elif & else.

        # This contains the systems info. For now, it is hard-coded info.
        # (It can be altered for cross-compilers.)
        self.options = {"OS_NAME": "Windows",
                        "OS_MAJOR": 0,  # What kind of crappy Window's is that?
                        "OS_MINOR": 0,
                        "BIT": 32}

        self.options = {}

        # A list of strings.
        self.strings = []

        # Setup temporary variable values.
        self.signed = False  # Signedness of the variable.
        self.datatype = ""
        self.namespace = ""
        self.value = None

        # C globals.
        self.globals_c = []

        # globals holds a list of names to declare for the linker.
        self.globals = []

        # Temp list of conditional statement labels.
        self.cons = []

        # List of temp generated labels for use in functions.
        self.labels = []

        self.location = 0
        self.defined = {"__global__": []}  # Becoming obsolete...

    def parser(self, pram1, pram2, pram3, pram4, pram5 = {"__global__": []}):
        """This function parser's a list created by the lexer.
           pram1 = This is the list created by the lexer.
           pram2 = This is a list of all of the functions found by the lexer.
           pram3 = File to line dictionary.
           pram4 = Build options in a dictionary.
           pram5 = Optional. A dictionary of functions and variable.
        """

        # If pram1 isn't a list, then throw an error.
        if not(isinstance(pram1, list)):
            self.internal_error("pram1 isn't a list!", "parser")
            return []

        # If pram2 isn't a dictionary, then throw an error.
        if not(isinstance(pram2, list)):
            self.internal_error("pram2 isn't a list!", "parser")
            return []

        # Create a class list...
        self.functions = pram2

        # If pram3 isn't a dictionary, then throw an error.
        if not(isinstance(pram3, dict)):
            self.internal_error("pram3 isn't a dict!", "parser")
            return []

        # Turn this into a global variable.
        self.filelines = pram3

        # If pram4 isn't a dictionary, then throw an error.
        if not(isinstance(pram4, dict)):
            self.internal_error("pram4 isn't a dict!", "parser")
            return []

        # Save the build options.
        self.options = pram4

        # If pram5 isn't a dictionary, then throw an error.
        if not(isinstance(pram5, dict)):
            self.internal_error("pram5 isn't a dict!", "parser")
            return []

        # This will be the main loop of the parser.
        while pram1:

            if pram1[0][0] == "NAMESPACE" and pram1[0][1] == "FUNCTION":
                self.do_function(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "RETURN":
                del pram1[0]
                self.do_return(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "EXIT":
                del pram1[0]
                self.do_exit(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "PASS":
                del pram1[0]

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "NOP":
                del pram1[0]
                self.out.append("nop")

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "EXTERN":
                del pram1[0]
                self.do_extern(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "EXTERNC":
                del pram1[0]
                self.do_externc(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "WHILE":
                del pram1[0]
                self.do_while(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "IF":
                del pram1[0]
                self.do_if(pram1)

            elif pram1[0][0] == "STATEMENT" and pram1[0][1] == "ELSE":
                del pram1[0]
                self.do_else(pram1)

            elif pram1[0][0] == "DATATYPE" and pram1[0][1] == "STRUCT":
                del pram1[0]
                self.do_struct(pram1)

            elif (pram1[0][0] == "DATATYPE"):
                # It can be assumed that this datatype isn't signed.
                self.signed = False

                # Assign the datatype.
                self.datatype = pram1[0][1]

                if self.function and self.datatype == "LONG":
                    self.location -= 8
                elif self.function:
                    self.location -= 4

                del pram1[0]

                # Throw an error.
                if pram1[0][0] != "NAMESPACE":
                    self.parser_error("Expected a namespace.", self.line)
                    return []
                else:
                    self.namespace = pram1[0][1]
                    del pram1[0]

                    # Add this variable into the defined dictionary for later static reference.
                if self.function:
                    self.defined[self.function_namespace].append(
                        [self.signed,
                         self.datatype,
                         self.namespace,
                         self.location])
                elif not self.function and self.current_structs:
                    self.structs[self.current_structs[-1]].append({"signed": self.signed,
                                                                   "datatype": self.datatype,
                                                                   "namespace": self.namespace})
                else:
                    self.defined["__global__"].append([self.signed, self.datatype, self.namespace])

                # If there is an assignment, then math will be needed.
                if (pram1[0][0] == "OPERATOR") and (pram1[0][1] == "="):
                    pram1.insert(0, ["NAMESPACE", self.namespace])
                    self.math(pram1)
                else:
                    self.value = "dword 0"

                # Make sure there isn't any trailing code.
                if pram1[0][0] == "INDENT":

                    # Reset these variables now that they're no longer needed.
                    self.signed = False
                    self.datatype = ""
                    self.namespace = ""
                    self.value = None

                # If there's trailing code, then an error should be thrown.
                else:
                    self.parser_error("Unknown code at the end of the line.",
                                      self.line)
                    return []

            elif (pram1[0][0] == "NAMESPACE" and
                  pram1[1][0] == "OPERATOR" and
                  pram1[1][1] == "("):
                self.math(pram1)

            # For already declared variables.
            elif pram1[0][0] == "NAMESPACE":
                found = False

                for i in self.defined["__global__"]:
                    if i[2] == pram1[0][1] and not(found):
                        found = True
                        self.namespace = pram1[0][1]
                        self.signed = i[0]
                        self.datatype = i[1]
                        self.math(pram1)

                if self.function_namespace:
                    for i in self.defined[self.function_namespace]:
                        if i[2] == pram1[0][1] and not(found):
                            found = True
                            self.namespace = pram1[0][1]
                            self.signed = i[0]
                            self.datatype = i[1]
                            self.math(pram1)

                if not found:
                    self.parser_error("Variable `%s` is undefined!" % pram1[0][1], self.line)
                    return []

                # Don't change an empty function!
                if self.function_namespace == "__global__": self.function_namespace = "__global__"

            # This is needed after every line or there's an error!
            # Ensures that there's no garbage at the end of the code!
            if pram1[0][0] == "INDENT":
                self.line += 1
                self.if_done = False
                self.indent_level = pram1[0][1]
                del pram1[0]
                self.do_indent(pram1)
            else:
                self.parser_error("Unknown garbage at the end of the line!", self.line)
                exit()

        # Insert the text section declaration.
        self.out.insert(self.out_offset, "")
        self.out.insert(self.out_offset, "SECTION .text\n")
        self.out.insert(self.out_offset, "")

        # Define our structures for NASM!
        if self.structs:
            for i in self.structs.keys():
                self.out.insert(self.out_offset, "")
                self.out.insert(self.out_offset, "endstruc")
                self.structs[i] = self.structs[i][::-1]  # Reverse the variables.

                # Write the variables to the output.
                for x in self.structs[i]:
                    self.out.insert(self.out_offset,
                                    "{:>4}.{}: {} 0".format(" ",
                                                            x["namespace"],
                                                            self.res_shrink(x["datatype"])))

                # Don't forget the structures name!
                self.out.insert(self.out_offset, "struc {}".format(i))

        if self.globals:
            self.out.insert(self.out_offset, "")
            for i in self.globals:
                self.out.insert(self.out_offset, "global %s" % i)

        if self.externs:
            self.out.insert(self.out_offset, "")
            for i in self.externs:
                self.out.insert(self.out_offset, "extern %s" % i)

        # Don't add a pointless section if it's not needed. Plus,
        # having a data section with no data would break the OS.
        if self.data:
            self.data.insert(self.out_offset, "\nSECTION .data")
            self.out += self.data

        if self.strings:
            self.out.append("SECTION .data")
            n = 0
            for i in self.defined["__global__"]:
                self.out.append("%s: %s 0" % (i[2], self.shrink(i[1])))
            for i in self.strings:
                self.out.append("string%d: db %s" % (n, i))
                n += 1

        for i in range(len(self.out)):
            if not self.out[i].endswith(":"):
                self.out[i] = "{:>4}{}".format("", self.out[i]).rstrip()

                # Excessive line breaks are flagged.
                if i > 0 and self.out[i] == "" and (self.out[i-1] == "" or
                                                    self.out[i-1].endswith(":")):
                    self.out[i] = None

        # Excessive line breaks are now removed. :D
        self.out = [i for i in self.out if i != None]

        # Return the list of assembly.
        return self.out

    def do_while(self, pram1):
        """This function computes the while statement.
           pram1 = A list of tokens.
        """

        second = False
        found = False

        cmp = ""

        # Well...it's name says it all...
        temp_list = []

        lbl = self.create_label()
        self.cons.append(lbl)

        self.out.append("%s:" % lbl)

        while pram1[0][0] != "INDENT":
            if pram1[0][1] not in ("==", "!=", ":"):
                temp_list.append(pram1[0])
                del pram1[0]
            else:
                if pram1[0][1] != ":": found = True
                if temp_list[0][0] == "NAMESPACE":
                    self.datatype = self.dtype(temp_list[0][1])
                else:
                    self.datatype = "INT"

                temp_list.append(["INDENT", -1])

                # Trick math with a dummy list.
                self.math(temp_list)

                if not second:
                    self.out.append("mov ebx, eax")
                    second = True

                temp_list = []

                if not cmp:
                    cmp = pram1[0][1]

                del pram1[0]

        self.indent.append(["WHILE_NEXT", self.indent_level])

        if found:
            self.out.append("cmp eax, ebx")
        else:
            del self.out[-1]
            self.out.append("test eax, eax")
            cmp = "jz"

        lbl = self.create_label()
        self.cons.append(lbl)

        if cmp == "==":
            self.out.append("jne %s" % lbl)
        elif cmp == "!=":
            self.out.append("je %s" % lbl)
        elif cmp == "jz":
            self.out.append("jz %s" % lbl)

        # Keep the code neat and tidy!
        self.out.append("")

    def do_else(self, pram1):
        """This function computes the if statement.
           pram1 = A list of tokens.
        """

        if not self.if_done:
            self.parser_error("Need an if statement before an else statement!", self.line)
            exit(-1)

        if not pram1[0][1] == ":":
            self.parser_error("Expected a colon at the end!", self.line)
            exit(-1)

        del pram1[0]

        self.indent.append(["ELSE_NEXT", self.indent_level])

        lbl = self.create_label()
        self.cons.append(lbl)

        self.out.insert(-1, "jmp %s" % lbl)
        self.out.insert(-1, "")

    def do_if(self, pram1):
        """This function computes the if statement.
           pram1 = A list of tokens.
        """

        second = False
        found = False

        cmp = ""

        # Well...it's name says it all...
        temp_list = []

        while pram1[0][0] != "INDENT":
            if pram1[0][1] not in ("==", "!=", ":"):
                temp_list.append(pram1[0])
                del pram1[0]
            else:
                if pram1[0][1] != ":": found = True
                if temp_list[0][0] == "NAMESPACE":
                    self.datatype = self.dtype(temp_list[0][1])
                else:
                    self.datatype = "INT"

                temp_list.append(["INDENT", -1])

                # Trick math with a dummy list.
                self.math(temp_list)

                if not second:
                    self.out.append("mov ebx, eax")
                    second = True

                temp_list = []


                if not cmp:
                    cmp = pram1[0][1]

                del pram1[0]

        self.indent.append(["IF_NEXT", self.indent_level])


        if found:
            self.out.append("cmp eax, ebx")
        else:
            del self.out[-1]
            self.out.append("test eax, eax")
            cmp = "jz"

        lbl = self.create_label()
        self.cons.append(lbl)

        if cmp == "==":
            self.out.append("jne %s" % lbl)
        elif cmp == "!=":
            self.out.append("je %s" % lbl)
        elif cmp == "jz":
            self.out.append("jz %s" % lbl)

        # Keep the code neat and tidy!
        self.out.append("")

    def do_struct(self, pram1):
        """This function builds structures.
           pram1 = A list of tokens.
        """

        if pram1[0][0] == "NAMESPACE":
            self.structs[pram1[0][1]] = []
            self.current_structs.append(pram1[0][1])
            del pram1[0]
        else:
            self.parser_error("Expected a structure namespace!", self.line)
            exit(-1)

        if pram1[0][1] == ":":
            del pram1[0]
        else:
            self.parser_error("Expected an ending ':'!", self.line)
            exit(-1)

        self.indent.append(["STRUCT_NEXT", self.indent_level])

    def do_externc(self, pram1):
        """This function compiles and analyzes the external functions much
           like do_extern, except it puts it in a C styled format. This is
           useful for briding C like languages with Pop.
           pram1 = A list of tokens.
        """

        if not (pram1[0][0] == "NAMESPACE" and pram1[0][1] == "FUNCTION"):
            self.parser_error("Expected a function!", self.line)
            exit(0)

        del pram1[0]

        if not pram1[0][0] == "DATATYPE":
            self.parser_error("Expected a datatype!", self.line)
            exit(0)

        del pram1[0]

        if not pram1[0][0] == "NAMESPACE":
            self.parser_error("Expected a namespace!", self.line)
            exit(0)

        func = pram1[0][1]
        dec = 0

        del pram1[0]

        if (pram1[0][0] == "OPERATOR") and (pram1[0][1] == "("):
            del pram1[0]
        else:
            self.parser_error("Expected a starting paratheses.", self.line)
            exit(0)

        while (pram1[0][0] != "OPERATOR") and (pram1[0][1] != ")"):
            if (pram1[0][0] == "INDENT"):
                self.parser_error("Expected a closing parenthese!", self.line)
                exit()
            elif (pram1[0][0] == "DATATYPE" and pram1[1][0] == "NAMESPACE"):

                # This is important for stack allocation purposes.
                if pram1[0][1] == "LONG":
                    dec += 8
                else:
                    dec += 4

                # Get rid of the namespace and data type tokens.
                del pram1[0]
                del pram1[0]

            else:
                self.parser_error("An error has occurred within a function's parmeters.", self.line)

            # A comma is expected after ever prameter,
            # unless it is the end of prameters.
            if pram1[0][0] == "OPERATOR" and pram1[0][1] == ",":
                del pram1[0]
            elif pram1[0][0] == "OPERATOR" and pram1[0][1] != ")":
                self.parser_error("Expected a comma!", self.line)
                exit()

        # Remove ")" symbol.
        del pram1[0]

        self.externs.append("_%s@%d" % (func, dec))

        if func not in self.defined:
            self.defined[func] = [] # NOTE! Get parameters. Why?
        else:
            self.parser_error("Cannot redeclare a function!.", self.line)
            exit(0)

    def do_extern(self, pram1):
        """This function compiles and analyzes the the external functions.
           pram1 = A list of tokens.
        """

        if not (pram1[0][0] == "NAMESPACE" and pram1[0][1] == "FUNCTION"):
            self.parser_error("Expected a function!", self.line)
            exit(0)
        else:
            del pram1[0]

        if not pram1[0][0] == "DATATYPE":
            self.parser_error("Expected a datatype!", self.line)
            exit(0)
        else:
            del pram1[0]

        if not pram1[0][0] == "NAMESPACE":
            self.parser_error("Expected a namespace!", self.line)
            exit(0)

        func = pram1[0][1]
        dec = 0
        temp = ""
        temp_list = []

        del pram1[0]

        if (pram1[0][0] == "OPERATOR") and (pram1[0][1] == "("):
            del pram1[0]
        else:
            self.parser_error("Expected a starting paratheses.", self.line)
            exit(0)

        while (pram1[0][0] != "OPERATOR") and (pram1[0][1] != ")"):
            if (pram1[0][0] == "INDENT"):
                self.parser_error("Expected a closing parenthese!", self.line)
                exit()
            elif (pram1[0][0] == "DATATYPE" and pram1[1][0] == "NAMESPACE"):

                temp_list.append([False, pram1[0][1], pram1[1][1], "+%d" % dec])

                # This is important for stack allocation purposes.
                if pram1[0][1] == "BYTE":
                    temp += "_B"
                elif pram1[0][1] == "SHORT":
                    temp += "_S"
                elif pram1[0][1] == "INT":
                    temp += "_I"
                elif pram1[0][1] == "LONG":
                    temp += "_L"
                    dec += 4
                elif pram1[0][1] == "STRING":
                    temp += "_A"
                elif pram1[0][1] == "BOOL":
                    temp += "_G"

                dec += 4

                # Get rid of the namespace and data type tokens.
                del pram1[0]
                del pram1[0]

            else:
                self.parser_error("An error has occurred within a function's parmeters.", self.line)

            # A comma is expected after ever prameter,
            # unless it is the end of prameters.
            if pram1[0][0] == "OPERATOR" and pram1[0][1] == ",":
                del pram1[0]
            elif pram1[0][0] == "OPERATOR" and pram1[0][1] != ")":
                self.parser_error("Expected a comma!", self.line)
                exit()

        # Remove ")" symbol.
        del pram1[0]

        if not temp:
            temp = "_E"

        self.externs.append("_%s%s@%d" % (func, temp, dec))

        func += temp

        if func not in self.defined:
            self.defined[func] = temp_list
        else:
            self.parser_error("Cannot redeclare a function!.")
            exit(0)



    def do_function(self, pram1):
        """This function implements the compilers function compiling.
           pram1 = A list of tokens.
        """

        function_prams = []

        # Delete this namespace.
        del pram1[0]

        if pram1[0][0] == "DATATYPE" and pram1[0][1] in ("SIGNED", "UNSIGNED"):
            del pram1[0]

        # Don't merge with the above if statement.
        # It could have a datatype and signedness.
        if (pram1[0][0] == "DATATYPE"):
            self.function_datatype = pram1[0][1]
            self.datatype = pram1[0][1]
            del pram1[0]
        else:
            self.parser_error("Expected a data type for the function!", self.line)

        if (pram1[0][0] == "NAMESPACE"):
            self.function_namespace = pram1[0][1]
            del pram1[0]
        else:
            self.parser_error("Expected a function namespace!", self.line)
            exit()

        # Throw an error if there aren't any parentheses.
        if not(pram1[0][0] == "OPERATOR") and pram1[0][1] == "(":
            self.parser_error("Expected an opening parenthese.", self.line)
            exit(0)
        else:
            del pram1[0]
            location = 8 # This is a local variable that isn't the same as self.location!

            temp_list = []
            while (pram1[0][0] != "OPERATOR") and (pram1[0][1] != ")"):
                if (pram1[0][0] == "INDENT"):
                    self.parser_error("Expected a closing parenthese!", self.line)
                    exit()
                elif (pram1[0][0] == "DATATYPE" and pram1[1][0] == "NAMESPACE"):

                    # No need to check for duplicates; the lexer handles that.
                    temp_list.append([False, pram1[0][1], pram1[1][1], "+%d" % location])

                    # This is important for stack allocation purposes.
                    if pram1[0][1] == "LONG":
                        location += 8
                    else:
                        location += 4


                    function_prams.append(pram1[0][1])
                    # Get rid of the namespace and data type tokens.
                    del pram1[0]
                    del pram1[0]
                else:
                    self.parser_error("An error has occurred within a function's parameters.", self.line)

                # A comma is expected after ever prameter, unless it is the end of prameters.
                if pram1[0][0] == "OPERATOR" and pram1[0][1] == ",":
                    del pram1[0]
                elif pram1[0][0] == "OPERATOR" and pram1[0][1] != ")":
                    self.parser_error("Expected a comma!", self.line)
                    exit()

            # Delete the ')'
            del pram1[0]

            if (pram1[0][0] != "OPERATOR") or (pram1[0][1] != ":"):
                self.parser_error("Expected a colon at the end of the function", self.line)
                exit()

            del pram1[0]

        # Setup the function information
        self.function = True
        self.indent.append(["FUNCTION_NEXT", self.indent_level])

        temp = ""

        for i in function_prams:
            if i in ("EMPTY", "BYTE", "SHORT", "INT", "LONG"):
                temp += "_%s" % i[0]
            elif i == "BOOL":
                temp += "_G"
            elif i == "STRING":
                temp += "_A"

        if not temp:
            temp = "_E"

        self.function_namespace += temp

        # Define a list for the compiler to keep track of
        # all of the variables within the function!
        self.defined[self.function_namespace] = temp_list

        # New temp.
        temp = "_%s@%d:" % (self.function_namespace, location-8)

        self.out.append(temp)
        self.out.append("push ebp")
        self.out.append("mov ebp, esp")
        self.function_line = len(self.out)
        self.out.append("")

    def do_indent(self, pram1):
        """This function implements the compilers indentation.
           pram1 = A list of tokens.
        """

        # If this is an empty line, then get out of here!
        if self.indent_level == -1:
            return
        elif (len(self.indent) == 0) and (self.indent_level == 0):
            return
        elif (len(self.indent) == 0) and (self.indent_level != 0):
            self.parser_error("Indentation error!", self.line)
            return []

        elif (len(self.indent) != 0) and (self.indent_level == self.indent[-1][1]):
            return

        elif self.indent[-1][0] == "FUNCTION_NEXT" and (self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("FUNCTION", self.indent_level))

        elif self.indent[-1][0] == "STRUCT_NEXT" and (self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("STRUCT", self.indent_level))

        elif self.indent[-1][0] == "WHILE_NEXT" and (self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("WHILE", self.indent_level))

        elif self.indent[-1][0] == "IF_NEXT" and (self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("IF", self.indent_level))

        elif self.indent[-1][0] == "ELSE_NEXT" and (self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("ELSE", self.indent_level))

        elif self.indent[-1][0] == "FUNCTION":

            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1] # Delete it now.

                pram1.insert(0, ["INDENT", -1])

                if self.location != 0:
                    self.out.insert(self.function_line,
                                    "sub esp, %d" % (abs(self.location)))
                    self.out.insert(self.function_line+1,"")

                # Append this leaving code for the function.
                self.do_return(pram1)
                self.out.append("")

                # Reset the function prameters.
                self.function = False
                self.function_signed = False
                self.function_datatype = ""
                self.function_namespace = ""
                self.function_prams = []
                self.cons = []
                self.labels = []

                # Reset the location.
                self.location = 0
                self.function_line = -1

        elif self.indent[-1][0] == "STRUCT":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1] # Delete it now.

            # Clean up.
            del self.current_structs[-1]

        elif self.indent[-1][0] == "WHILE":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1] # Delete it now.

                # Important if cleanup code here.
                self.out.append("jmp %s" % self.cons[-2])
                self.out.append("")
                self.out.append("%s:" % self.cons[-1])

                del self.cons[-1]
                del self.cons[-1]

        elif self.indent[-1][0] == "IF":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1] # Delete it now.

                # Important if cleanup code here.
                self.out.append("")
                self.out.append("%s:" % self.cons[-1])

                del self.cons[-1]

                self.if_done = True

        elif self.indent[-1][0] == "ELSE":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1] # Delete it now.

                # Important else cleanup code here.
                self.out.append("")
                self.out.append("%s:" % self.cons[-1])

                del self.cons[-1]

        else:
            self.parser_error("Unknown indentation error!", self.line)
            exit(1)

        # If there isn't any indentation, then remove all of the nests.
        if self.indent_level == 0 and self.indent:
            self.do_indent(pram1)

    def do_return(self, pram1):
        """This function handles the return statement.
           pram1 = The list of tokens.
        """

        # Don't repeat a return statement!
        if self.out[-1] == "ret" and \
           self.out[-2] == "pop ebp" and \
           self.out[-3] == "mov esp, ebp":

            # Remove excess garbage!
            while pram1[0][0] != "INDENT":
                del pram1[0]
            return

        # Add this for file neatness.
        self.out.append("")

        if len(pram1) and pram1[0][0] != "INDENT":
            if self.function:
                self.datatype = self.function_datatype
            else:
                self.datatype = "INT"
            if self.datatype == "EMPTY":
                self.parser_error("An `empty` cannot return anything!", self.line)
                exit(1)
            self.math(pram1)
        else:
            self.out.append("xor eax, eax")

        # Simple append a return statement. AX holds returns.
        self.out.append("mov esp, ebp")
        self.out.append("pop ebp")
        self.out.append("ret")
        self.out.append("")

    def do_exit(self, pram1):

        # Add this for file neatness.
        self.out.append("")

        if len(pram1) and pram1[0][0] != "INDENT":
            self.datatype = "INT"
            self.math(pram1)
        else:
            self.out.append("xor %s, %s" % (self.reg("INT"),
                                            self.reg("INT")))

        self.out.append("push %s" % self.reg("INT"))
        self.out.append("call ___exit")
        self.out.append("add esp, 4")

    def internal_error(self, pram1, pram2):
        """This function is used when there's an internal error.
           pram1 = An error message to display.
           pram2 = The function in which the error occurred in.
        """

        print("Internal Parser Error in '%s': %s" % (pram2, pram1))


    def parser_error(self, pram1, pram2):
        """This function displays an error message caused by the programmer's code, not the compiler.
           pram1 = The error string.
           pram2 = The line number.
        """

        line = -1
        file = "undefined"

        for i in self.filelines.keys():
            if pram2 in self.filelines[i]:
                line = self.filelines[i].index(pram2) + 1
                file = i

        # Prints a formatted error string.
        print("Parser Error in '%s' @ %d: %s" % (file, line, pram1))


    def get_function_name(self, pram1, pram2):
        """This function returns a decorated function name.
           pram1 = An undecorated function name.
           pram2 = A list of each parameter's data type.
        """

        # The number of bytes to use in the decorator.
        size = 0

        # Create a shallow copy of self.function!
        funcs = self.functions[:]

        for func in funcs:
            # Test to see if this function exists...
            for i in range(len(funcs)):
                if funcs[i][2].startswith(pram1): break # It's okay.
                funcs[i] = ["", "", ""] # Do not modify the list; it's a deep copy.
                                        # This *will* corrupt self.functions!

            else:
                self.parser_error("This function doesn't exist!", self.line)
                exit(-1)

        temp = ""

        dec = 0

        for i in pram2:
            if i == "BYTE":
                temp += "_B"
            elif i == "SHORT":
                temp += "_S"
            elif i == "INT":
                temp += "_I"
            elif i == "LONG":
                temp += "_L"
                dec += 4
            elif i == "STRING":
                temp += "_A"
            elif i == "BOOL":
                temp += "_G"

            dec += 4

        if not temp:
            temp = "_E"

        temp_list = []

        # Test to see if this function exists...
        for i in funcs:
            if i[2].startswith(pram1) and i[2].endswith("@%d" % dec):
                temp_list.append(i[:])

        if not temp_list:
            self.parser_error("This function's parameters are wrong!", self.line)
            exit(-1)

        temp2 = ""

        # Strictly for type casting
        if "%s%s" % (pram1, temp) not in self.defined.keys():
            for i in range(len(temp)//2):
                x = temp[i*2+1]
                y = ""
                for t in temp_list:  # This area might cause problems; keep an eye on it.
                    t[2] = t[2][t[2].find("_")+1:]
                    if t[2][0] == "G" and not y:
                        y = "G"
                    elif t[2][0] == "A" and not y:
                        y = "A"
                    elif t[2][0] == "B" and (x == "B" and not y):
                        y = "B"
                    elif t[2][0] == "S" and (x == "S" and not y and y != "B"):
                        y = "S"
                    elif t[2][0] == "I" and (x == "I" and not y and y not in ("B", "S")):
                        y = "I"
                    # Longs aren't supported yet.
                if not y:
                    y = x
                temp2 += "_%s" % y
            temp = temp2

        if pram1 in self.defined:
            return "call _%s@%d" % (pram1, dec)
        else:
            return "call _%s%s@%d" % (pram1, temp, dec)

    def shrink(self, pram1):
        """ Turns a datatype like 'BYTE' into asm datatypes, like 'db'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL" or pram1 == "STRING":
            return "db"
        elif pram1 == "SHORT":
            return "dw"
        elif pram1 == "INT":
            return "dd"
        elif pram1 == "LONG":
            return "dq"
        else:
            self.internal_error("An unknown data type was passed.", self.line)

    def res_shrink(self, pram1):
        """ Turns a datatype like 'BYTE' into asm uninitialized datatypes, like 'resb'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL" or pram1 == "STRING":
            return "resb"
        elif pram1 == "SHORT":
            return "resw"
        elif pram1 == "INT":
            return "resd"
        elif pram1 == "LONG":
            return "resq"
        else:
            self.internal_error("An unknown data type was passed.", self.line)

    def p_reg_a(self):
        """ Returns the systems memory sized ?a? register.
        """

        if self.options["BIT"] == 16:
            return "ax"
        elif self.options["BIT"] == 32:
            return "eax"
        elif self.options["BIT"] == 64:
            return "rax"
        else:
            self.internal_error("An unknown datatype was passed.", "p_reg_a")

    def p_reg_b(self):
        """ Returns the systems memory sized ?b? register.
        """

        if self.options["BIT"] == 16:
            return "bx"
        elif self.options["BIT"] == 32:
            return "ebx"
        elif self.options["BIT"] == 64:
            return "rbx"
        else:
            self.internal_error("An unknown datatype was passed.", "p_reg_b")

    def reg(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'al'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL":
            return "al"
        elif pram1 == "SHORT":
            return "ax"
        elif pram1 == "INT" or (pram1 == "STRING" and self.options["BIT"] == 32):
            return "eax"
        elif pram1 == "LONG":
            return "rax"
        elif pram1 == "EMPTY":
            return "?empty?"
        else:
            self.internal_error("An unknown datatype was passed.", "reg")
            exit()

    def reg_b(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'bl'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL":
            return "bl"
        elif pram1 == "SHORT":
            return "bx"
        elif (pram1 == "INT" or
              (pram1 == "STRING" and
               self.options["BIT"] == 32)):
            return "ebx"
        elif pram1 == "LONG":
            return "rbx"
        elif pram1 == "EMPTY":
            return "?empty?"
        else:
            self.internal_error("An unknown datatype was passed.", "reg_b")
            exit()

    def reg_c(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'cl'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL":
            return "cl"
        elif pram1 == "SHORT":
            return "cx"
        elif pram1 == "INT" or (pram1 == "STRING" and self.options["BIT"] == 32):
            return "ecx"
        elif pram1 == "LONG":
            return "rcx"
        elif pram1 == "EMPTY":
            return "?empty?"
        else:
            self.internal_error("An unknown datatype was passed.", "reg_c")
            exit()

    def reg_d(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'al'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL":
            return "dl"
        elif pram1 == "SHORT":
            return "dx"
        elif pram1 == "INT" or (pram1 == "STRING" and self.options["BIT"] == 32):
            return "edx"
        elif pram1 == "LONG":
            return "rdx"
        elif pram1 == "EMPTY":
            return "?empty?"
        else:
            self.internal_error("An unknown datatype was passed.", "reg")
            exit()

    def size(self, pram1):
        """ Turns a datatype like 'INT' into an aligned register, like 'dword'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL":
            return "byte"
        elif pram1 == "SHORT":
            return "word"
        elif pram1 == "INT" or (pram1 == "STRING" and self.options["BIT"] == 32):
            return "dword"
        elif pram1 == "LONG":
            return "qword"
        else:
            self.internal_error("An unknown datatype was passed.", "size")
            exit(0)

    def dtype(self, pram1):
        """ Finds the datatype of a variable.
            pram1 = The name of the variable.
        """

        if (pram1.startswith("[") and
            pram1.endswith("]")):
            pram1 = pram1[1:-1]

        for i in self.defined["__global__"]:
            if i[2] == pram1:
                return i[1]

        for i in self.defined[self.function_namespace]:
            if i[2] == pram1:
                return i[1]


        if pram1.startswith("string"):
            return "STRING"

        if pram1.isdigit():
            return "INT"

        if pram1 in ("True", "False"):
            return "BOOL"

        # WRONG!!!
        if pram1.startswith("ebp"):
            return "INT"

        self.parser_error("The variable '%s' is undefined!" % pram1, self.line)
        exit(-1)

    def num_dtype(self, pram1):
        """ Gives a number like '103' or '-129802' a datatype.
            pram1 = Number to use.
        """

        # Turn the parameter into an int incase it's a string or something.
        v = int(pram1)

        if v <= 255:
            return "BYTE"
        elif v <= 65535:
            return "SHORT"
        elif v <= 4294967295:
            return "INT"
        elif v > 4294967295:
            return "LONG"
        else:
            self.internal_error("An unknown number size was passed.", "num_dtype")

    def locate(self, pram1):
        """ Finds the location of a stack-based variable.
            pram1 = The name of the variable.
        """

        #if not self.function:
        #    self.internal_error("Cannot call this when a function is not present!", "locate")

        #if not self.function_namespace:
        #    self.internal_error("Illegal function name!", "locate")

        for i in self.defined["__global__"]:
            if i[2] == pram1:
                return "[%s]" % i[2]

        for i in self.defined[self.function_namespace]:
            if i[2] == pram1:
                return "[ebp%s]" % i[3]
        self.internal_error("Unknown variable namespace!", "locate")
        exit(0)

    def var_exists(self, pram1):
        """ Tests to see if the given variable name exists.
            pram1 = The name of the variable.
        """

        for i in self.defined["__global__"]:
            if i[2] == pram1:
                return True

        for i in self.defined[self.function_namespace]:
            if i[2] == pram1:
                return True

        return False

    def create_string(self, pram1):
        """ Appends a string to the list and returns its label.
            pram1 = The string to create.
        """

        if pram1 in self.strings:
            return "string%d" % self.strings.index(pram1)
        else:
            newstring = ""
            while pram1:
                if ord(pram1[0]) <= 0xFF:

                    # Escape characters are proccessed by the compiler, not by a lib function.
                    if pram1[0] == "\\":

                        # Common escape characters supported.
                        # NOTE: Move this to create_string in parser!
                        if pram1[1] == "0":
                            newstring += "\", 0x00, \"" # BEL # NUL
                        elif pram1[1] == "a":
                            newstring += "\", 0x07, \"" # BEL
                        elif pram1[1] == "b":
                            newstring += "\", 0x08, \"" # BS
                        elif pram1[1] == "t":
                            newstring += "\", 0x09, \"" # HT
                        elif pram1[1] == "n":
                            newstring += "\", 0x0A, \"" # LF
                        elif pram1[1] == "v":
                            newstring += "\", 0x0B, \"" # VT
                        elif pram1[1] == "f":
                            newstring += "\", 0x0C, \"" # FF
                        elif pram1[1] == "r":
                            newstring += "\", 0x0D, \"" # CR
                        elif pram1[1] == "e":
                            newstring += "\", 0x1B, \"" # ESC
                        elif pram1[1] == "\"":
                            newstring += "\", 0x22, \"" # "
                        elif pram1[1] == "\'":
                            newstring += "\", 0x27, \"" # '
                        elif pram1[1] == "\\":
                            newstring += "\", 0x5C, \"" # \
                        else:
                            self.parser_error("Unknown escape character!", self.line)
                            exit(-1)

                        # Remove both characters.
                        pram1 = pram1[2:]

                    # No escape characters; procced as normal.
                    else:
                        newstring += pram1[0]
                        pram1 = pram1[1:]

                else:
                    self.parser_error("Character exceeds the size of a byte!", self.line)
                    exit(-1)

            newstring += ", 0x00"
            self.strings.append(newstring)
            return "string%d" % (len(self.strings)-1)

    def create_label(self):
        """ Creates a relative label.
        """

        self.labels.append(".C%d" % len(self.labels))

        return self.labels[-1]

    def math(self, pram1, completed=False):
        """ This function does the math for parser.
            pram1 = The location of the lexer's list.
        """

        mstr = "" # The string that will be converted to RPN.
        mlist = [] # A list that store all of the RPN expression.
        glob = False
        assign = False

        # data type of (e)ax
        reg_dtype = "INT"

        if not self.datatype:
            self.datatype = "INT"

        # Reduces typing.
        reg = self.reg(self.datatype)
        regb = self.reg_b(self.datatype)
        regc = self.reg_c(self.datatype)
        regd = self.reg_d(self.datatype)

        # See if the variable is global or not.
        if self.function:
            glob = True

        # Already RPN'ized.
        if completed:
            mlist = pram1

        # The first phase extracts the lexer's list and creates a math
        # list. Unlike the lexer's list, there are no sub-lists.

        # Also note that error checking can be used here to prevent too
        # much checking later on.
        while not completed and pram1[0][0] != "INDENT":
            mstr += " %s" % pram1[0][1]
            del pram1[0]

        if not completed:
            mstr = mstr.strip()
            self.out.append("; Infixed: `%s`" % mstr)
            mlist = RPN(mstr)
            self.out.append("; RPN: `%s`" % " ".join(mlist))

            for i in range(len(mlist)):
                if not mlist[i].isdigit() and mlist[i] not in RPN.ops and self.var_exists(mlist[i]):
                    mlist[i] = self.locate(mlist[i])
                elif mlist[i].find("\"") != -1:
                    mlist[i] = self.create_string(mlist[i])
                elif mlist[i] in ("True", "False"):
                    break
                elif not mlist[i].isdigit() and mlist[i] not in RPN.ops and not self.var_exists(mlist[i]):
                    mlist[i] = "func %s" % mlist[i]

            self.out.append("; Expanded RPN: `%s`" % " ".join(mlist))

        mov_set = False
        stack = []

        # This is for handling functions.
        prams = []

        while mlist:
            if mlist and mlist[0] not in RPN.ops:
                if len(mlist) > 1 and (mlist[1] not in RPN.ops or mlist[1] in ("True", "False")) and mov_set:
                    self.out.append("push %s" % reg)
                    stack.append("(")
                    mov_set = False
                elif mlist[0].startswith("func "):
                    # Call math over and over...
                    func = mlist[0][5:]
                    del mlist[0]
                    if mlist[0] != "(":
                        self.parser_error("Expected a starting paratheses!",
                                          self.line)
                        exit(-1)
                    del mlist[0]

                    # A flag to get out of there...
                    count = 1
                    size = 0
                    moretemp = []
                    while count:
                        templist = []
                        size += 4
                        if count and mlist and mlist[0] != ",":
                            moretemp.append(self.dtype(mlist[0]))
                        while count and mlist and mlist[0] != ",":
                            if mlist[0] == "(":
                                count += 1
                            elif mlist[0] == ")":
                                count -= 1
                            if count:
                                templist.append(mlist[0])
                                del mlist[0]
                        del mlist[0]
                        # Do something with the args...
                        if len(templist) > 1:
                            # Actually do something...
                            self.math(templist, True)
                            self.out.append("push eax")
                        else:
                            self.out.append("push dword %s" % templist[0])

                    self.out.append(self.get_function_name(func, moretemp))
                    self.out.append("add esp, %d" % size) # TBD handle typecasting changes!
                    mov_set = True
                else:
                    stack.append(mlist[0])
                    del mlist[0]
            elif len(mlist) > 1 and mlist[0] == "[":
                del mlist[0]
                index_list = []
                while mlist and mlist[0] != "]":
                    index_list.append(mlist[0])
                    del mlist[0]

                del mlist[0]
                self.math(index_list, True)

                # Actually do something. Is this string-biased?
                self.out.append("push %s" % reg)
                self.out.append("push dword %s" % stack[-1])
                self.out.append("call ___strindex")
                self.out.append("add esp, 8")

                del stack[-1]

            else:
                # Make sure ?ax contains the right value.
                if not mov_set:

                    # Get the right stack location.
                    s = 0
                    if "(" in stack:
                        s = stack[::-1].index("(")
                        if len(stack[s:]) > 2:
                            s += 1
                    elif ("=" in mlist or
                          "+=" in mlist or
                          "-=" in mlist or
                          "*=" in mlist or
                          "/=" in mlist or
                          "//=" in mlist or
                          "&=" in mlist or
                          "|=" in mlist or
                          "^=" in mlist or
                          "<<=" in mlist or
                          ">>=" in mlist):
                        s = 1
                    else:
                        s = 0

                    # Find the right one. Is this even needed?
                    for i in range(s, len(stack)):
                        if stack[i] not in RPN.ops:
                            break
                    else:
                        self.parser_error("Math syntax error!", self.line)
                        exit(-1)

                    self.out.append("mov %s, %s" % (reg, stack[i]))
                    del stack[i]
                    mov_set = True


                # ***NOTE: WORK ON STRING SUPPORT!***

                # Actually do what the operator says.
                if mlist[0] == "+" and stack[-1] == "1" and self.datatype == "INT":
                    self.out.append("inc %s" % reg)
                elif mlist[0] == "+" and self.datatype == "INT":
                    self.out.append("add %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "+" and self.datatype == "STRING":
                    if self.dtype(stack[-1]) != "STRING":
                        self.parser_error("Cannot convert '%s' to 'STRING' implicitly." % self.dtype(stack[-1]),
                                          self.line)
                    self.out.append("push dword %s" % stack[-1])
                    self.out.append("push %s" % reg)
                    self.out.append("call ___strcat")
                    self.out.append("add esp, 8")

                elif mlist[0] == "-" and stack[-1] == "1":
                    self.out.append("dec %s" % reg)
                elif mlist[0] == "-":
                    self.out.append("sub %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "*" and self.datatype == "INT":
                    self.out.append("mov %s, %s" % (regd, stack[-1]))
                    self.out.append("mul %s" %  regd)
                elif mlist[0] == "*" and self.datatype == "STRING":
                    if reg_dtype != "INT":
                        self.parser_error("Cannot multiply sequence type 'STRING' by non-int of type '%s'." % self.dtype(stack[-1]),
                                          self.line)
                    self.out.append("push dword %s" % stack[-1])
                    self.out.append("push %s" % reg)
                    self.out.append("call ___striter")
                    self.out.append("add esp, 8")

##                elif mlist[0] == "/":
##                    pass
                elif mlist[0] == "//":
                    self.out.append("xor %s, %s" % (regd, regd))
                    self.out.append("mov %s, %s" % (regc, stack[-1]))
                    self.out.append("div %s" % regc)
                elif mlist[0] == "%":
                    self.out.append("xor %s, %s" % (regd, regd))
                    self.out.append("mov %s, %s" % (regc, stack[-1]))
                    self.out.append("div %s" % regc)
                    self.out.append("mov %s, %s" % (reg, regd))
                elif mlist[0] == "&":
                    self.out.append("and %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "|":
                    self.out.append("or %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "^":
                    self.out.append("xor %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "<<":
                    self.out.append("shl %s, %s" % (reg, stack[-1]))
                elif mlist[0] == ">>":
                    self.out.append("shr %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "=":
                    self.out.append("mov %s, %s" % (stack[-1], reg))
                elif mlist[0] == "+=" and self.datatype == "INT":
                    self.out.append("add %s, %s" % (stack[-1], reg))
                elif mlist[0] == "+=" and self.datatype == "STRING":
                    self.out.append("push %s" % reg)
                    self.out.append("push dword %s" % stack[-1])
                    self.out.append("call ___strcat")
                    self.out.append("add esp, 8")
                    self.out.append("mov %s, %s" % (stack[-1], reg))
                    mlist[0] = "="
                elif mlist[0] == "-=":
                    self.out.append("sub %s, %s" % (stack[-1], reg))
                elif mlist[0] == "*=":
                    self.out.append("mul dword %s" %  stack[-1])
                    self.out.append("mov %s, %s" % (stack[-1], reg))
##                elif mlist[0] == "/=":
                elif mlist[0] == "//=":
                    self.out.append("xor %s, %s" % (regd, regd))
                    self.out.append("mov %s, %s" % (regc, reg))
                    self.out.append("mov %s, %s" % (reg, stack[-1]))
                    self.out.append("div %s" % regc)
                    self.out.append("mov %s, %s" % (stack[-1], reg))
                elif mlist[0] == "&=":
                    self.out.append("and %s, %s" % (stack[-1], reg))
                elif mlist[0] == "|=":
                    self.out.append("or %s, %s" % (stack[-1], reg))
                elif mlist[0] == "^=":
                    self.out.append("xor %s, %s" % (stack[-1], reg))
                elif mlist[0] == "<<=":
                    self.out.append("shl %s, %s" % (stack[-1], reg))
                elif mlist[0] == ">>=":
                    self.out.append("shr %s, %s" % (stack[-1], reg))
##                elif mlist[0] == "<->":
##                    self.out.append("xchg")
##                    self.out.append("mov %s, %s" % (stack[-1], reg))
                elif mlist[0] == "==":
                    self.out.append("mov %s, %s" % (regb, stack[-1]))
                    self.out.append("test %s, %s" % (reg, regb))
                    self.out.append("xor %s, %s" % (reg, reg))
                    self.out.append("lahf")
                    self.out.append("shr %s, 8" % reg)
                    self.out.append("and %s, 3" % reg)
                else:
                    self.internal_error(
                        "An unknown operator was passed to the generator.",
                        "math")
                    exit(-1)

                # Delete this stuff.
                del mlist[0]
                del stack[-1]

                if stack and stack[-1] == "func":
                    del stack[-1]
                # Do we need to pop a value off the stack?
                elif stack and stack[-1] == "(":
                    self.out.append("mov %s, %s" % (regd, reg))
                    self.out.append("pop %s" % reg)
                    stack[-1] = regd

        if len(stack) == 1:
            self.out.append("mov %s, %s" % (reg, stack[-1]))
        elif len(stack) > 0:
            print(stack)
            self.internal_error("A math stack problem has occurred!", "math")
            exit(-1)

        self.out.append("")

if __name__ == "__main__":
    print("This isn't a standalone library!")
