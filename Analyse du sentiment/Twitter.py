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
print(client.lastSevenDaysTweetsCount("lvmh -is:retweet"))
print(client.lastSevenDaysTweets("lvmh -is:retweet").data)
    