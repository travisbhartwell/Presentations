#!/usr/bin/python
from twitpic import twitpic2
import twitter

from config import *

twitpic = twitpic2.TwitPicOAuthClient(
    consumer_key = consumer_key,
    consumer_secret = consumer_secret,
    access_token = access_token,
    service_key = twitpic_api_key,
)

response = twitpic.create('upload',
                          {'media': "presentation-1.png",
                           "message": "Web Automation With Python. Slide 2"})

if response:
    twitter_api = twitter.Api(consumer_key=consumer_key,
                              consumer_secret=consumer_secret,
                              access_token_key=twitter_oauth_token,
                              access_token_secret=twitter_oauth_token_secret)

    status = twitter_api.PostUpdate("%s: %s" % (response["text"], response["url"]))
