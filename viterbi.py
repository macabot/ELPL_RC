'''
By:
Michael Cabot (6047262), Richard Rozeboom (6173292)
'''

import nltk.tree
import sys
import getopt
import ast
import CYK
import extractPCFG


def mostProbableTree(string, grammar):
    parseForest, probs = CYK.makeForest(string, grammar)
    j = len(string.split())
    return viterbi(parseForest, probs, 0, j)
    
def viterbi(parseForest, probs, i, j, node='TOP', repeat=False):
    entry = maxEntry(parseForest[(i,j)], probs, i, j, node) # parent, left-child, right-child, k
    if not entry or repeat:
        return node
    if entry[1]==node and entry[2]==None: #X->X only allowed once
        repeat = True
    else:
        repeat = False
    leftChild = viterbi(parseForest, probs, i, entry[3], entry[1], repeat)
    if entry[2]: # if binary rule
        rightChild = viterbi(parseForest, probs, entry[3], j, entry[2], repeat)
        return nltk.Tree(entry[0], [leftChild, rightChild])
    else: # if unary rule
        return nltk.Tree(entry[0], [leftChild])
        
def maxEntry(entries, probs, i, j, node):
    bestEntry = None
    bestProb = -1
    for entry in entries:
        if entry[0]==node and bestProb < probs[(entry[0], i, j)]:
            bestEntry = entry
            bestProb = probs[(entry[0], i, j)]
    return bestEntry

if __name__ == "__main__":
    # TODO if given -c and -g then don't ignore -c, but create a new grammar using
    # -c and save as -g
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:g:s:t:")
    except getopt.GetoptError as e:
        print e
        sys.exit(2) # command line error
        
    corpusFileName, grammarFileName = None, None
    testFileName, targetFileName = None, None
    for opt, arg in opts:
        if opt == "-c": # tree corpus
            corpusFileName = arg
        elif opt == "-g": # tree grammar
            grammarFileName = arg
        elif opt == "-s": # test sentences
            testFileName = arg
        elif opt == "-t": # target trees for test sentences
            targetFileName = arg
    # read/create grammar
    if not corpusFileName and not grammarFileName: # no tree corpus or grammar given
        print "Use '-c <file>' to give a tree corpus or '-g <file>' to give a grammar."
        sys.exit(2)
    elif corpusFileName: 
        if not extractPCFG.fileExists(corpusFileName):
            print "The tree corpus '%s' does not exist." %corpusFileName
            sys.exit(2)
        grammar = extractPCFG.createGrammar(corpusFileName) # create grammar from corpus
        if not grammarFileName: 
            grammarFileName = 'grammar_' + corpusFileName
            print "The grammar file is saved as: %s" %grammarFileName
        extractPCFG.saveToFile(grammar, grammarFileName) # save grammar
    elif grammarFileName:
        if not extractPCFG.fileExists(grammarFileName):
            print "The grammar '%s' does not exist." %grammarFileName
            sys.exit(2)
        try: # read grammar
            grammarFile = open(grammarFileName, 'r')
            grammar = ast.literal_eval(grammarFile.next().strip()) # read grammar from file
        except (SyntaxError, ValueError):
            print "The file %s does not contain a grammar." %grammarFileName
            sys.exit(2)    
    # read sentences
    if testFileName:
        if not extractPCFG.fileExists(testFileName):
            print "The file '%s' does not exist." %testFileName
            sys.exit(2)
        testFile = open(testFileName, 'r')
        for line in testFile: # read from file
            print line
            print mostProbableTree(line, grammar)            
    else:
        print "Enter a sentence. Type 'q' to quit."
        line = raw_input("Sentence: ")
        while line!='q': # read from stdin
            bestTree = mostProbableTree(line, grammar)
            print bestTree
            bestTree.draw()            
            line = raw_input("Sentence: ")