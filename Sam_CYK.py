#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# ----------------------------------------------------------------------------------
# TP Implementation of the algorithme CYK
# Replace "pass" with your code
#
# Don't forget to comment your code and make sure that the output of your program is 
# readable and relevant
#
# The code should be submitted on Moodle before Thursday 2 december 23:59
# ----------------------------------------------------------------------------------

class Symbol:
    # field name: string
    # (no methods)

    def __init__(self, name):
        # name: String

        self.name = name

    def __str__(self):
        return self.name


class Rule:
    # field lhs: Symbol
    # field rhs: list of Symbol
    # (no methods)

    def __init__(self, lhs, rhs):
        # lhs: Symbol (left hand side)
        # rhs: list of Symbol (right hand side)

        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return str(self.lhs) + " --> [" + ",".join([str(s) for s in self.rhs]) + "]"


class Grammar:
    # field symbols: list of Symbol
    # field axiom: Symbol
    # field rules: list of Rule
    # field name: string
    # field nonTerminals: set of Symbol
    # method createNewSymbol: String -> Symbol
    # method isNonTerminal: Symbol -> Boolean

    def __init__(self, symbols, axiom, rules, name):
        # symbols: list of Symbol
        # axiom: Symbol
        # rules: list of Rule
        # name: String

        self.symbols = symbols
        self.axiom = axiom
        self.rules = rules
        self.name = name

        self.nonTerminals = set()
        for rule in rules:
            self.nonTerminals.add(rule.lhs)

    # Returns a new symbol (with a new name build from the argument)
    def createNewSymbol(self, symbolName):
        # symbolName: string

        name = symbolName

        ok = False
        while (ok == False):
            ok = True
            for s in self.symbols:
                if s.name == name:
                    ok = False
                    continue

            if ok == False:
                name = name + "'"

        return Symbol(name)

    def isNonTerminal(self, symbol):
        # symbol: Symbol

        return symbol in self.nonTerminals

    def __str__(self):
        return "{" + \
               "symbols = [" + ",".join([str(s) for s in self.symbols]) + "] " + \
               "axiom = " + str(self.axiom) + " " + \
               "rules = [" + ", ".join(str(r) for r in self.rules) + "]" + \
               "}"

class Tree:
    # field branches: list of length 1 or 2 (only two possibilities in CNF).
    # field label: Symbol
    # (no methods)

    def __init__(self, label, branches):
        self.branches = branches
        self.label = label

    def __str__(self):
        if len(self.branches) == 1:
            return "[ " + self.label.name + ", " + str(self.branches[0]) + " ]"
        else:
            return "[ " + self.label.name + ", " + str(self.branches[0]) + ", " + str(self.branches[1]) + " ]"


# Definition of the symbols
symS = Symbol("S")
symA = Symbol("A")
symB = Symbol("B")
symC = Symbol("C")
#symX = Symbol("X")
symTerminalA = Symbol("a")
symTerminalB = Symbol("b")
symTerminalC = Symbol("c")
# Symbols can of course be added if necessary

# Definition of two grammars

g1 = Grammar(
    # Alphabet
    [symS, symA, symB, symTerminalA, symTerminalB],

    # Axiom
    symS,

    # List of rules
    [
        Rule(symS, [symA, symB]),  # S --> AB
        Rule(symS, [symTerminalA]),  # S --> a
        Rule(symA, [symS, symB]),  # A --> SB
        Rule(symA, [symTerminalB]),  # A --> b
        Rule(symB, [symTerminalB])  # B --> b
    ],

    # name
    "g1"
)

g2 = Grammar(
    # Alphabet
    [symS, symA, symTerminalA, symTerminalB],

    # Axiom
    symS,

    # List of rules
    [
        Rule(symS, [symA, symS]),  # S --> AS
        Rule(symS, [symTerminalB]),  # S --> b
        Rule(symA, [symTerminalA])  # A --> a
    ],

    # name
    "g2"
)


# ----------------------------------------------------------------------
# Minimum version of the CYK algorithm
#
# Let u be a word of length n for 0 =< i < j <= n,
# T[i, j] is the set of non-terminals A such that there exists
# a derivation from A to the subword 'u[i] u[i+1] ... u[j-1]'
# (i.e. A -->* u[i] ... u[j-1])
#
# More details: handout of Yvon et Demaille (2016) P189, algorithm 14.4
# ----------------------------------------------------------------------

print ("Question 1 : Creation of the analysis table\n")

"Creation and initialization of the table T for the word u and the grammar gr"


def init(u, gr):
    T = {}
    # The parse table T is initially empty: T[i, j] = ∅
    for i in range(len(u)):
        for j in range(i, len(u) + 1):
            T[i, j] = set()
    #initialization of the diagonal with the rules that generate a terminal letter
    for i in range(len(u)):
        for rule in gr.rules:                               
            if rule.rhs[0].name == u[i]:                     
                T[i, i+1].add(Tree(rule.lhs, rule.rhs))                 #typecasting 
    return T

"Filling the table T (initialization already done) for the word u and the grammar gr"

# main loop where we look for constituents of increasing length
def loop(T, u, gr):
    for l in range(2, (len(u)+1)):                                      #length of the span        
        for i in range(0, (len(u)-l+1)):                                #beginning, left to right  
            for k in range(i+1, i+l):                                   #latter part of the span, till the end 
                for r in[rule for rule in gr.rules if rule.rhs[0] in gr.nonTerminals]:  #accessing grammar rules 
                    for leftspan in T[i, k]:                               #accessing left of the span 
                        for rightspan in T[k, i+l]:                        #accessing right of the span 
                            if leftspan.label==r.rhs[0] and rightspan.label==r.rhs[1]:
                                branches = [leftspan, rightspan]              #combining the split branches because Tree can accept only two arguments 
                                T[i, i+l].add(Tree(r.lhs, branches))    #typecasting 
    return T                    
            

"Creation of the analysis table of the word u for the grammar gr"

def buildTable(u, gr):
    T = init(u, gr)
    loop(T, u, gr)

    return T


"Display a table T for a word of length n"

def printT(T, n):
    for i in range(n):
        for j in range(i, n + 1):
            print (str((i, j)) + ": " + ", ".join(str(t.label) for t in T[i, j]))

printT(buildTable("bb", g1), 2)


# ----------------------------------------------------------------------
# The algo is entirely coded in the three previous functions,
# The following functions are only used to display the results,
# and to easily perform some tests
# ----------------------------------------------------------------------
print("")
print ("Question 2 : interpretation of the parse table")

"Once the table T is filled, determine if the analysis was successful"

#
def isSuccess(T, u, gr):
    for i in T[0, len(u)]:  
        if gr.axiom == i.label: 
            return True 
    return False


"Once the parse is complete, retrieve and display the syntax tree from the table T"

def printTree(T, u, gr):
     while len(T[0, len(u)]) != 0:
        i = T[0, len(u)].pop()      #since it is a set 
        print(str(i))


"Check that the grammar is in Chomsky Normal Form"
def checkCNF(gr):
    result=True
    for r in gr.rules:
        if len(r.rhs) == 1 and r.rhs[0] not in gr.nonTerminals:
            continue
        elif len(r.rhs) == 2 and r.rhs[0] in gr.nonTerminals and r.rhs[1] in gr.nonTerminals:
            continue
        else: 
            result=False 
    return result


"Global parsing function"
def parse(u, gr):
    print("--- \"" + u + "\" - " + gr.name + " ---")

    if not checkCNF(gr):
        print("The grammar is not in Chomsky Normal Form !")
        return

    T = buildTable(u, gr)

    print("Analysis table :")
    printT(T, len(u))
    print("")

    if isSuccess(T, u, gr):
        print("The word is generated by the grammar")
        print("")

        printTree(T, u, gr)
    else:
        print("The word is NOT generated by the grammar")

parse("abab", g1)
print("")

parse("abb", g1)
print("")

parse("aaab", g2)
print("")

parse("ab", g2)
print("")


"Parse the word abaca with the ambiguous grammar.  Two parsing trees should be displayed"

g3 = Grammar(
    # Alphabet
    [symS, symA, symB, symC, symTerminalA, symTerminalB, symTerminalC],

    # Axiom
    symS,

    # List of rules
    [
        Rule(symS, [symS, symA]),  # S --> SA
        Rule(symS, [symTerminalA]),  # S --> a
        Rule(symA, [symB, symS]),  # A --> BS
        Rule(symA, [symC, symS]),  # A --> CS
        Rule(symB, [symTerminalB]),  # B --> b
        Rule(symC, [symTerminalC])  # C --> c
    ],

    # name
    "g3"
)

parse("abaca", g3)
