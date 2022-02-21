#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 17:00:19 2022

@author: user
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tweepy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

import Credentials

class TwitterClient(object):

    def __init__(self):

        bearer_token = Credentials.BEARER_TOKEN
        consumer_key = Credentials.CONSUMER_KEY
        consumer_secret = Credentials.CONSUMER_SECRET
        access_token = Credentials.ACCESS_TOKEN
        access_token_secret = Credentials.ACCESS_TOKEN_SECRET

        try:
            self.client = tweepy.Client(
                bearer_token,
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret)
        except:
            print("Error Authenticating")
    
    def getInfo(self):
        return self.client.get_me()

    def recentTweetsCount(self, query):
        return self.client.get_recent_tweets_count(query=query, granularity="day")

    def lastSevenDaysTweetsCount(self, query):
        return self.client.get_recent_tweets_count(query).meta["total_tweet_count"]
    
    def lastSevenDaysTweets(self,query):
        return self.client.search_recent_tweets(query)


client = TwitterClient()
collected_data=client.lastSevenDaysTweets("air liquide company").data
test=collected_data[0].text
text=[]
for data in collected_data:
    text.append(data.text)
for sentence in text:
    sid = SentimentIntensityAnalyzer() #juste un exemple car celui là vient de nltk.sentiement.vader à aller voir sur internet pour créer nos propres points positifs et négatifs
    print(sentence)
    ss = sid.polarity_scores(sentence)
    for k in sorted(ss):
        print('{0}: {1}, '.format(k, ss[k]), end='')
    print() 
#donc juste à créer notre classe Sentiment avec les mots clés choisis