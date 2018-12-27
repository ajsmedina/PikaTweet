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
for index, word in enumerate(syllables):
    final_tweet += word_info[index]['punctuation_before']
    # TODO: automate this based on my rules

    if word > 0:
        final_tweet += 'P' if word_info[index]['capital'] else 'p'
        if word == 1:
            final_tweet += 'I' if word_info[index]['capslock'] else 'i'
        elif word == 2:
            final_tweet += 'ika'
        elif word == 3:
            final_tweet += 'ikachu'
        elif word == 4:
            final_tweet += 'ikapika'

    final_tweet += word_info[index]['punctuation_after']
    final_tweet += ' '

print(final_tweet)

# breakdown:
# 1 syllable: alternate pi ka (I don't know -> Pi ka pi)
# 2+ syllables mod 2 or mod 0, pikachu  (beautiful -> pikachu) (hippopotamus -> pikapikachu)
# 2 syllables to 1 syllable: pika pi
# 1 syllable to 2 syllables: pi pika

# TODO: preserve capitalization
