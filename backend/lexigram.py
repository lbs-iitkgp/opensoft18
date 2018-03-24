from sys import argv

import os
from os.path import join, dirname
import requests
import dotenv
import parse_name as pn

dotenv.load(join(dirname(__file__), '.env'))
LEXIGRAM_ENDPOINT = 'https://api.lexigram.io/v1/extract/entities'
LEXIGRAM_KEY = os.getenv('LEXIGRAM_KEY')

def fetch_response(endpoint, query):
    """
    GETS lexigram extractor endpoint
    :param endpoint: path to the API endpoint
    :param query: query string to extract data
    :return: response: JSON response of the request
    """

    headers = {'Authorization': 'Bearer '+LEXIGRAM_KEY}
    params = {'text': query, 'withContext': True,
              'withMatchLogic': 'longest', 'withText': False}

    return requests.get(endpoint, headers=headers, params=params).json()

def extract_metadata_json(query):
    """
    Extracts a JSON response with keys 'NAMES', 'DRUGS', 'FINDINGS', 'PROBLEMS', etc.
    :param query: query string to extract json data
    :return: response: Dict response with keys 'NAMES', 'DRUGS', 'FINDINGS', 'PROBLEMS', etc.
    """

    metadata = {}
    matches = fetch_response('https://api.lexigram.io/v1/extract/entities', query)['matches']
    for match in matches:
        for match_type in match['types']:
            if match_type not in metadata:
                metadata[match_type] = set()
            metadata[match_type].add(match['label'])

    names = set(pn.extract(query))
    if names:
        metadata['NAMES'] = names

    return metadata

def has_medicine(query):
    """
    Returns boolean response of whether a string contains a DRUG or not
    :param query: query string to extract json data
    :return: True or False
    """

    matches = fetch_response('https://api.lexigram.io/v1/extract/entities', query)['matches']
    for match in matches:
        if 'DRUGS' in match['types']:
            return True
    return False

if __name__ == "__main__":
    """
    1. Get key for lexigram from https://docs.lexigram.io/v1/data-extractions/extract
     and save it in a .env file, like the one shown in .env_example file.
    2. Run this script like, `python3 azure_spellcheck.py 'Amoxicillin (10)'`.
    """

    QUERY = argv[1] # For example, 'Amoxicillin Heart Attack (10mg)'
    print(has_medicine(QUERY))
    print(extract_metadata_json(QUERY))
