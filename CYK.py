'''
By:
Michael Cabot (6047262), Richard Rozeboom (6173292)
'''

import nltk
import sys
import getopt
import ast
import os
import extractPCFG

# TODO do not add trees to parse forest, but add pointers
# as to how the trees can be made
# viterbi will move through forest and create the most 
# probable one	
def makeTrees(string, grammar):
    """Creates parse forest: all possible (sub)trees with probabilities
    for a sentence given a grammar.
    Arguments:
    string      - contains words separated by single whitespace
    grammar - dictionary mapping rhs to lhs
    Return:
    triangleTable   - dictionary mapping span [i,j) to possible subtrees"""
    string = string.strip() # remove whitespace+\n @ start and end 
    triangleTable = {} #triangle table.
    words = string.split(' ')
    # initialize 
    for i in xrange(len(words)): # set terminals in triangle table
        word = words[i]
        for lhs in grammar.get(word, []): # TODO if word not in grammar
            tree = nltk.ProbabilisticTree(lhs[1], [word], prob=lhs[0])
            triangleTable.setdefault((i,i+1), []).append(tree)
            triangleTable[(i,i+1)].extend(extendUnary(tree, grammar)) # extend with unary rules
            
    # expand
    for span in xrange(2, len(words)+1): # loop over spans
        for i in xrange(len(words)-span+1): # loop over sub-spans [i-k), [k-j)
            j = i+span
            for k in xrange(i+1, j): # k splits span [i,j)
                left = triangleTable.get((i,k), [])
                right= triangleTable.get((k,j), [])
                for x in left: # loop over sub-trees with span [i-k)
                    for y in right: # loop over sub-trees with span [k-j)
                        rhs = ','.join([x.node, y.node])
                        for lhs in grammar.get(rhs, []): # expand trees
                            tree = nltk.ProbabilisticTree(lhs[1], [x, y])
                            tree.set_prob(lhs[0] * x.prob() * y.prob())
                            triangleTable.setdefault((i,j), []).append(tree)
                            triangleTable[(i,j)].extend(extendUnary(tree, grammar)) # extend with unary rules
    
    return triangleTable
                    
def extendUnary(tree, grammar):
    """Finds trees that extend a tree with unary rules.
    Arguments:
    tree        - nltk.ProbabilisticTree
    grammar - dictionary mapping rhs to lhs
    Return:
    list    - list of trees that extend 'tree' with unary rules"""
    list = []
    for lhs in grammar.get(tree.node, []):
        if lhs[1]==tree.node:
            continue
        newTree = nltk.ProbabilisticTree(lhs[1], [tree])
        newTree.set_prob(lhs[0] * tree.prob())        
        list.append(newTree)
        list.extend(extendUnary(newTree, grammar))        
    return list
    
                    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:g:s:t:")
    except getopt.GetoptError as e:
        print e
        sys.exit(2) # command line error
        
    trainFileName, grammarFileName = None, None
    testFileName, targetFileName = None, None
    for opt, arg in opts:
        if opt == "-c": # tree corpus
            trainFileName = arg
        elif opt == "-g": # tree grammar
            grammarFileName = arg
        elif opt == "-s": # test sentences
            testFileName = arg
        elif opt == "-t": # target trees for test sentences
            targetFileName = arg
    # read/create grammar
    if not trainFileName and not grammarFileName: # no tree corpus or grammar given
        print "Use '-c <file>' to give a tree corpus or '-g <file>' to give a grammar."
        sys.exit(2)
    elif grammarFileName and \
    extractPCFG.fileExists(grammarFileName): 
        try: # read grammar
            grammarFile = open(grammarFileName, 'r')
            grammar = ast.literal_eval(grammarFile.next().strip()) # read grammar from file
        except (SyntaxError, ValueError):
            print "The file %s does not contain a grammar." %grammarFileName
            sys.exit(2)
    elif trainFileName and \
    extractPCFG.fileExists(trainFileName): 
        grammar = extractPCFG.createGrammar(trainFileName) # create grammar from corpus
        if not grammarFileName: 
            name, extension = os.path.splitext(trainFileName)
            grammarFileName = 'grammar_' + name + extension
            print "The grammar file is saved as: %s" %grammarFileName
        extractPCFG.saveToFile(grammar, grammarFileName) # save grammar
    else: # no tree corpus and no grammar found
        print "The tree corpus '%s' does not exist." %trainFileName
        print "The grammar '%s' does not exist." %grammarFileName
        sys.exit(2)
    # read sentences
    if testFileName and extractPCFG.fileExists(testFileName):
        testFile = open(testFileName, 'r')
        for line in testFile: # read from file
            print line
            triangleTable = makeTrees(line.strip(), grammar)
            for tree in triangleTable.get((0,len(line.split(' '))), []):
                if tree.node=='TOP':
                    print tree
    else:
        print "Enter a sentence. Type 'q' to quit."
        line = None
        while line!='q': # read from stdin
            line = raw_input("Sentence: ")
            triangleTable = makeTrees(line.strip(), grammar)
            for tree in triangleTable.get((0,len(line.split(' '))), []):
                if tree.node=='TOP':
                    print tree
    