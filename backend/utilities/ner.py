import spacy
from spacy import displacy

NLP = spacy.load('en_core_web_sm')

def render_ner(text):
    tagged_text = NLP(text)
    return displacy.parse_ents(tagged_text)
