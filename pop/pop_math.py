from pop.pop_rpn import *

class Math():
    """This class contains the math praser for the Pop compiler."""

    def __init__(self):
        # Define the x86 registers.
        self.reg = {"a": "eax",
                    "b": "ebx",
                    "c": "ecx",
                    "d": "edx"}

        # List of registers and their contents.
        self.type = {"a": "",
                     "b": "",
                     "c": "",
                     "d": ""}

        # A list of values on the *real* stack.
        self.reg_stack = []

        # A list of op functions.
        self.ops = {"*": self.mul,
                    "/": None,
                    "//": self.fdiv,
                    "%": self.mod,
                    "+": self.add,
                    "-": self.sub,
                    "<<": None,
                    ">>": None,
                    "==": None,
                    "!=": None,
                    "&": self.bin_and,
                    "^": self.bin_xor,
                    "|": self.bin_or,
                    "=": self.equal,
                    "+=": self.equal_add,
                    "-=": self.equal_sub,
                    "*=": self.equal_mul,
                    "/=": None,
                    "//=": self.equal_fdiv,
                    "%=": None,
                    "<<=": None,
                    ">>=": None,
                    "&=": None,
                    "^=": None,
                    "|=": None}

        # An assembly list to return to the parser.
        self.out = []

    def math(self, pparser, mlist, complete=True):
        """This is the main method for Math.
           pparser = The current parser class that's passed.
           mlist = The location of the lexer's list.
           complete = True if mlist is already parsered!
        """

        if not complete:
            mlist = self.parser(pparser, mlist)

        stack = []

        # Let's do something with mlist.
        while mlist:
            # For debug purposes.
            #print("{} <-> {}".format(mlist, stack))

            if mlist[0] in self.ops:
                self.ops[mlist[0]](mlist, stack)
                del mlist[0]

            # Create a function to handle... functions.
            elif mlist[0].startswith("func "):
                func = mlist[0][5:]
                del mlist[0]

                temp = []
                count = 1
                size = 0
                tempd = []

                if mlist[0] == "(":
                    del mlist[0]
                    if mlist[0] != ")":
                        tempd.append(pparser.dtype(mlist[0]))

                while count:
                    if mlist[0] == "(":
                        count += 1
                    elif mlist[0] == ")":
                        count -= 1

                    if mlist[0] == "," or (mlist[0] == ")" and not count):
                        self.out.extend(Math().math(pparser, temp, True))
                        self.out.append("push {}".format(self.reg["a"]))
                        size += 4
                        temp = []
                        if len(mlist) != 1 and mlist[1] != ")":
                            tempd.append(pparser.dtype(mlist[1]))
                    else:
                        temp.append(mlist[0])

                    del mlist[0]

                self.out.append("call {}".format(
                    pparser.get_function_name(func, tempd)))

                if size:
                    self.out.append("add esp, {!s}".format(size))

                self.out.append("")

            else:
                if not self.type["a"]:
                    self.type["a"] = pparser.dtype(mlist[0])
                    if len(mlist) == 1:
                        self.out.append("mov {}, {}".format(self.reg["a"],
                                                            mlist[0]))
                    else:
                        self.out.append("mov {}, {}".format(self.reg["a"],
                                                            mlist[1]))
                        del mlist[1]

                # Add to the stack!
                stack.append(mlist[0])
                del mlist[0]

        return self.out

    def parser(self, pparser, mlist):
        """This method parsers a math list created by the lexer.
           pparser = The current parser class that's passed.
           mlist = The location of the lexer's list.
        """

        mlist = RPN(self.format_mlist(mlist))

        temp_mlist = []

        for i in range(len(mlist)):
            if not mlist[i]:
                pass
            elif (mlist[i] == "." and
                  mlist[i-1].startswith("[ebp") and
                  pparser.vtype(
                      pparser.vlocate(mlist[i-1][4:-1])) in pparser.structs):

                # Sloppy, but usable structure support.
                temp_mlist.append("[ebp{}+{}.{}]".format(
                    mlist[i-1][4:-1],
                    pparser.vtype(pparser.vlocate(mlist[i-1][4:-1])),
                    mlist[i+1]))

                del temp_mlist[-2]
                mlist[i+1] = None

            elif (mlist[i] == "." and
                  mlist[i-1].startswith("[ebp") and
                  pparser.vtype(
                      pparser.vlocate(mlist[i-1][4:-1])) in pparser.classes):

                self.out.append("mov ebx, {}".format(mlist[i-1]))
                self.type["b"] = mlist[i-1]

                # Sloppy, but usable method support.
                if [x for x in pparser.classes[
                    pparser.dtype(pparser.vlocate(mlist[i-1][4:-1]))] if
                    x.startswith(mlist[i+1])]:
                    temp_mlist.append("func [ebx+{}.{}]".format(
                        pparser.dtype(mlist[i-1]),
                        mlist[i+1]))
                elif mlist[i+1] in pparser.classes[pparser.dtype(pparser.vlocate(
                    mlist[i-1][4:-1]))]["__global__"]:
                    temp_mlist.append("[ebx+_class_{}.{}]".format(
                        pparser.dtype(pparser.vlocate(mlist[i-1][4:-1])),
                        mlist[i+1]))
                else:
                    pparser.parser_error("`{}` isn't a class method or a class"
                                      " variable!".format(mlist[i+1]),
                                      self.line)
                    exit()

                del temp_mlist[-2]
                mlist[i+1] = None

            elif mlist[i] == "@":
                # Make sure @ is used correctly!
                if not (mlist[i-1].startswith("[ebp") and
                        mlist[i-1].endswith("]")):
                    pparser.parser_error("Incorrect use of the @ operator!",
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
                  pparser.var_exists(mlist[i])):
                temp_mlist.append(pparser.locate(mlist[i]))
                mlist[i] = temp_mlist[-1]

            elif mlist[i].find("\"") != -1:
                temp_mlist.append(pparser.create_string(mlist[i]))
                mlist[i] = temp_mlist[-1]

            elif (not mlist[i].isdigit() and
                  mlist[i] not in RPN.ops and
                  not pparser.var_exists(mlist[i])):
                temp_mlist.append("func {}".format(mlist[i]))
                mlist[i] = temp_mlist[-1]

            else:
                temp_mlist.append(mlist[i])

        mlist = temp_mlist

        # Remove all None types now that we're out of a loop.
        mlist = [i for i in mlist if i is not None]

        self.out.append("; Expanded RPN: `%s`" % " ".join(mlist))

        return mlist

    def format_mlist(self, mlist):
        """This method turns the lexer's list into the math's list.
           mlist = The location of the lexer's list.
        """

        mstr = ""
        while mlist[0][0] != "INDENT":
            mstr += " {}".format(mlist[0][1])
            del mlist[0]

        return mstr.strip()

    def mul(self, mlist, stack):
        if self.type["a"] == "INT":
            self.out.append("mov %s, %s" % (regd, stack.pop()))
            self.out.append("mul %s" % regd)
        elif self.type["a"] == "STRING":
            self.out.append("push dword %s" % stack.pop())
            self.out.append("push %s" % reg)
            self.out.append("call ___striter")
            self.out.append("add esp, 8")

    def fdiv(self, mlist, stack):
        self.out.append("xor {0}, {0}".format((self.reg["d"])))
        self.out.append("mov {}, {}".format(self.reg["c"], stack.pop()))
        self.out.append("div {}".format(self.reg["c"]))

    def mod(self, mlist, stack):
        self.out.append("xor {0}, {0}".format((self.reg["d"])))
        self.out.append("mov {}, {}".format(self.reg["c"], stack.pop()))
        self.out.append("div {}".format(self.reg["c"]))
        self.out.append("mov {}, {}".format(self.reg["a"], self.reg["d"]))

    def add(self, mlist, stack):
        if stack[-1] == "1":
            self.out.append("inc {}".format(self.reg["a"]))
            del stack[-1]
        else:
            self.out.append("add %s, %s" % (self.reg["a"], stack.pop()))

    def sub(self, mlist, stack):
        if stack[-1] == "1":
            self.out.append("dec {}".format(self.reg["a"]))
            del stack[-1]
        else:
            self.out.append("sub %s, %s" % (self.reg["a"], stack.pop()))

    def bin_and(self, mlist, stack):
        self.out.append("and {}, {}".format(self.reg["a"], stack.pop()))

    def bin_xor(self, mlist, stack):
        self.out.append("xor {}, {}".format(self.reg["a"], stack.pop()))

    def bin_or(self, mlist, stack):
        self.out.append("or {}, {}".format(self.reg["a"], stack.pop()))

    def equal(self, mlist, stack):
        self.out.append("mov {}, {}".format(stack.pop(), self.reg["a"]))

    def equal_add(self, mlist, stack):
        if self.type["a"] == "INT":
            self.out.append("add {}, {}".format(stack.pop(), self.reg["a"]))
        elif self.type["a"] == "STRING":
            self.out.append("push {}".format(self.reg["a"]))
            self.out.append("push dword {}".format(stack[-1]))
            self.out.append("call ___strcat")
            self.out.append("add esp, 8")
            self.out.append("mov {}, {}".format(stack.pop(), self.reg["a"]))

    def equal_sub(self, mlist, stack):
        self.out.append("sub {}, {}".format(stack.pop(), self.reg["a"]))

    def equal_mul(self, mlist, stack):
        self.out.append("mul dword {}".format(stack[-1]))
        self.out.append("mov {}, {}".format(stack.pop(), self.reg["a"]))

    def equal_fdiv(self, mlist, stack):
        self.out.append("xor {0}, {0}".format(self.reg["d"]))
        self.out.append("mov {}, {}".format(self.reg["c"], self.reg["a"]))
        self.out.append("mov {}, {}".format(self.reg["a"], stack[-1]))
        self.out.append("div {}".format(self.reg["c"]))
        self.out.append("mov {}, {}".format(stack.pop(), self.reg["a"]))
