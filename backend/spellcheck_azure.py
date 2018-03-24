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

    response = spellcheck(old_query)['flaggedTokens']
    response.reverse()
    new_query = old_query

    for token in response:
        left = token['offset']
        right = left + len(token['token'])
        suggestions = sorted(token['suggestions'], key=operator.itemgetter('score'), reverse=True)
        replacement = suggestions[0]['suggestion']
        new_query = new_query[:left] + replacement + new_query[right:]

    return new_query

if __name__ == "__main__":
    """
    1. Get key for spell check from https://azure.microsoft.com/en-in/try/cognitive-services
     and save it in a .env file, like the one shown in .env_example file.
    2. Run this script like, `python3 azure_spellcheck.py 'Afoxilin talet (10)'`.
    """

    QUERY = argv[1] # For example, 'Afoxilin talet (10)'
    make_correction(QUERY)
