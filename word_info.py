import requests
import json

wordnikApiUrl = 'http://api.wordnik.com/v4'
wordnikApiKey = '84f847568dcea9f7800070ff8620bb33f62222a82c603d8b3'
translateUrl = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
translateApiKey = 'trnsl.1.1.20161025T084011Z.855e1e7dff7841a3.1741c0fb9b04bec795285583df7868e55221fbc2'

"""https://translate.yandex.net/api/v1.5/tr.json/translate ?
key=<API key>
 & text=<text to translate>
 & lang=<translation direction>
 & [format=<text format>]
 & [options=<translation options>]
 & [callback=<name of the callback function>]"""
def get_translation(word):
    params = dict(
        text=word,
        lang='en-ru',
        key=translateApiKey
    )
    resp = requests.get(translateUrl, params=params)
    return resp.json()['text']


def get_example(word):
    url = wordnikApiUrl + """/word.json/""" + word + """/topExample?useCanonical=true&api_key=""" + wordnikApiKey
    resp = requests.get(url=url)
    data = json.loads(resp.text)
    return data['text']


def get_defenition(word, pos):
    url = wordnikApiUrl + """/word.json/""" + word + """/definitions?limit=5&partOfSpeech=""" + pos + \
          """&includeRelated=true&sourceDictionaries=all&useCanonical=true&includeTags=false&api_key=""" + wordnikApiKey
    resp = requests.get(url=url)
    data = json.loads(resp.text)[0]
    return data['text']
