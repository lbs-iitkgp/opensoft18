import os
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv(join(dirname(__file__), '.env'))

import requests
import operator
from sys import argv

LEXIGRAM_ENDPOINT = 'https://api.lexigram.io/v1/extract/entities'
LEXIGRAM_KEY = os.getenv('LEXIGRAM_KEY')

def fetch_response(endpoint, query):
  '''
  GETS the spellcheck endpoint response
  '''
  return(requests.get(endpoint, headers={'Authorization': 'Bearer '+LEXIGRAM_KEY}, params={'text': query, 'withContext': True, 'withMatchLogic': 'longest', 'withText': False}).json())

def fetch_search_response(endpoint, query):
  '''
  GETS the spellcheck endpoint response
  '''
  return(requests.get(endpoint, headers={'Authorization': 'Bearer '+LEXIGRAM_KEY}, params={'q': query, 'limit': 20}).json())

def extract_data(query):
  print(fetch_response('https://api.lexigram.io/v1/extract/entities', query))
  print(fetch_response('https://api.lexigram.io/v1/highlight/entities', query))
  print(fetch_search_response('https://api.lexigram.io/v1/lexigraph/search', query))

  # return(data)

if __name__ == "__main__":
  '''
  1. Get key for lexigram from https://docs.lexigram.io/v1/data-extractions/extract
     and save it in a .env file, like the one shown in .env_example file.
  2. Run this script like, `python3 azure_spellcheck.py 'Amoxicillin (10)'`.
  '''
  query = argv[1] # For example, 'Amoxicillin (10)'
  extract_data(query)
  # print(data)
