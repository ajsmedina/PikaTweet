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
pucntuation = {}

for index, word in enumerate(words):

    for letter in word:
        if not (letter.isalnum() or letter == "'"):
            pucntuation[index] = letter

    word_to_count = re.sub(r"[^A-Za-z']+", '', word)

    if word_to_count == '':
        syllables.append(word)
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
    # TODO: automate this based on my rules
    if word == 1:
        final_tweet += 'pi'
    elif word == 2:
        final_tweet += 'pika'
    elif word == 3:
        final_tweet += 'pikachu'
    elif word == 4:
        final_tweet += 'pikapika'
    elif word != -1:
        final_tweet += words[index]

    if index in pucntuation:
        final_tweet += pucntuation[index]
    final_tweet += ' '

print(final_tweet)

# breakdown:
# 1 syllable: alternate pi ka (I don't know -> Pi ka pi)
# 2+ syllables mod 2 or mod 0, pikachu  (beautiful -> pikachu) (hippopotamus -> pikapikachu)
# 2 syllables to 1 syllable: pika pi
# 1 syllable to 2 syllables: pi pika

# TODO: preserve capitalization
