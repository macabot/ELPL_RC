'''
By:
Michael Cabot (6047262), Richard Rozeboom (6173292)
'''

import re
import sys
import getopt
import os

def createGrammar(fileName, minTerminalFreq):
    """Creates grammar from tree corpus.
    Arguments:
    fileName        - name of file with tree corpus
    minTerminalFreq - words that have a lower frequency are replaced
    Return:
    grammar     - dictionary that maps rhs to list of p(rule) and lhs"""
    infrequent = infrequentTerminals(fileName, minTerminalFreq)
    lhsFreq, ruleFreq = grammarFreq(fileName, infrequent)
    grammar = {} # {rhs: [(prob, lhs),...],...}
    for rule,freq in ruleFreq.iteritems():
        splitRule = rule.split('~',1)
        prob = float(freq) / lhsFreq[splitRule[0]]
        grammar.setdefault(splitRule[1], []).append((prob, splitRule[0]))
    
    return grammar
      
def grammarFreq(fileName, infrequent=set([])):
    """Count the frequency of all the grammar rules and 
    left-hand-sides in a file.
    Arguments:
    fileName    - name of file with tree corpus
    infrequent  - set of infrequent terminals
    Return:
    lhsFreq     - dictionary mapping left-hand-side to its frequency
    ruleFreq    - dictionary mapping grammar rule to its frequency"""
    file = open(fileName, 'r')
    lhsFreq = {} # left hand side frequency
    ruleFreq = {} # rule frequency
    for line in file:
        rules = extractRules(line, infrequent) # get rules in tree 
        for rule in rules:
            lhs = rule.split('~',1)[0]
            lhsFreq[lhs] = lhsFreq.get(lhs, 0) + 1
            ruleFreq[rule] = ruleFreq.get(rule, 0) + 1
            
    return lhsFreq, ruleFreq
        
def extractRules(string, infrequent=set([])):
    """Extracts rules from parse tree.
    Arguments:
    string  - parse tree
    infrequent  - infrequent terminals in this set will be replace by 'XXXUNKNOWNXXX'
    Return:
    rules   - list of rules that make up the parse tree"""
    string = string.strip() # remove whitespace+\n @ start and end
    stack = ['TOP'] # contains unfinished rules
    string = string[5:len(string)-1] # remove TOP from string
    rules = [] # rules in tree
    while len(string) > 0:        
        if string[0]==')':
            rules.append(stack.pop())
            string = string[1:] # remove ')'
        else:
            leftBracket = string[0]=='('
            if leftBracket:
                string = string[1:] # remove '('
            word, string = getFirstWord(string)
            if not leftBracket and word in infrequent:
                word = 'XXXUNKNOWNXXX' # replace infrequent terminal
            stack[len(stack)-1] += '~' + word
            if leftBracket:
                stack.append(word) 
            
        string = string.lstrip() # remove whitespaces from start
        
    rules.append(stack.pop()) # add TOP rule to rules
    return rules

def infrequentTerminals(fileName, minTerminalFreq):
    """Find the set of terminals that occur infrequently in a file.
    Arguments:
    fileName        - name of file with tree corpus
    minTerminalFreq - words that have a lower frequency are replaced
    Return:
    set of infrequent terminals"""
    file = open(fileName, 'r')
    terminalCount = terminalFreq(file)    
    infrequent = set([]) # set of infrequent terminals
    for terminal, freq in terminalCount.iteritems():
        if freq < minTerminalFreq:
            infrequent.add(terminal)
    
    return infrequent
    
def terminalFreq(file):
    """Count the frequency of all the terminals in a file.
    Arguments:
    file            - file with tree corpus
    Return:
    terminalFreq    - dictionary mapping terminal to its frequency"""
    terminalFreq = {} # terminal frequency
    for line in file:
        terminals = extractTerminals(line)
        for t in terminals:
            terminalFreq[t] = terminalFreq.get(t, 0)+1
    return terminalFreq
    
def extractTerminals(string):
    """Extracts terminals from parse tree.
    Arguments:
    string  - parse tree
    Return:
    rules   - list of terminals in the parse tree"""
    string = string.strip() # remove whitespace+\n at start and end
    terminals = [] # terminals in tree
    while len(string) > 0:        
        if string[0]==')':
            string = string[1:] # remove ')'
        else:
            leftBracket = string[0]=='('
            if leftBracket:
                string = string[1:] # remove '('
            word, string = getFirstWord(string)
            if not leftBracket:
                terminals.append(word)     
			
        string = string.lstrip() # remove whitespaces from start
        
    return terminals

def getFirstWord(string):
    """Get first word of partially parsed parse tree
    Arguments:
    string  - partially parsed parse tree
    Return:
    word    - first substring excluding ')' and whitespace
    string  - 'string' after removing 'word'"""
    word = re.search('[^)\s]+', string).group(0)
    string = string.replace(word, '', 1) # remove first occurence
    return word, string
    
def saveToFile(element, fileName, verbose=True):
    """Saves an object to file. If file already exists, file
    can be overwritten or new name can be given.
    Arguments:
    element     - object that is written to file
    fileName    - name of file"""
    if verbose and fileExists(fileName):
        print "Your are about to overwrite %s\n" \
            "y\t\t- To overwrite the file.\n" \
            "<new name>\t- To change the name." %fileName
        input = raw_input()
        if input!='y':
            fileName = input
            
    file = open(fileName, 'w')
    file.write(str(element))
    file.close()
    
def fileExists(fileName):
    """Checks whether a file exists.
    Arguments:
    fileName    - name of the file
    Return: 
    True, if file exists, else False"""
    try:
        with open(fileName) as f: return True
    except IOError:
        return False
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:g:")
    except getopt.GetoptError as e:
        print e
        sys.exit(2) # command line error
    
    trainFileName, grammarFileName = None, None
    for opt, arg in opts:
        if opt == "-c":
            trainFileName = arg
        elif opt == "-g":
            grammarFileName = arg
    
    if not trainFileName:
        print "Use '-c <file>' to give a tree corpus."
        sys.exit(2)
    elif not fileExists(trainFileName):
        print "The tree corpus '%s' does not exist." %trainFileName
        sys.exit(2)
    elif not grammarFileName:
        name, extension = os.path.splitext(trainFileName)
        grammarFileName = 'grammar_' + name + extension
        print "The grammar file is saved as: %s" %grammarFileName
    
    minTerminalFreq = 5 # minimal frequency of terminal. if lower, then replace by 'XXXUNKNOWNXXX'
    grammar = createGrammar(trainFileName, minTerminalFreq)
    saveToFile(grammar, grammarFileName)