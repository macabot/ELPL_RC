'''
By:
Michael Cabot (6047262), Richard Rozeboom (6173292)
'''

#import nltk
import sys
import getopt
import ast
import extractPCFG

def makeForest(string, grammar):
    """Creates parse forest: all possible (sub)trees with probabilities
    for a sentence given a grammar.
    Arguments:
    string      - contains words separated by single whitespace
    grammar     - dictionary mapping rhs to [(P(rule_1), lhs_1), ..., (P(rule_n), lhs_n)]
    Return:
    parseForest - dictionary mapping span [i,j) to entries (parent, left-child, right-child, k)
    probs       - dictionary mapping (node, i, j) to P(node)"""
    string = string.strip() # remove whitespace+\n @ start and end 
    parseForest = {} # condenses all possible parse tree
    probs = {} # holds probability of each entry in 'parseForest'
    words = string.split(' ')
    # initialize 
    for i in xrange(len(words)): # set terminals in triangle table
        word = words[i]
        for lhs in grammar.get(word, []): # TODO if word not in grammar
            entry = (lhs[1], word, None, i+1) # parent, left-child, _right-child, _k
            parseForest.setdefault((i,i+1), set([])).add(entry)
            probs[(lhs[1], i, i+1)] = lhs[0]
            extendUnary(entry, grammar, parseForest, probs, i, i+1) # extend with unary rules            
            
    # expand
    for span in xrange(2, len(words)+1): # loop over spans
        for i in xrange(len(words)-span+1): # loop over sub-spans [i-k), [k-j)
            j = i+span
            for k in xrange(i+1, j): # k splits span [i,j)
                left = parseForest.get((i,k), [])
                right= parseForest.get((k,j), [])
                for x in left: # loop over sub-trees with span [i-k)
                    for y in right: # loop over sub-trees with span [k-j)
                        rhs = '~'.join([x[0], y[0]])
                        for lhs in grammar.get(rhs, []): # expand trees
                            entry = (lhs[1], x[0], y[0], k) # parent, left-child, right-child, k
                            probEntry = lhs[0]*probs[(x[0], i,k)]*probs[(y[0],k,j)]
                            if probs.get((lhs[1], i, j), -1) < probEntry:
                                parseForest.setdefault((i,j), set([])).add(entry)
                                probs[(lhs[1], i, j)] = probEntry
                                extendUnary(entry, grammar, parseForest, probs, i, j) # extend with unary rules                               
    
    return parseForest, probs
                    
def extendUnary(entry, grammar, parseForest, probs, i, j):
    """Finds entries that extend a tree with unary rules.
    Arguments:
    entry       - (parent, left-child, _right-child, _k)
    grammar     - dictionary mapping rhs to lhs
    parseForest - dictionary mapping span [i,j) to entries
    probs       - dictionary mapping (node, i, j) to P(node)
    i           - left index of span (inclusive)
    j           - right index of span (exclusive)"""
    for lhs in grammar.get(entry[0], []):
        if lhs[1]==entry[0]: # prevent X->X
            continue
        newEntry = (lhs[1], entry[0], None, j)
        parseForest[(i,j)].add(newEntry)
        probs[(lhs[1], i, j)] = lhs[0] * probs[(entry[0], i, j)]
        extendUnary(newEntry, grammar, parseForest, probs, i, j)
                    
if __name__ == "__main__":
    # TODO if given -c and -g then don't ignore -c, but create a new grammar using
    # -c and save as -g
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:g:s:")
    except getopt.GetoptError as e:
        print e
        sys.exit(2) # command line error
        
    corpusFileName, grammarFileName = None, None
    testFileName = None
    for opt, arg in opts:
        if opt == "-c": # tree corpus
            corpusFileName = arg
        elif opt == "-g": # tree grammar
            grammarFileName = arg
        elif opt == "-s": # test sentences
            testFileName = arg
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
            parseForest, probs = makeForest(line.strip(), grammar)
            for entry in parseForest.get((0,len(line.split(' '))), []):
                if entry[0]=='TOP':
                    print entry
    else:
        print "Enter a sentence. Type 'q' to quit."
        line = raw_input("Sentence: ")
        while line!='q': # read from stdin
            parseForest, probs = makeForest(line.strip(), grammar)
            for entry in parseForest.get((0,len(line.split(' '))), []):
                if entry[0]=='TOP':
                    print entry
            line = raw_input("Sentence: ")
    