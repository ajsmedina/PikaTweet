import json
import os
import re
from html import unescape

import requests
import twitter

RAPID_API_KEY = os.environ['RAPID_API_KEY']
TWITTER_CONSUMER = os.environ['TWITTER_CONSUMER']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_ACCESS = os.environ['TWITTER_ACCESS']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

headers = {'X-RapidAPI-Key': RAPID_API_KEY}

api = twitter.Api(consumer_key=TWITTER_CONSUMER,
                  consumer_secret=TWITTER_CONSUMER_SECRET,
                  access_token_key=TWITTER_ACCESS,
                  access_token_secret=TWITTER_ACCESS_SECRET)


def generate_pika(syllables, start_pi, is_capital, is_capslock):
    use_pi = start_pi or syllables > 1
    word_to_return = ''

    for i in range(syllables):
        if use_pi:
            if i == syllables - 1 and syllables > 1:
                word_to_return += 'CHU' if is_capslock else 'chu'
            else:
                word_to_return += 'P' if is_capslock or (is_capital and i == 0) else 'p'
                word_to_return += 'I' if is_capslock else 'i'
        else:
            word_to_return += 'K' if is_capslock or (is_capital and i == 0) else 'k'
            word_to_return += 'A' if is_capslock else 'a'

        use_pi = not use_pi

    return word_to_return


results = api.GetSearch(raw_query='q=from%3ArealDonaldTrump&tweet_mode=extended')

tweet = unescape(json.loads(results[0].AsJsonString())['full_text'])
print(tweet)

words = tweet.split(' ')
syllables = []
word_info = []

for index, word in enumerate(words):
    info = {'punctuation_before': '', 'punctuation_after': '', 'capital': False, 'capslock': False}

    if word.isupper():
        info['capslock'] = True

    before = True
    for letter in word:
        if not (letter.isalpha() or letter == "’"):
            if before:
                info['punctuation_before'] += letter
            else:
                info['punctuation_after'] += letter
        elif before:
            if letter.isalpha() and letter.isupper():
                info['capital'] = True
            before = False

    word_info.append(info)
    word_to_count = re.sub(r"[^A-Za-z']+", '', word)

    if word_to_count == '':
        syllables.append(-1)
    else:

        response = requests.get(f"https://wordsapiv1.p.rapidapi.com/words/{word_to_count}/",
                                headers=headers
                                )
        word_obj = json.loads(response.text)
        if 'syllables' in word_obj:
            syllables.append(word_obj['syllables']['count'])
        else:
            syllables.append(1)

final_tweet = ''
use_pi = False
for index, word in enumerate(syllables):
    info = word_info[index]

    if word > 1:
        use_pi = False
    else:
        use_pi = not use_pi
    if info['punctuation_before'] == '#' or info['punctuation_before'] == '@':
        final_tweet += words[index]
    elif word > 0:

        final_tweet += info['punctuation_before']
        final_tweet += generate_pika(word, use_pi, info['capital'], info['capslock'])
        final_tweet += info['punctuation_after']

    if not info['punctuation_after'] == '':
        use_pi = False
    final_tweet += ' '

print(final_tweet)