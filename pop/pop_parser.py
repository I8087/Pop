# Notice the word 'we' in my comments... obvious signs of insanity...

import pop
from pop.pop_rpn import *
from collections import OrderedDict

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
                    "; Compiled using version {} of the Pop Compiler!".format(
                        pop.__version__),
                    "",
                    "%define True 1",  # Define this in a header.
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

        # This holds a list of all the global structures.
        self.structs = OrderedDict()

        # This holds a list of current structure indentations.
        self.current_structs = []

        # Setup class values.
        self.cls = False  # NOTE: Cannot be self.class
        self.class_namespace = "__global__"

        # Ordered dictionary help with class building!
        self.classes = OrderedDict([("__global__",
                                     OrderedDict([("__global__",
                                                   OrderedDict())]))])
        # Setup function values.
        self.function = False
        self.function_signed = False
        self.function_datatype = ""
        self.function_namespace = "__global__"
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

        self.mathpop = []

    def parser(self, pram1, pram2, pram3, pram4, pram5={"__global__": []}):
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

            elif pram1[0][0] == "NAMESPACE" and pram1[0][1] == "CLASS":
                self.do_class(pram1)

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

            elif (pram1[0][0] == "DATATYPE" or
                  pram1[0][1] in self.structs or
                  pram1[0][1] in self.classes):

                # It can be assumed that this datatype isn't signed.
                self.signed = False

                # Assign the datatype.
                self.datatype = pram1[0][1]

                if self.function and self.datatype == "LONG":
                    self.location -= 8
                elif self.function and self.datatype in self.classes:
                    self.location -= 4

                elif self.function and self.datatype in self.structs:
                    l = 0
                    for i in self.structs[self.datatype]:
                        if i["datatype"] == "LONG":
                            l += 8
                        elif i["datatype"] == "INT":
                            l += 4
                        elif i["datatype"] == "SHORT":
                            l += 4  # 2
                        elif i["datatype"] == "BYTE":
                            l += 4  # 1
                        else:
                            self.parser_error("Unknown datatype in the "
                                              "structure `{}`!".format(
                                                  self.datatype),
                                              self.line)

                    # Make sure everything is aligned by a dword.
                    self.location -= l + (4-l % 4)

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

                # NOTE: WORK HERE!

                # Add this variable into the defined dictionary
                # for later static reference.
                if self.function:
                    self.classes[self.class_namespace][
                        self.function_namespace][self.namespace] = {
                        "signed": self.signed,
                        "datatype": self.datatype,
                        "location": "{!s}".format(self.location)}

                elif not self.function and self.current_structs:
                    self.structs[self.current_structs[-1]].append({
                        "signed": self.signed,
                        "datatype": self.datatype,
                        "namespace": self.namespace})
                else:
                    self.classes[self.class_namespace][
                        "__global__"][self.namespace] = {
                            "signed": self.signed,
                            "datatype": self.datatype,
                            "location": ""}

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

                if pram1[0][1] in self.classes[self.class_namespace][
                        self.function_namespace]:

                    self.namespace = pram1[0][1]

                    if pram1[0][1] == "self":
                        self.signed = False
                        self.datatype = self.class_namespace
                    else:
                        self.signed = self.classes[self.class_namespace][
                            self.function_namespace][pram1[0][1]]["signed"]

                        self.datatype = self.classes[self.class_namespace][
                            self.function_namespace][pram1[0][1]]["datatype"]

                    if (self.dtype(pram1[0][1]) in self.classes and
                        [x for x in self.classes[self.dtype(pram1[0][1])] if x.startswith(pram1[2][1])]):
                        i = 0
                        while True:
                            if pram1[i][1] == "(":
                                #pram1.insert(i+1, ["OPERATOR", "@"])
                                pram1.insert(i+1, ["NAMESPACE", pram1[0][1]])
                                if pram1[i+2][1] != ")":
                                    pram1.insert(i+2, ["OPERATOR", ","])
                                break
                            elif pram1[i][0] == "INDENT":
                                break
                            i += 1

                    self.math(pram1)

                else:
                    self.parser_error("Variable `%s` is undefined!" %
                                      pram1[0][1], self.line)
                    return []

            # This is needed after every line or there's an error!
            # Ensures that there's no garbage at the end of the code!
            if pram1[0][0] == "INDENT":
                self.line += 1
                self.if_done = False
                self.indent_level = pram1[0][1]
                del pram1[0]
                self.do_indent(pram1)
            else:
                self.parser_error("Unknown garbage at the end of the line!",
                                  self.line)
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

                # Reverse the variables.
                self.structs[i] = self.structs[i][::-1]

                # Write the variables to the output.
                for x in self.structs[i]:
                    self.out.insert(self.out_offset,
                                    "{:>4}.{}: {} 0".format(
                                        " ",
                                        x["namespace"],
                                        self.res_shrink(x["datatype"])))

                # Don't forget the structures name!
                self.out.insert(self.out_offset, "struc {}".format(i))

        for i in self.classes:
            if i == "__global__":
                continue

            self.out.insert(self.out_offset, "")
            self.out.insert(self.out_offset, "endstruc")

            tempcls = tuple(self.classes[i].keys())[::-1]

            for x in tempcls:
                if x == "__global__":
                    for a in self.classes[i]["__global__"]:
                        self.out.insert(self.out_offset,
                                        "    .{}: {} 1".format(a,
                                            self.res_shrink(self.classes[i][
                                                "__global__"][a]["datatype"])))
                else:
                    self.out.insert(self.out_offset,
                                    "    ._{0}@{1}: resd 1".format(
                                        x,
                                        self.function_size(x, cls=i)))

            # Don't forget the structures name!
            self.out.insert(self.out_offset, "struc _class_{}".format(i))

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
            for i in self.classes["__global__"]["__global__"]:
                self.out.append("%s: %s 0" % (i,
                                              self.shrink(i["datatype"])))
            for i in self.strings:
                self.out.append("string%d: db %s" % (n, i))
                n += 1

        for i in range(len(self.out)):
            if not self.out[i].endswith(":"):
                self.out[i] = "{:>4}{}".format("", self.out[i]).rstrip()

                # Excessive line breaks are flagged.
                if (i > 0 and
                    self.out[i] == ""and
                    (self.out[i-1] == "" or
                     self.out[i-1].endswith(":"))):
                    self.out[i] = None

        # Excessive line breaks are now removed. :D
        self.out = [i for i in self.out if i is not None]

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
                if pram1[0][1] != ":":
                    found = True
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
            self.parser_error("Need an if statement before an else statement!",
                              self.line)
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
                if pram1[0][1] != ":":
                    found = True
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
                self.parser_error("An error has occurred within a function's "
                                  "parmeters.", self.line)
                exit()

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

        if func not in self.classes[self.class_namespace]:
            self.classes[self.class_namespace][func] = OrderedDict()
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
        temp_list = {}

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

                temp_list[pram1[1][1]] = {
                    "signed": False,
                    "datatype": pram1[0][1],
                    "location": "+%d" % dec}

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
                elif pram1[0][1] == "PTR8":
                    temp += "_PB"                
                elif pram1[0][1] == "PTR16":
                    temp += "_PS"
                elif pram1[0][1] == "PTR32":
                    temp += "_PI"
                elif pram1[0][1] == "PTR64":
                    temp += "_PL"
                    dec += 4

                dec += 4

                # Get rid of the namespace and data type tokens.
                del pram1[0]
                del pram1[0]

            else:
                self.parser_error("An error has occurred within a function's "
                                  "parameters.", self.line)
                exit()

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

        if func not in self.classes[self.classes_namespace]:
            self.classes[self.classes_namespace][func] = temp_list
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
            self.parser_error("Expected a data type for the function!",
                              self.line)

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

            # This is a local variable that isn't the same as self.location!
            location = 8

            temp_list = {}

            # Classes have a special class variable.
            if self.class_namespace != "__global__":
                    temp_list["self"] = {"signed": False,
                                         "datatype": self.class_namespace,
                                         "location": "+%d" % location}
                    location += 4

            while (pram1[0][0] != "OPERATOR") and (pram1[0][1] != ")"):
                if (pram1[0][0] == "INDENT"):
                    self.parser_error("Expected a closing parenthese!",
                                      self.line)
                    exit()
                elif (pram1[0][0] == "DATATYPE" and
                      pram1[1][0] == "NAMESPACE"):

                    # No need to check for duplicates; the lexer handles that.
                    temp_list[pram1[1][1]] = {"signed": False,
                                              "datatype": pram1[0][1],
                                              "location": "+%d" % location}

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
                    self.parser_error("An error has occurred within a "
                                      "function's parameters.", self.line)
                    exit()

                # A comma is expected after ever prameter,
                # unless it is the end of prameters.
                if pram1[0][0] == "OPERATOR" and pram1[0][1] == ",":
                    del pram1[0]
                elif pram1[0][0] == "OPERATOR" and pram1[0][1] != ")":
                    self.parser_error("Expected a comma!", self.line)
                    exit()

            # Delete the ')'
            del pram1[0]

            if (pram1[0][0] != "OPERATOR") or (pram1[0][1] != ":"):
                self.parser_error("Expected a colon at the end of the "
                                  "function", self.line)
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
            elif i == "PTR8":
                temp += "_PB"
            elif i == "PTR16":
                temp += "_PS"
            elif i == "PTR32":
                temp += "_PI"
            elif i == "PTR64":
                temp += "_PL"

        if not temp:
            temp = "_E"

        self.function_namespace += temp

        # Define a list for the compiler to keep track of
        # all of the variables within the function!
        self.classes[self.class_namespace][self.function_namespace] = temp_list

        # New temp.
        if self.class_namespace == "__global__":
            temp = "_{}@{!s}:".format(self.function_namespace, location-8)
        else:
            temp = "._{}@{!s}:".format(self.function_namespace, location-8)

        self.out.append(temp)
        self.out.append("push ebp")
        self.out.append("mov ebp, esp")
        self.function_line = len(self.out)
        self.out.append("")

    def do_class(self, pram1):
        """This function implements the compilers class compiling.
           pram1 = A list of tokens.
        """

        if self.cls:
            parser_error("Cannot define a class within a class!",
                         self.line)

        # Delete this namespace.
        del pram1[0]

        self.cls = True
        self.class_namespace = pram1[0][1]

        # Setup the class in the classes list.
        if self.class_namespace in self.classes:
            self.parser_error("You cannot redefine a class!", self.line)
            exit(1)

        self.classes[self.class_namespace] = OrderedDict([("__global__", OrderedDict())])

        # Delete the class's namespace.
        del pram1[0]

        # Setup the class's indentation.
        self.indent.append(["CLASS_NEXT", self.indent_level])

        if (pram1[0][0] != "OPERATOR") or (pram1[0][1] != ":"):
            self.parser_error("Expected a colon at the end of the class!",
                              self.line)
            exit()

        # Delete the colon.
        del pram1[0]

        self.out.append("{}:".format(self.class_namespace))
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

        elif (len(self.indent) != 0 and
              self.indent_level == self.indent[-1][1]):
            return

        elif (self.indent[-1][0] == "CLASS_NEXT" and
              self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("CLASS", self.indent_level))

        elif (self.indent[-1][0] == "FUNCTION_NEXT" and
              self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("FUNCTION", self.indent_level))

        elif (self.indent[-1][0] == "STRUCT_NEXT" and
              self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("STRUCT", self.indent_level))

        elif (self.indent[-1][0] == "WHILE_NEXT" and
              self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("WHILE", self.indent_level))

        elif (self.indent[-1][0] == "IF_NEXT" and
              self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("IF", self.indent_level))

        elif (self.indent[-1][0] == "ELSE_NEXT" and
              self.indent_level > self.indent[-1][1]):
            del self.indent[-1]
            self.indent.append(("ELSE", self.indent_level))

        elif self.indent[-1][0] == "FUNCTION":

            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1]  # Delete it now.

                pram1.insert(0, ["INDENT", -1])

                if self.location != 0:
                    self.out.insert(self.function_line,
                                    "sub esp, %d" % (abs(self.location)))
                    self.out.insert(self.function_line+1, "")

                # Append this leaving code for the function.
                self.do_return(pram1)
                self.out.append("")

                # Reset the function parameters.
                self.function = False
                self.function_signed = False
                self.function_datatype = ""
                self.function_namespace = "__global__"
                self.function_prams = []
                self.cons = []
                self.labels = []

                # Reset the location.
                self.location = 0
                self.function_line = -1

        elif self.indent[-1][0] == "CLASS":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)

            self.classes[self.class_namespace]["__new___E"] = OrderedDict()

            # If __init__() doesn't exist, added it!
            if "__init___E" not in self.classes[self.class_namespace]:
                self.classes[self.class_namespace]["__init___E"] = \
                {"self": {"signed": False,
                          "datatype": self.class_namespace,
                          "location": "+8"}}

                self.out.append(".___init___E@4:")
                self.out.append("push ebp")
                self.out.append("mov ebp, esp")
                self.out.append("")
                self.out.append("xor eax, eax")
                self.out.append("mov esp, ebp")
                self.out.append("pop ebp")
                self.out.append("ret")
                self.out.append("")

            x = 0

            for i in self.classes[self.class_namespace]:
                if i != "__global__":
                    x += 4
                else:
                    for n in self.classes[self.class_namespace]["__global__"]:
                        n = self.classes[self.class_namespace]["__global__"][
                            n][ "datatype"]
                        if n == "BYTE":
                            x += 1
                        elif n == "SHORT":
                            x += 2
                        elif n == "INT" or n.startswith("PTR"):
                            x += 4
                        elif n == "LONG":
                            x += 8
                        else:
                            self.internal_error(
                                "Unknown datatype in class field!",
                                "do_indent")

            self.out.append(".___new___E@0:")
            self.out.append("push ebp")
            self.out.append("mov ebp, esp")
            self.out.append("sub esp, 4")
            self.out.append("")

            # Allocate the the class!
            self.out.append("push dword {!s}".format(x))
            self.out.append("call ___malloc")
            self.out.append("add esp, 4")
            self.out.append("")

            self.out.append("mov ebx, eax")
            self.out.append("")

            for i in self.classes[self.class_namespace]:
                if i != "__global__":
                    self.out.append("mov dword [ebx+_class_{3}._{1}"
                                    "@{2}], {3}._{1}@{2}".format(
                                         self.location,
                                         i,
                                         self.function_size(
                                             i,
                                             cls=self.class_namespace),
                                         self.class_namespace))

            self.out.append("mov [ebp-4], eax")
            self.out.append("push eax")
            self.out.append("call dword [ebx+_class_{}.___init___E@4]".format(
                self.class_namespace))
            self.out.append("add esp, 4")
            self.out.append("")

            self.out.append("mov eax, [ebp-4]")
            self.out.append("mov esp, ebp")
            self.out.append("pop ebp")
            self.out.append("ret")
            self.out.append("")

            del self.indent[-1]  # Delete it now.

            # Reset the class parameters.
            self.cls = False
            self.class_namespace = "__global__"

        elif self.indent[-1][0] == "STRUCT":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)

            del self.indent[-1]  # Delete it now.

            # Clean up.
            del self.current_structs[-1]

        elif self.indent[-1][0] == "WHILE":
            if self.indent[-1][1] < self.indent_level:
                self.parser_error("Indentation error!", self.line)
                exit(1)
            else:
                del self.indent[-1]  # Delete it now.

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
                del self.indent[-1]  # Delete it now.

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
                del self.indent[-1]  # Delete it now.

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
                self.parser_error("An `empty` cannot return anything!",
                                  self.line)
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
        """This function displays an error message caused by the programmer's
           code, not the compiler.
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

    def get_function_name(self, pram1, pram2, cls="__global__"):
        """This function returns a decorated function name.
           pram1 = An undecorated function name.
           pram2 = A list of each parameter's data type.
        """

        # The number of bytes to use in the decorator.
        size = 0

        # Create a shallow copy of self.function!
        funcs = self.classes[cls].copy()

        # Check to see if this function exists.
        for func in funcs:
            if func.startswith(pram1):
                break
            funcs[func] = None
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
            elif i == "PTR8":
                temp += "_PB"
            elif i == "PTR16":
                temp += "_PS"
            elif i == "PTR32":
                temp += "_PI"
            elif i == "PTR64":
                temp += "_PL"
                dec += 4

            dec += 4

        if not temp:
            temp = "_E"

        temp_list = []

        # Test to see if this function exists...
        for func in funcs:
            if (func.startswith(pram1) and
               func.endswith("@{!s}".format(dec))) or func.startswith(pram1):
                temp_list.append(func[:])

        if not temp_list:
            self.parser_error("This function's parameters are wrong!",
                              self.line)
            exit(-1)

        temp2 = ""

        # Strictly for type casting. Fix it up.
        if "%s%s" % (pram1, temp) not in self.classes[cls]:
            for i in range(len(temp)//2):
                x = temp[i*2+1]
                y = ""
                # (Probably) broken code. Keep an eye on it.
                for t in temp_list:
                    t = t[t.find("_")+1:]
                    if t[0] == "PB" and not y:
                        y = "PB"
                    elif t[0] == "PS" and not y:
                        y = "PS"
                    elif t[0] == "PI" and not y:
                        y = "PI"
                    elif t[0] == "PL" and not y:
                        y = "PL"
                    elif t[0] == "G" and not y:
                        y = "G"
                    elif t[0] == "A" and not y:
                        y = "A"
                    elif t[0] == "B" and (x == "B" and not y):
                        y = "B"
                    elif t[0] == "S" and (x == "S" and not y and y != "B"):
                        y = "S"
                    elif t[0] == "I" and (x == "I" and not y and y not in ("B",
                                                                           "S")
                                          ):
                        y = "I"
                    # Longs aren't supported yet.
                if not y:
                    y = x
                temp2 += "_%s" % y
            temp = temp2

        if pram1 in self.classes[cls]:
            return "_%s@%d" % (pram1, dec)
        else:
            return "_%s%s@%d" % (pram1, temp, dec)

    def function_size(self, pram1, cls="__global__"):
        size = 0

        for i in self.classes[cls][pram1]:
            if "-" in self.classes[cls][pram1][i]["location"]:
                continue

            if self.classes[cls][pram1][i]["datatype"] == "LONG":
                size += 8
            else:
                size += 4

        return size

    def shrink(self, pram1):
        """ Turns a datatype like 'BYTE' into asm datatypes, like 'db'.
            pram1 = Datatype to shrink.
        """
        if pram1 in ("BYTE", "BOOL"):
            return "db"
        elif pram1 == "SHORT":
            return "dw"
        elif pram1 in ("INT", "STRING") or pram1.startswith("PTR"):
            return "dd"
        elif pram1 == "LONG":
            return "dq"
        else:
            self.internal_error("An unknown data type was passed.", self.line)
            exit()

    def res_shrink(self, pram1):
        """ Turns a datatype like 'BYTE' into asm uninitialized datatypes,
            like 'resb'.
            pram1 = Datatype to shrink.
        """
        if pram1 in ("BYTE", "BOOL"):
            return "resb"
        elif pram1 == "SHORT":
            return "resw"
        elif pram1 in ("INT", "STRING") or pram1.startswith("PTR"):
            return "resd"
        elif pram1 == "LONG":
            return "resq"
        else:
            self.internal_error("An unknown data type was passed.", self.line)
            exit()

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

        if (pram1 == "BYTE" or
            pram1 == "BOOL" or
                (pram1.startswith("PTR") and self.options["BIT"] == 8)):
            return "al"
        elif (pram1 == "SHORT" or
              (pram1.startswith("PTR") and self.options["BIT"] == 16)):
            return "ax"
        elif (pram1 == "INT" or
              (pram1 == "STRING" and self.options["BIT"] == 32) or
              pram1 in self.structs or
              pram1 in self.classes or
              (pram1.startswith("PTR") and self.options["BIT"] == 32)):
            return "eax"
        elif (pram1 == "LONG" and
              (pram1.startswith("PTR") and self.options["BIT"] == 64)):
            return "rax"
        elif pram1 == "EMPTY":
            return "eax"
        else:
            self.internal_error("An unknown datatype was passed.", "reg")
            exit()

    def reg_b(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'bl'.
            pram1 = Datatype to shrink.
        """

        # Get the ?a? version of the register.
        r = self.reg(pram1)

        # If a ?a? register is returned, convert it to ?b?.
        if r:
            r = r.replace("a", "b")

        # Return the ?b? register.
        return r

    def reg_c(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'cl'.
            pram1 = Datatype to shrink.
        """

        # Get the ?a? version of the register.
        r = self.reg(pram1)

        # If a ?a? register is returned, convert it to ?c?.
        if r:
            r = r.replace("a", "c")

        # Return the ?c? register.
        return r

    def reg_d(self, pram1):
        """ Turns a datatype like 'BYTE' into an aligned register, like 'al'.
            pram1 = Datatype to shrink.
        """

        # Get the ?a? version of the register.
        r = self.reg(pram1)

        # If a ?a? register is returned, convert it to ?d?.
        if r:
            r = r.replace("a", "d")

        # Return the ?d? register.
        return r

    def size(self, pram1):
        """ Turns a datatype like 'INT' into an aligned register, like 'dword'.
            pram1 = Datatype to shrink.
        """
        if pram1 == "BYTE" or pram1 == "BOOL":
            return "byte"
        elif pram1 == "SHORT":
            return "word"
        elif (pram1 == "INT" or
              (pram1 == "STRING" and self.options["BIT"] == 32) or
              pram1 in self.structs):
            return "dword"
        elif pram1 == "LONG":
            return "qword"
        else:
            self.internal_error("An unknown datatype was passed.", "size")
            exit(0)

    def dtype(self, pram1, cls=""):
        """ Finds the datatype of a variable.
            pram1 = The name of the variable.
        """

        if not cls:
            cls = self.class_namespace

        if (pram1.startswith("[") and
                pram1.endswith("]")):
            pram1 = pram1[1:-1]

        if pram1 in ("eax", "ebx", "ecx", "edx"):
            return pram1

        if pram1 in self.classes[cls]:
            return pram1

        for i in self.classes[cls]["__global__"]:
            if i == pram1:
                return self.classes[cls][
                    "__global__"][i]["datatype"]            

        for i in self.classes[cls][self.function_namespace]:
            if i == pram1:
                return self.classes[cls][
                    self.function_namespace][i]["datatype"]

        if pram1.startswith("string"):
            return "PTR8"

        if pram1.isdigit():
            return "INT"

        if pram1 in ("True", "False"):
            return "BOOL"

        if (pram1.startswith("ebp") or
            pram1.startswith("ebx")):
            if pram1.strip() in ("ebp", "ebx"):
                return "INT"
            elif "." in pram1 and "+" in pram1:
                pram1 = pram1.split("+")[-1].split(".")
                return self.dtype(pram1[1], cls=pram1[0][7:])
            else:
                return self.vtype(self.vlocate(pram1[3:]))

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
            self.internal_error("An unknown number size was passed.",
                                "num_dtype")

    def locate(self, pram1):
        """ Finds the location of a stack-based variable.
            pram1 = The name of the variable.
        """

        for i in self.classes["__global__"]["__global__"]:
            if i == pram1:
                return "[%s]" % i

        for i in self.classes[self.class_namespace][self.function_namespace]:
            if i == pram1:
                return "[ebp%s]" % self.classes[self.class_namespace][
                    self.function_namespace][i]["location"]

        self.internal_error("Unknown variable namespace!", "locate")
        exit(0)

    def vlocate(self, pram1):
        """ Finds the variable of a stack-based location.
            pram1 = The location.
        """

        for i in self.classes[self.class_namespace][self.function_namespace]:
            if pram1 == self.classes[self.class_namespace][
                    self.function_namespace][i]["location"]:
                return i

        self.internal_error("Unknown stack location!", "vlocate")
        exit(0)

    def vtype(self, pram1):
        """ Finds datatype of a variable.
            pram1 = The location.
        """

        if self.function:
            for i in self.classes[self.class_namespace][
                    self.function_namespace]:
                if pram1 == i:
                    return self.classes[self.class_namespace][
                        self.function_namespace][i]["datatype"]
        return ""


    def var_exists(self, pram1):
        """ Tests to see if the given variable name exists.
            pram1 = The name of the variable.
        """

        for i in self.classes[self.class_namespace][self.function_namespace]:
            if i == pram1:
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

                    # Escape characters are proccessed by the compiler,
                    # not by a Python function.
                    if pram1[0] == "\\":

                        # Common escape characters supported.
                        # NOTE: Move this to create_string in parser!
                        if pram1[1] == "0":
                            newstring += "\", 0x00, \""  # NUL
                        elif pram1[1] == "a":
                            newstring += "\", 0x07, \""  # BEL
                        elif pram1[1] == "b":
                            newstring += "\", 0x08, \""  # BS
                        elif pram1[1] == "t":
                            newstring += "\", 0x09, \""  # HT
                        elif pram1[1] == "n":
                            newstring += "\", 0x0A, \""  # LF
                        elif pram1[1] == "v":
                            newstring += "\", 0x0B, \""  # VT
                        elif pram1[1] == "f":
                            newstring += "\", 0x0C, \""  # FF
                        elif pram1[1] == "r":
                            newstring += "\", 0x0D, \""  # CR
                        elif pram1[1] == "e":
                            newstring += "\", 0x1B, \""  # ESC
                        elif pram1[1] == "\"":
                            newstring += "\", 0x22, \""  # "
                        elif pram1[1] == "\'":
                            newstring += "\", 0x27, \""  # '
                        elif pram1[1] == "\\":
                            newstring += "\", 0x5C, \""  # \
                        else:
                            self.parser_error("Unknown escape character!",
                                              self.line)
                            exit(-1)

                        # Remove both characters.
                        pram1 = pram1[2:]

                    # No escape characters; procced as normal.
                    else:
                        newstring += pram1[0]
                        pram1 = pram1[1:]

                else:
                    self.parser_error("Character exceeds the size of a byte!",
                                      self.line)
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

        self.out.extend(pop.Math().math(self, pram1, completed))
        return

        mstr = ""  # The string that will be converted to RPN.
        mlist = []  # A list that store all of the RPN expression.
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

        # Datatypes for current registers, including those on the stack.
        typea = []
        typeb = []
        typec = []
        typed = []

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

            temp_mlist = []

            for i in range(len(mlist)):
                if not mlist[i]:
                    pass
                elif (mlist[i] == "." and
                      mlist[i-1].startswith("[ebp") and
                      self.vtype(
                          self.vlocate(mlist[i-1][4:-1])) in self.structs):

                    # Sloppy, but usable structure support.
                    temp_mlist.append("[ebp{}+{}.{}]".format(
                        mlist[i-1][4:-1],
                        self.vtype(self.vlocate(mlist[i-1][4:-1])),
                        mlist[i+1]))

                    del temp_mlist[-2]
                    mlist[i+1] = None

                elif (mlist[i] == "." and
                      mlist[i-1].startswith("[ebp") and
                      self.vtype(
                          self.vlocate(mlist[i-1][4:-1])) in self.classes):

                    self.out.append("mov ebx, {}".format(mlist[i-1]))
                    typeb.append(mlist[i-1])

                    # Sloppy, but usable method support.
                    if [x for x in self.classes[
                        self.dtype(self.vlocate(mlist[i-1][4:-1]))] if
                        x.startswith(mlist[i+1])]:
                        temp_mlist.append("func [ebx+{}.{}]".format(
                            self.dtype(mlist[i-1]),
                            mlist[i+1]))
                    elif mlist[i+1] in self.classes[self.dtype(self.vlocate(
                        mlist[i-1][4:-1]))]["__global__"]:
                        temp_mlist.append("[ebx+_class_{}.{}]".format(
                            self.dtype(self.vlocate(mlist[i-1][4:-1])),
                            mlist[i+1]))
                    else:
                        self.parser_error("`{}` isn't a class method or a class"
                                          " variable!".format(mlist[i+1]),
                                          self.line)
                        exit()

                    del temp_mlist[-2]
                    mlist[i+1] = None

                elif mlist[i] == "@":
                    # Make sure @ is used correctly!
                    if not (mlist[i-1].startswith("[ebp") and
                            mlist[i-1].endswith("]")):
                        self.parser_error("Incorrect use of the @ operator!",
                                          self.line)
                        exit(-1)

                    # Get the address of the variable,
                    # even if it's stack-based!
                    mlist[i-1] = mlist[i-1].lstrip("[").rstrip("]")
                    del temp_mlist[-1]
                    temp_mlist.append("ebp")
                    temp_mlist.append(mlist[i-1][4:])
                    temp_mlist.append(mlist[i-1][3:4])

                elif (not mlist[i].isdigit() and
                      mlist[i] not in RPN.ops and
                      self.var_exists(mlist[i])):
                    temp_mlist.append(self.locate(mlist[i]))
                    mlist[i] = temp_mlist[-1]

                elif mlist[i].find("\"") != -1:
                    temp_mlist.append(self.create_string(mlist[i]))
                    mlist[i] = temp_mlist[-1]

                elif (not mlist[i].isdigit() and
                      mlist[i] not in RPN.ops and
                      not self.var_exists(mlist[i])):
                    temp_mlist.append("func {}".format(mlist[i]))
                    mlist[i] = temp_mlist[-1]

                else:
                    temp_mlist.append(mlist[i])

            mlist = temp_mlist

            # Remove all None types now that we're out of a loop.
            mlist = [i for i in mlist if i is not None]

            self.out.append("; Expanded RPN: `%s`" % " ".join(mlist))

        mov_set = False
        stack = []

        # This is for handling functions.
        prams = []

        while mlist:
            if mlist and mlist[0] not in RPN.ops:
                if (len(mlist) > 1 and
                    (mlist[1] not in RPN.ops or
                     mlist[1] in ("True", "False"))
                    and mov_set):
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
                        if count and mlist and mlist[0] == ")":
                            count -= 1
                        if count and mlist and mlist[0] != ",":
                            if mlist[0] == "ebp":
                                moretemp.append(self.dtype("{}{}{}".format(
                                    mlist[0],
                                    mlist[2],
                                    mlist[1])))
                            elif mlist[0].startswith("func"):
                                moretemp.append(mlist[0])
                            elif count == 1:
                                moretemp.append(self.dtype(mlist[0]))
                            size += 4

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

                        # Old code is this really needed anymore?
                        elif templist and templist[0].startswith("ebp"):
                            self.out.append("mov eax, ebp")
                            if "+" in templist[0]:
                                self.out.append("add eax, {}".format(
                                    templist[0][4:]))
                            else:
                                self.out.append("sub eax, {}".format(
                                    templist[0][4:]))
                            self.out.append("push eax")
                        elif templist:
                            self.out.append("push dword %s" % templist[0])

                    if "." in func:
                        self.out.append("call [ebx+_class_{}.{}]".format(
                            func[5:].split(".")[0],
                            self.get_function_name(func.split(".")[1][:-1],
                                                   moretemp,
                                                   cls=func[5:].split(".")[0])
                                        ))
                    elif func in self.classes:
                        self.out.append("call {}.___new___E@0".format(func))
                    else:
                        self.out.append("call {}".format(
                            self.get_function_name(func, moretemp)))
                    if size:
                        # TBD handle typecasting changes!
                        self.out.append("add esp, %d" % size)
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

                if self.dtype(stack[-1]) == "STRING":
                    self.out.append("push %s" % reg)
                    self.out.append("push dword %s" % stack[-1])
                    self.out.append("call ___strindex")
                    self.out.append("add esp, 8")
                elif self.dtype(stack[-1]).startswith("PTR"):

                    # Factor in pointer offsets.
                    if self.dtype(stack[-1]).endswith("16"):
                        self.out.append("mov {}, 2".format(regd))
                    if self.dtype(stack[-1]).endswith("32"):
                        self.out.append("mov {}, 4".format(regd))
                    if self.dtype(stack[-1]).endswith("64"):
                        self.out.append("mov {}, 8".format(regd))
                    if not self.dtype(stack[-1]).endswith("8"):
                        self.out.append("mul {}".format(regd))

                    #self.out.append("push {}".format(regb))
                    #typeb.append(stack[-1])

                    # WORK!!!
                    self.out.append("add {}, {}".format(reg, stack[-1]))
                    self.out.append("")
                    if "=" in mlist and mov_set:
                        # movsx!!!
                        self.out.append("mov {}, {}".format(regb, reg))
                        self.out.append("mov al, [{}]".format(regb))
                        self.out.append("movsx {}, al".format(reg))
                        self.out.append("pop {}".format(regb))
                        self.out.append("mov [{}], al".format(regb))
                    else:
                        mlist.insert(0, "[eax]")
                        self.out.append("push eax")
                        self.out.append("")
                else:
                    self.parser_error("Indexing error!", self.line)
                    exit()

                typea.append(self.dtype(stack[-1]))

                # Remove the closing bracket.
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

                    # PLACE HOLDER!!!
                    typea.append(self.dtype(stack[i]))
                    self.out.append("mov %s, %s" % (reg, stack[i]))
                    del stack[i]
                    mov_set = True

                # ***NOTE: WORK ON STRING SUPPORT!***

                # Actually do what the operator says.
                if (mlist[0] == "+" and
                    stack[-1] == "1" and
                        self.datatype == "INT"):
                    self.out.append("inc %s" % reg)
                elif mlist[0] == "+" and self.datatype != "STRING":
                    self.out.append("add %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "+" and self.dtype(stack[-1]) == "STRING":
                    self.out.append("push dword %s" % stack[-1])
                    self.out.append("push %s" % reg)
                    self.out.append("call ___strcat")
                    self.out.append("add esp, 8")

                elif mlist[0] == "-" and stack[-1] == "1":
                    self.out.append("dec %s" % reg)
                elif mlist[0] == "-":
                    self.out.append("sub %s, %s" % (reg, stack[-1]))
                elif mlist[0] == "*" and typea[-1] == "INT":
                    self.out.append("mov %s, %s" % (regd, stack[-1]))
                    self.out.append("mul %s" % regd)
                elif mlist[0] == "*" and typea[-1] == "STRING":
                    if reg_dtype != "INT":
                        self.parser_error("Cannot multiply sequence type "
                                          "'STRING' by non-int of type "
                                          "'%s'." % self.dtype(stack[-1]),
                                          self.line)
                    self.out.append("push dword %s" % stack[-1])
                    self.out.append("push %s" % reg)
                    self.out.append("call ___striter")
                    self.out.append("add esp, 8")
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
                    self.out.append("mul dword %s" % stack[-1])
                    self.out.append("mov %s, %s" % (stack[-1], reg))
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
            #print(stack)
            self.internal_error("A math stack problem has occurred!", "math")
            exit(-1)

        #for i in typeb:
        #    self.out.append("pop {}".format(regb))

        self.out.append("")

if __name__ == "__main__":
    print("This isn't a standalone library!")
