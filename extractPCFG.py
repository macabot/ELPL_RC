'''
By:
Michael Cabot (6047262), Richard Rozeboom (6173292)
'''

import re
import sys
import getopt
import os

def createGrammar(fileName, minTerminalFreq):
    """Creates grammar from corpus.
    Arguments:
    fileName    - name of file with tree corpus
    Return:
    grammar     - dictionary that maps rhs to lhs"""
    stringFile = preprocess(fileName, minTerminalFreq)
    lhsFreq, ruleFreq, _ = grammarFreqs(stringFile)    
    
    grammar = {} # {rhs: [(prob, lhs),...],...}
    for rule,freq in ruleFreq.iteritems():
        splitRule = rule.split('~',1)
        prob = float(freq) / lhsFreq[splitRule[0]]
        grammar.setdefault(splitRule[1], []).append((prob, splitRule[0]))
    
    return grammar

def smoothGrammar(minTerminalFreq, terminalFreq):
    for terminal, freq in terminalFreq.iteritems():
        if freq <= minTerminalFreq:
            temp = grammar[terminal]
            del grammar[terminal]
            grammar.setdefault('XXXUNKNOWNXXX', []).extend(temp)
        
def preprocess(fileName, minTerminalFreq):
    file = open(fileName, 'r')
    stringFile = file.read()
    _, _, terminalFreq = grammarFreqs(file)
    for terminal, freq in terminalFreq.iteritems():
        if freq <= minTerminalFreq:
            stringFile = stringFile.replace(' '+terminal+')',' XXXUNKNOWNXXX)')
    saveToFile(stringFile,'replace')
    return stringFile.split('\n')
    
    
def grammarFreqs(file):
    lhsFreq = {} # left hand side frequency
    ruleFreq = {} # rule frequency
    terminalFreq = {} # terminal frequency
    for line in file:
        rules = extractRules(line, terminalFreq) # get rules in tree 
        for rule in rules:
            lhs = rule.split('~',1)[0]
            lhsFreq[lhs] = lhsFreq.get(lhs, 0) + 1
            ruleFreq[rule] = ruleFreq.get(rule, 0) + 1
            
    return lhsFreq, ruleFreq, terminalFreq
    
def extractRules(string, terminalFreq):
    """Extracts rules from parse tree.
    Arguments:
    string  - parse tree
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
            stack[len(stack)-1] += '~' + word
            if leftBracket:
                stack.append(word) 
            else:
                terminalFreq[word] = terminalFreq.get(word, 0) + 1
			
        string = string.lstrip() # remove whitespaces from start
        
    rules.append(stack.pop()) # add TOP rule to rules
    return rules

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
    
def saveToFile(element, fileName):
    """Saves an object to file. If file already exists, file
    can be overwritten or new name can be given.
    Arguments:
    element     - object that is written to file
    fileName    - name of file"""
    if fileExists(fileName):
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
    
    grammar = createGrammar(trainFileName, 5)
    saveToFile(grammar, grammarFileName)