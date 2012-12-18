ELPL_RC
=======
By Richard Rozeboom (6173292) and Michael Cabot (6047262).

Task:
- create grammar from tree corpus
- create parse forest for sentence with CYK
- create most probable parse with Viterbi

Three python files are given:
- extractPCFG.py
- CYK.py
- viterbi.py

Dependencies
=======

- python 2.7 : http://www.python.org/
- nltk : http://nltk.org/

nltk is a large package and may take a while to import into python.

extractPCFG.py
=======
Creates a PCFG from a tree corpus. The PCFG is 
represented by a dictionary that maps the right-hand-side of
a production rule to all possible left-hand-sides along with the
probability of each rule. When creating the grammar, all words that
occur less than 5 times in the corpus are replaced with the unique
symbol 'XXXUNKNOWNXXX'. This way an unknown word can be treated as if
it is this symbol.

Takes command line arguments:
- -c [corpus] : name of file with tree corpus
- -g [grammar] : grammar is saved with this name

If grammar name is omitted, then file name is: 
'grammar_' + [corpus file]

CYK.py
=======
Creates a parse forest for a sentence given a corpus. The parse forest
is represented by a dictionary that maps a span [i,j) to a dictionary
mapping parents to their left and right child. Each parent represents
a partial derivation of the sentence. The probability of these parents
are kept in a separate dictionary mapping a node in a span to its
probability.

Takes command line arguments:
- -c [corpus] : name of file with tree corpus       
- -g [grammar] : grammar is saved with this name
- -s [sentences] : sentences that will be parsed with grammar

If a grammar is given, then it is used. If not, then one
is made using the corpus and saved. If sentence file is not 
given, then sentences must be given with stdin.

viterbi.py
=======
Creates the most probable derivation of a sentence.

Takes command line arguments:
- -c [corpus] : name of file with tree corpus       
- -g [grammar] : grammar is saved with this name
- -s [sentences] : sentences that will be parsed with grammar
- -p [parses] : name of file that parses are to be written to

If a grammar is given, then it is used. If not, then one
is made using the corpus and saved. If sentence file is not 
given, then sentences must be given with stdin. If sentence
file is given, then resulting parse trees are written to
parses file. If parse name is omitted, then file name is:
'parses_' + [sentences]

grammar_minFreq5_wsj.02-21.training.nounary
=======
A grammar created from the train data. All words that occurred less
than 5 times were replaced with 'XXXUNKNOWNXXX'.