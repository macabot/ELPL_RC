
import ast
import CYK

if __name__=="__main__":
    grammarFile = open('grammar_debugTrainData.txt', 'r')
    grammar = ast.literal_eval(grammarFile.next().strip())
    testString = open('debugTestData.txt', 'r').next().strip()
    print testString
    triangleTable = CYK.makeTrees(testString, grammar)
    for tree in triangleTable[(0,len(testString.split(' ')))]:
        print tree
        tree.draw()