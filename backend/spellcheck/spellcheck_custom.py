import re
import os
from collections import Counter
from sys import argv

dicts = {}
dicts['a'] = list('bdou')
dicts['b'] = list('hlt')
dicts['c'] = list('eo')
dicts['d'] = list('ao')
dicts['e'] = list('c')
dicts['f'] = list('l')
dicts['g'] = list('pqy')
dicts['h'] = list('tbn')
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
dicts['u'] = list('ovwy')
dicts['v'] = list('uw')
dicts['w'] = list('vu')
dicts['x'] = list('v')
dicts['y'] = list('gjq')
dicts['z'] = list('s')
dicts['6'] = 'b'
dicts['2'] = 'z'
dicts['3'] = 'b'
dicts['8'] = 'b'
dicts['9'] = 'g'
dicts['('] = 'c'
dicts['5'] = 's'
dicts['1'] = 'li'
dicts['0'] = '0'
misc = '12356890('
numbers = '1234567890'

def words(text): return re.findall(r'\w+', text.lower())

current = os.path.dirname(__file__)
spellcheckfol = os.path.join(current,'resources')
DATA = open(os.path.join(spellcheckfol,'medvocab.txt')).read()+'\n'+open(os.path.join(spellcheckfol,'engvocab.txt')).read()
WORDS = Counter(words(DATA))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    if len(word) <= 3:
        return(known([word]) or known(edi_del(word)) or [word])
    elif len(word) <= 6:
        return(known([word]) or known(edi_del(word)) or known(edi_del2(word)) or [word])
    else :
        temp = known([word]) or known(edi_del(word)) or known(edi_del2(word))
        if bool(temp):
            return temp
        return(temp or known(edits3(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    # deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in dicts[R[0]]]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(transposes + replaces + inserts)

def delete(word):
    "Checks for a delete"
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    return set(deletes)

def edi_del(word):
    return delete(word).union(edits1(word))

def edi_del2(word):
    return delete(word).union(edits2(word))

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edi_del(word) for e2 in edits1(e1))

def edits3(word):
    "All edits that are three edits away from `word`."
    return (e3 for e2 in edits2(word) for e3 in edits1(e2))

# def edits4(word):
#     "All edits that are three edits away from `word`."
#     return (e4 for e3 in edits3(word) for e4 in edits1(e2))

def spellcor(word):
    word = word.lower()
    # while word.count(' ') > 2:
    # word = word.replace(' ', '', 1)
    if word in WORDS:
        return word
    try:
        return correction(word)
    except Exception:
        return word

if __name__ == "__main__":
    print(spellcor(argv[1]))
