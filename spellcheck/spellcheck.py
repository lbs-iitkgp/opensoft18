#!/usr/bin/python3
# spellcheck.py

import re
from collections import Counter
from sys import argv

dicts = {}
dicts['a'] = list('bdou')
dicts['b'] = list('hlt')
dicts['c'] = list('eo')
dicts['d'] = list('ao')
dicts['e'] = list('c')
dicts['f'] = list('')
dicts['g'] = list('pqy')
dicts['h'] = list('bn')
dicts['i'] = list('jlt')
dicts['j'] = list('giy')
dicts['k'] = list('bx')
dicts['l'] = list('ikt')
dicts['m'] = list('n')
dicts['n'] = list('mr')
dicts['o'] = list('au')
dicts['p'] = list('qy')
dicts['q'] = list('gpy')
dicts['r'] = list('cnx')
dicts['s'] = list('cz')
dicts['t'] = list('fl')
dicts['u'] = list('ovy')
dicts['v'] = list('uw')
dicts['w'] = list('v')
dicts['x'] = list('')
dicts['y'] = list('gjq')
dicts['z'] = list('s')
dicts['6'] = list('b')
dicts['('] = list('c')
dicts['5'] = list('s')

def words(text):
    return re.findall(r'\w+', text.lower())

DATA = open('medvocab.txt').read()+'\n'+open('engvocab.txt').read()
WORDS = Counter(words(DATA))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word,len(word)), key=P)

def candidates(word,n): 
    "Generate possible spelling corrections for word."
    k = known([word]) or known(edits1(word))
    if n==1:
        return k or [word]
    for i in range(n-1): 
        k = k or known(editsn(word,i+2))
    k = k or [word]
    return k

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def editsn(word,n): 
    "All edits that are two edits away from `word`."
    if n==1:
        return edits1(word)
    else :
        return (e2 for e1 in editsn(word,n-1) for e2 in edits1(e1))

def visualsim(word):
    "Matching visually similar letters"
    k = list(word)
    check = []
    for b,count in enumerate(k):
        for x in dicts[count]:
            h = list(word)
            h[b] = x
            check.append(''.join(h))
    return check

def visualsimn(word,n):
    check = []
    if n==1:
        return visualsim(word)
    else:
        hi = visualsimn(word,n-1)
        for kri in hi:
            for b,count in enumerate(kri):
                for x in dicts[count]:
                    h = list(word)
                    h[b] = x
                    check.append(''.join(h))
        return check + hi

def vsimcandidates(word,n): 
    "Generate possible spelling corrections for word."
    k = known([word]) or known(visualsim(word))
    if n==1:
        return k or [word]
    for i in range(n-1): 
        k = k or known(visualsimn(word,i+2))
    return k

def vsimcorrection(word): 
    "Most probable spelling correction for word."
    the = vsimcandidates(word,len(word))
    if bool(the):
        return max(the, key=P)
    else:
        return "#@!"

def spellcor(word):
    store = vsimcorrection(word.lower())
    if store == "#@!":
        return correction(word.lower())
    else :
        return store

if __name__ == "__main__":
    spellcor(argv[1])
