from sys import argv

import os
from os.path import join, dirname
import operator
import requests
import dotenv
dotenv.load_dotenv(join(dirname(__file__), '.env'))

SPELLCHECK_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0/spellcheck'
SPELLCHECK_KEY = os.getenv('SPELLCHECK_KEY')

def spellcheck(query):
    """
    GETS azure spellcheck endpoint
    :param query: query string to extract data
    :return: response: JSON response of the request
    """

    params = {'subscription-key': SPELLCHECK_KEY, 'text': query}
    return requests.get(SPELLCHECK_ENDPOINT, params=params).json()

def make_correction(old_query):
    """
    Makes the corrections prescribed by Azure's spellchecker
    :param old_query: query string
    :return: new_query: string with corrections made
    """
    print(old_query)
    response = spellcheck(old_query)['flaggedTokens']
    print(response)
    response.reverse()
    new_query = old_query
    for token in response:
        left = token['offset']
        right = left + len(token['token'])
        suggestions = sorted(token['suggestions'], key=operator.itemgetter('score'), reverse=True)
        replacement = suggestions[0]['suggestion']
        new_query = new_query[:left] + replacement + new_query[right:]
    return new_query

def merge_bounding_boxes(bounding_boxes):
    """
    Merges any bounding boxes, based on spellchecker's typo corrections
    :param bounding_boxes: A list of bounding boxes
    :return: new_bounding_boxes: Merged bounding boxes, with same 'A', 'W', 'L' encoding
    """

    old_all_text = bounding_boxes[0].bound_text
    new_all_text = make_correction(old_all_text)
    bounding_boxes[0].bound_text = new_all_text

    word_boxes = list(filter(lambda x: x.box_type == 'W', bounding_boxes))
    i = 0
    while i < len(word_boxes)-1:
        this_box = word_boxes[i]
        next_box = word_boxes[i+1]
        this_word = this_box.bound_text
        next_word = next_box.bound_text
        print(new_all_text)
        # print(this_word, .find(this_word))
        # print(next_word, new_all_text.find(next_word))
        print(this_word, new_all_text.find(this_word)==0, new_all_text.find(next_word) == (len(this_word)))
        if new_all_text.find(this_word) != 0:
            # print("OWOWnew_all_textOW")
            word_boxes[i].bound_text = new_all_text.split(' ')[0]
            new_all_text = " ".join(new_all_text.split(' ')[1:])
            i += 1
        elif new_all_text.find(this_word) == 0 and new_all_text.find(next_word) == (len(this_word)+1) and next_word[0].islower():
            # print("EYEYEY")
            # new_all_text = new_all_text[len(this_word)+1:]
            # print(word_boxes[i])
            # print(word_boxes[i+1])
            word_boxes[i] = this_box.merge(next_box)
            # print(word_boxes[i])
            # print(word_boxes[i+1])
            del word_boxes[i+1]
        else:
            new_all_text = new_all_text[len(this_word)+1:]
            i += 1
        # else:
        #     print(word_boxes[i])
        #     print(word_boxes[i+1])
        #     word_boxes[i] = this_box.merge(next_box)
        #     print(word_boxes[i])
        #     print(word_boxes[i+1])
        #     del word_boxes[i+1]
        # input()

    new_bounding_boxes = [bounding_boxes[0]] + word_boxes
    sentence_boxes = list(filter(lambda x: x.box_type == 'L', bounding_boxes))
    for sentence_box in sentence_boxes:
        sentence_box.bound_text = sentence_box.find_enclosed_text(word_boxes)
        sentence_box.bb_children = sentence_box.find_enclosed_boxes(word_boxes)
        new_bounding_boxes.append(sentence_box)

    return new_bounding_boxes

if __name__ == "__main__":
    """
    1. Get key for spell check from https://azure.microsoft.com/en-in/try/cognitive-services
     and save it in a .env file, like the one shown in .env_example file.
    2. Run this script like, `python3 azure_spellcheck.py 'Afoxilin talet (10)'`.
    """

    QUERY = argv[1] # For example, 'Afoxilin talet (10)'
    make_correction(QUERY)
