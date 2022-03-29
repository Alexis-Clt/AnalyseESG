#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:54:35 2022

@author: user
"""
# en fait se poser la question si nécessaire car les news sur sites nécessitent web scrapping alors que yahoo finance tweets ses articles => est- ce vraiment utile yahoo finance car va être utilisé deux fois dans analyse sentiments
from Twitter import TwitterClient
from SentimentIntensityAnalyzer import SentimentIntensityAnalyzerClass

def YahooFinanceSS(text):
    ssresult=[]
    for sentence in text:
        sid = SentimentIntensityAnalyzerClass() 
        ss = sid.polarity_scores(sentence)
        ssresult.append(ss)
    return ssresult

def CleaningData(query):
    client = TwitterClient()
    collected_data=client.client.get_users_tweets(id="19546277").data #récupère tout les tweets de yahoo finance
    text=[]
    for data in collected_data:
        if (query in data.text):
            text.append(data.text)
    return text
    