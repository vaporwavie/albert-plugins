"""
  Get suggestions from Google
"""
from albertv0 import *
from os import path
import requests
import lxml.html
import json


__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'Google Suggestions'
__version__ = '1.0'
__trigger__ = 'gg '
__author__ = 'Angelo Gazzola'
__dependencies__ = ['lxml', 'cssselect']
__icon__ = path.dirname(__file__) + '/icons/Google.png'


REQUEST_HEADERS = {
  'User-Agent': (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/62.0.3202.62 Safari/537.36'
  )
}
session = requests.Session()
session.trust_env = False


class SuggestionItem(Item):
  def __init__(self, suggestion):
    super().__init__(
      id=str(hash(suggestion)),
      icon=__icon__,
      text=suggestion,
      completion=__trigger__ + suggestion,
      actions=[
        UrlAction(
          'Search on Google',
          'https://google.com/search?q={}'.format(suggestion)
        )
      ]
    )


class ResultItem(Item):
  def __init__(self, result):
    super().__init__(
      id=result[1],
      icon=__icon__,
      text=result[0],
      subtext=result[1],
      actions=[UrlAction('Search on Google', result[1])]
    )


def search(query):
  response = session.get('https://google.com/search',
    headers=REQUEST_HEADERS,
    params={
      'client': 'firefox',
      'output': 'toolbar',
      'hl': 'en',
      'q': query,
    }
  )
  get_url = lambda el: el.get('href')
  html = lxml.html.fromstring(response.text)
  results = html.cssselect('h3 > a')
  results = [(r.text_content(), get_url(r)) for r in results]
  return [ResultItem(r) for r in results]


def suggest(query):
  response = session.get('https://clients1.google.com/complete/search',
    headers=REQUEST_HEADERS,
    params={
      'client': 'firefox',
      'output': 'toolbar',
      'hl': 'en',
      'q': query,
    }
  )
  suggestions = json.loads(response.text)[1]
  return [SuggestionItem(suggestion) for suggestion in suggestions]


def handleQuery(query):
  if query.isTriggered and len(query.string) > 0:
    if query.string[-1] == '_':
      items = search(query.string[:-1])
    else:
      items = suggest(query.string)
      items.insert(0, SuggestionItem(query.string))
    return items

  return [Item(icon=__icon__, text='Search Google')]
