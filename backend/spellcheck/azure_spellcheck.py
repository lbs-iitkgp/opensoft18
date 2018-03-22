import os
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv(join(dirname(__file__), '.env'))

import requests
import operator
from sys import argv

SPELLCHECK_ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0/spellcheck'
SPELLCHECK_KEY = os.getenv('SPELLCHECK_KEY')

def spellcheck(query):
  '''
  GETS the spellcheck endpoint response
  '''
  return(requests.get(SPELLCHECK_ENDPOINT, params={'subscription-key': SPELLCHECK_KEY, 'text': query}).json())

def make_correction(old_query):
  '''
  Retuns a new string with spellcheck corrections made on the given string
  '''
  response = spellcheck(old_query)['flaggedTokens']
  response.reverse()
  new_query = old_query

  for token in response:
    left = token['offset']
    right = left + len(token['token'])
    suggestions = sorted(token['suggestions'], key=operator.itemgetter('score'), reverse=True)
    replacement = suggestions[0]['suggestion']
    new_query = new_query[:left] + replacement + new_query[right:]

  if old_query == new_query:
    print("Nothing fishy about '{}'".format(old_query))
  else:
    print("'{}' got corrected to '{}'".format(old_query, new_query))

  return(new_query)

if __name__ == "__main__":
  '''
  1. Get key for spell check from https://azure.microsoft.com/en-in/try/cognitive-services
     and save it in a .env file, like the one shown in .env_example file.
  2. Run this script like, `python3 azure_spellcheck.py 'Afoxilin talet (10)'`.
  '''
  query = argv[1] # For example, 'Afoxilin talet (10)'
  make_correction(query)
