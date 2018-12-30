import json
import os
import re
from html import unescape

import word

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

for index, num_syllables in enumerate(words):
    new_word = word.Word()

    if num_syllables.isupper():
        new_word.is_capslock = True

    before = True
    for letter in num_syllables:
        if not (letter.isalpha() or letter == "’"):
            if before:
                new_word.punctuation_before += letter
            else:
                new_word.punctuation_after += letter
        elif before:
            if letter.isalpha() and letter.isupper():
                new_word.is_capital = True
            before = False

    word_to_count = re.sub(r"[^A-Za-z']+", '', num_syllables)

    if word_to_count == '':
        new_word.syllables = -1
    else:

        response = requests.get(f"https://wordsapiv1.p.rapidapi.com/words/{word_to_count}/",
                                headers=headers
                                )
        word_obj = json.loads(response.text)
        if 'syllables' in word_obj:
            new_word.syllables = word_obj['syllables']['count']
        else:
            new_word.syllables = 1

    word_info.append(new_word)

final_tweet = ''
use_pi = False
for index, info in enumerate(word_info):
    num_syllables = info.syllables

    if num_syllables > 1:
        use_pi = False
    else:
        use_pi = not use_pi
    if info.punctuation_before == '#' or info.punctuation_before == '@':
        final_tweet += words[index]
    elif num_syllables > 0:

        final_tweet += info.punctuation_before
        final_tweet += generate_pika(num_syllables, use_pi, info.is_capital, info.is_capslock)
        final_tweet += info.punctuation_after

    if not info.punctuation_after == '':
        use_pi = False
    final_tweet += ' '

print(final_tweet)