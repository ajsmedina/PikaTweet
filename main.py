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
TWITTER_HANDLE = 'realDonaldTrump'

headers = {'X-RapidAPI-Key': RAPID_API_KEY}

api = twitter.Api(consumer_key=TWITTER_CONSUMER,
                  consumer_secret=TWITTER_CONSUMER_SECRET,
                  access_token_key=TWITTER_ACCESS,
                  access_token_secret=TWITTER_ACCESS_SECRET)


def generate_tweet(words, word_info):
    final_tweet = ''
    start_pi = False

    for index, info in enumerate(word_info):

        if info.syllables > 1:
            start_pi = False
        else:
            start_pi = not start_pi

        if '#' in info.punctuation_before or '@' in info.punctuation_before:
            final_tweet += words[index]
        else:
            final_tweet += info.punctuation_before
            final_tweet += generate_pika(info.syllables, start_pi, info.is_capital, info.is_capslock)
            final_tweet += info.punctuation_after

        if not info.punctuation_after == '':
            start_pi = False

        final_tweet += ' '

    return final_tweet


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


def create_word_info(words):
    word_info = []
    for index, original_word in enumerate(words):
        new_word = word.Word()

        if original_word.isupper():
            new_word.is_capslock = True

        before = True
        for letter in original_word:
            if not (letter.isalpha() or letter == "’"):
                if before:
                    new_word.punctuation_before += letter
                else:
                    new_word.punctuation_after += letter
            elif before:
                if letter.isalpha() and letter.isupper():
                    new_word.is_capital = True
                before = False

        word_to_count = re.sub(r"[^A-Za-z']+", '', original_word)

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

    return word_info


results = api.GetSearch(raw_query=f'q=from%3A{TWITTER_HANDLE}&tweet_mode=extended')
results_url = api.GetSearch(raw_query=f'q=from%3A{TWITTER_HANDLE}')
id_str = json.loads(results_url[0].AsJsonString())['id_str']
tweet = unescape(json.loads(results[0].AsJsonString())['full_text'])
print(tweet)

words = tweet.split(' ')
word_info = create_word_info(words)
new_tweet = generate_tweet(words, word_info)

print(new_tweet)
url = f'https://twitter.com/{TWITTER_HANDLE}/status/{id_str}'
print(url)
api.PostUpdate(new_tweet, attachment_url=url)
