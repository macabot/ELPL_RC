ELPL_RC
=======
By Richard Rozeboom and Michael Cabot.

Task:
- create grammar from tree corpus
- create parse forest for sentence with CYK
- create most probable parse with Viterbi

extractPCFG.py
=======

Takes command line arguments:
- -c [corpus]   : name of file with tree corpus
- -g [grammar]  : grammar is saved with this name

If grammar name is omitted, then file name is: 
'grammar_' + [corpus file]

CYK.py
=======
Takes command line arguments:
- -c [corpus]   : name of file with tree corpus       
- -g [grammar]  : grammar is saved with this name
- -s [sentences]: sentences that will be parsed with grammar

if a grammar is given, then it is used. If not, then one
is made using the corpus and saved. If sentence file is not 
given, then sentences must be given with stdin.

viterbi.py
=======
Takes command line arguments:
- -c [corpus]   : name of file with tree corpus       
- -g [grammar]  : grammar is saved with this name
- -s [sentences]: sentences that will be parsed with grammar
- -p [parses]   : name of file that parses are to be written to

if a grammar is given, then it is used. If not, then one
is made using the corpus and saved. If sentence file is not 
given, then sentences must be given with stdin. If sentence
file is given, then resulting parse trees are written to
parses file. If grammar name is omitted, then file name is:
'parses_' + [sentences]