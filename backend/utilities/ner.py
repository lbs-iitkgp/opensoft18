import spacy
from spacy import displacy

NLP = spacy.load('en')

def render_ner(text):
    tagged_text = NLP(text)
    return displacy.parse_ents(tagged_text)
