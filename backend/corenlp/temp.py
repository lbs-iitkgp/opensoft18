import os
from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP(r'stanford-corenlp-full-2018-02-27')

sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
print('Tokenize:', nlp.pos_tag(sentence))

nlp.close()
