import json
import re
import requests
import twitter

headers = {'X-RapidAPI-Key': '81ca78c963msh0d128dc3941a7a7p15fc23jsn4c4203c0863a'}

api = twitter.Api(consumer_key='KmmUe8P2yMpyCufe3eG14Iuoa', consumer_secret='jYLCmQ5vEesvRxBlb4Lcu2LFqhER4swm8z5CwQVYd3fG3O0Yhi',
            access_token_key='3029454813-pwXSKciyjFQ2Ut7tqPAYdv1IH1N24q8w0smDBQQ', access_token_secret='lC3ejCcEsmjKpb9SGpLcykg1lqD0a8NAlf9jgD3hdipNM')

results = api.GetSearch(raw_query='q=from%3Anot_antonik')

tweet = json.loads(results[0].AsJsonString())['text']
print(tweet)

words = tweet.split(' ')


for word in words:
    word_to_count = re.sub(r"[^A-Za-z']+", '', word)
    print(word_to_count)
    response = requests.get(f"https://wordsapiv1.p.rapidapi.com/words/{word_to_count}/",
                            headers=headers
                            )
    word_obj = json.loads(response.text)
    if 'syllables' in word_obj:
        print(word_obj['syllables']['count'])
    else:
        print('guess: 1')
