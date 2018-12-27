import json
import re
from html import unescape

import requests
import twitter

headers = {'X-RapidAPI-Key': '81ca78c963msh0d128dc3941a7a7p15fc23jsn4c4203c0863a'}

api = twitter.Api(consumer_key='KmmUe8P2yMpyCufe3eG14Iuoa',
                  consumer_secret='jYLCmQ5vEesvRxBlb4Lcu2LFqhER4swm8z5CwQVYd3fG3O0Yhi',
                  access_token_key='3029454813-pwXSKciyjFQ2Ut7tqPAYdv1IH1N24q8w0smDBQQ',
                  access_token_secret='lC3ejCcEsmjKpb9SGpLcykg1lqD0a8NAlf9jgD3hdipNM')

results = api.GetSearch(raw_query='q=from%3ArealDonaldTrump&tweet_mode=extended')

tweet = unescape(json.loads(results[0].AsJsonString())['full_text'])
print(tweet)

words = tweet.split(' ')
syllables = []
pucntuation = {}

for index, word in enumerate(words):
    only_punctuation = True

    for letter in word:
        if not (letter.isalnum() or letter == "'"):
            pucntuation[index] = letter
        else:
            only_punctuation = False

    if only_punctuation:
        syllables.append(-1)
    else:
        word_to_count = re.sub(r"[^A-Za-z']+", '', word)
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
        final_tweet += str(word)

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
