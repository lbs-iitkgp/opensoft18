"""
processes sentence and extracts names from it

credits: github@onyxfish and github@ririw
source: https://gist.github.com/onyxfish/322906
"""

import nltk

# downloading required nltk libraries
nltk.download('maxent_ne_chunker')
nltk.download('words')


def extract_entity_names(t):
    """
    extracts name(s) from one sentence at a time
    :param t: ntlk word tree made from sentence
    :return: entity_names: list containing names in the sentence
    """

    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names


def extract(in_str):
    """
    function to be called for extracting names from sentence
    :param in_str: string, can contain multiple sentences
    :return: entity_names: list of names in the input string, in order they appear
    """

    sentences = nltk.sent_tokenize(in_str)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    entity_names = []
    for tree in chunked_sentences:
        # append can be used below if we want names linked with sentences
        entity_names.extend(extract_entity_names(tree))

    return entity_names


if __name__ == "__main__":
    pass
