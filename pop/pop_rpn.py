class RPN():
    """An infix to postfix convert speceially made for thePop Compiler."""

    def __init__(self):
        pass

    def __new__(self, code="", verbose=False, func=False):
        outstack = []
        opstack = []
        instack = []

        # Dictionary that defines each operators, which points to a list where:
        # The first is the precendece level where 1 is the highest.
        # The second is a Boolean that's true if the operaator
        # is right associative.

        # TBD: Tuple the values.
        self.ops = {"(":   [1, False],
                    ")":   [1, False],
                    "[":   [1, False],
                    "]":   [1, False],
                    ",":   [1, False],
                    "@":   [2, True],
                    "*":   [3, False],
                    "/":   [3, False],
                    "//":  [3, False],
                    "%":   [3, False],
                    "+":   [3, False],
                    "-":   [3, False],
                    "<<":  [5, False],
                    ">>":  [5, False],
                    "==":  [6, False],
                    "!=":  [6, False],
                    "&":   [8, False],
                    "^":   [9, False],
                    "|":   [10, False],
                    "=":   [15, True],
                    "+=":  [15, True],
                    "-=":  [15, True],
                    "*=":  [15, True],
                    "/=":  [15, True],
                    "//=": [15, True],
                    "%=":  [15, True],
                    "<<=": [15, True],
                    ">>=": [15, True],
                    "&=":  [15, True],
                    "^=":  [15, True],
                    "|=":  [15, True]}

        # Flag if a variable was right before another token.
        var = False

        # A parameter stack.
        prams = []

        # Turn the string into a proper input_stack.
        while code:

            # If there is some spaces, remove them.
            if code[0] == " ":
                code = code.lstrip()

            # Like below, except it handles three character operators.
            elif code[:3] in self.ops:
                instack.append(code[:3])
                code = code[3:]

            # Like below, except it handles two character operators.
            elif code[:2] in self.ops:
                instack.append(code[:2])
                code = code[2:]

            # If this is an operator, then add it.
            elif code[0] in self.ops:
                instack.append(code[0])
                code = code[1:]

            elif code[0] == "\"":
                instack.append(code[0:code.find("\"", 1)+1])
                code = code[code.find("\"", 1)+1:]

            # This is a number literal, string literal, or namespace.
            else:
                instack.append(code[0])
                code = code[1:]
                while code and code[0] not in self.ops and code[0] != " ":
                    instack[-1] += code[0]
                    code = code[1:]

        # Important FLAG.
        size = -1

        # Now convert to RPN.
        for i in instack:

            size += 1

            # A verbose way of displaying the stacks.
            if verbose:
                print(outstack, "<->", opstack)
            # If this is a number of variable, then add it to the outstack.
            if i not in self.ops:
                var = True
                outstack.append(i)

            # If this is an operator,
            # than some complex stuff needs to be done...
            elif (i in self.ops and i not in ("(", ")", "[", "]", ",")):

                # TBD Add right associative support.
                if (opstack and
                    opstack[-1] not in ("(", ")", "[", "]") and
                    ((not self.ops[i][1] and
                      self.ops[i][0] >= self.ops[opstack[-1]][0]) or
                     (self.ops[i][1] and
                      self.ops[i][0] > self.ops[opstack[-1]][0]))):

                    outstack.append(opstack[-1])
                    opstack[-1] = i
                else:
                    opstack.append(i)

                var = False

            elif i == ",":
                outstack.extend(opstack)
                prams.append(outstack)
                opstack = []
                outstack = []

            elif i == "[":
                outstack.append("[")

            elif i == "]":
                while (opstack and
                       opstack[-1] != i
                       and self.ops[opstack[-1]][0] < 15):
                    outstack.append(opstack[-1])
                    del opstack[-1]

                outstack.append("]")

            elif i == "(":
                # Push operator onto the stack.
                if not var:
                    opstack.append(i)

                # A function has been found!
                else:
                    templist = []
                    count = 1
                    del instack[size]
                    while instack and count:
                        if instack[size] == "(":
                            count += 1
                        elif instack[size] == ")":
                            count -= 1
                        if count:
                            templist.append(instack[size])
                            del instack[size]
                    templist = RPN(" ".join(templist),
                                   verbose=verbose,
                                   func=True)
                    outstack.append("(")
                    outstack.extend(templist)
                    outstack.append(")")

                var = False

            # Pop everything off the opstack into
            # the outstack until a "(" is found.
            elif i == ")":

                # Well... i is now inverted.
                i = "("

                while opstack[-1] != i:
                    outstack.append(opstack[-1])
                    del opstack[-1]
                    if not opstack:
                        print("Error! Expected a leading \"(\"!" % i)
                        exit(-1)
                # Only delete the parenthesis.
                del opstack[-1]

                var = False

        # Pop everything off the opstack into the outstack.
        for i in opstack[::-1]:
            if i in ("(", "["):  # Switch them around for the error message.
                print("Error! Expected an ending \"%s\"!" % i)
                exit(-1)
            outstack.append(i)
        opstack = []

        # Display the RPN as a string if verbose if true.
        if verbose:
            print(" ".join(outstack))

        if func:
            outstack.extend(opstack)
            prams.append(outstack)
            opstack = []
            outstack = []
            for pram in prams[::-1]:
                outstack.extend(pram)
                outstack.append(",")

            if outstack[-1] == ",":
                del outstack[-1]

        return outstack
