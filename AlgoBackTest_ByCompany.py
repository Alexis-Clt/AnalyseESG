# -*- coding: utf-8 -*-
"""
Created on Sat May 28 13:15:43 2022

@author: alexm
"""
# %% Importations
import nltk
#nltk.download('vader_lexicon')
from SentimentIntensityAnalyzer import SentimentIntensityAnalyzerClass
from Twitter import TwitterClient
import YahooFinance
from DataSet import DataSet
import matplotlib.pyplot as plt
import datetime

from pandas_datareader import data as pdr
from datetime import date
import yfinance as yf
yf.pdr_override()
import pandas as pd

import os
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np


# %% Manipulation Twitter

import tweepy
import Credentials
from SentimentIntensityAnalyzer import SentimentIntensityAnalyzerClass

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
    
    def lastTweets(self,query,start,end):
        return self.client.search_all_tweets(query,start_time = start , end_time = end)

    def TwitterSS(query,start,end):
        client = TwitterClient()
        collected_data=client.lastTweets(query,start,end).data
        test=collected_data[0].text
        text=[]
        ssresult=[]
        for data in collected_data:
            text.append(data.text)
        for sentence in text:
            sid = SentimentIntensityAnalyzerClass() 
            ss = sid.polarity_scores(sentence)
            ssresult.append(ss)
        return ssresult
        

# %% Données YAHOO Finance

def getData(ticker,start_date,end_date):
    #print (ticker)
    start_dt = datetime.datetime.strptime(start_date,'%Y-%m-%d') - datetime.timedelta(1)
    start_date = start_dt.strftime("%Y-%m-%d")
    
    data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
    #print(data)
    dataname= ticker+"_"+str(end_date)
    files.append(dataname)
    SaveData(data, dataname)

# Create a data folder in your current dir.
def SaveData(df, filename):
    path = os.getcwd()
    df.to_csv(path + "\\data\\" +filename+".csv")

#This loop will iterate over ticker list, will pass one ticker to get data, and save that data as file.
#%% Utilisation Twitter
def Algo(Ecoef,Scoef,Gcoef,expectedscore,CompanyName,start,end):
    path = r"C:\Users\alexm\Desktop\VI-AnalyseESG-main\Analyse du sentiment\CAC40_valeurs_ESG.xlsx"

    OurDataSet=DataSet(path, Ecoef,Scoef,Gcoef,expectedscore)
    ssresultyahoo=[]
    ssresulttwitter=[]
    sumcyahooresult=[]
    sumctwitterresult=[]
    companies=[]
    esgscores=[]
    tupleresult=[]
    
    ssresultyahoo.append(YahooFinance.YahooFinanceSS(YahooFinance.CleaningData(str(CompanyName))))  #liste de dictionnaires selon company
    ssresulttwitter.append(TwitterClient.TwitterSS(str(CompanyName),start,end))  #liste de dictionnaires selon company
    companies.append(str(CompanyName))
    for i in OurDataSet.titres["Final Score"]:
        esgscores.append(float(i))
    for i in ssresultyahoo: 
        sumcyahoo=0
        if (i!=[]):
            for j in i:
                sumcyahoo+=j["compound"] #on récupère et on somme tout les compound concernant la company
        sumcyahooresult.append(sumcyahoo) 
        
    for i in ssresulttwitter:
        sumctwitter=0
        if (i!=[]):
            for j in i:
                sumctwitter+=j["compound"] #on récupère et on somme tout les compound concernant la company
        sumctwitterresult.append(sumctwitter)
    compoundresult=[sumcyahooresult[i]+sumctwitterresult[i] for i in range(len(sumctwitterresult))] #en index i, la company (classée i-ème) obtient son score compound
    for i in range(len(compoundresult)):
        tupleresult.append((companies[i],round(compoundresult[i],2),round(esgscores[i],2)))
    return tupleresult

def DisplayResults(tupleresult):
    x=[]
    y=[]
    names=[]
    for i in range(len(tupleresult)):
        x.append(tupleresult[i][1])
        y.append(tupleresult[i][2])
        names.append(tupleresult[i][0])
    plt.scatter(x,y)
    plt.xlabel("Compound Score")
    plt.ylabel("ESG Score")
    plt.title('Results of the analysis')
    for i, label in enumerate(names):
        plt.text(x[i], y[i],label)
    plt.show()

def ToString(tupleresult):
    opinions=[]
    for i in range(len(tupleresult)):
        if (tupleresult[i][1]<0):
            opinions.append("sell")
        elif (tupleresult[i][1]<1 and tupleresult[i][1]>=0):
            opinions.append("wait")
        else:
            opinions.append("buy")
    for i in range(len(opinions)):
        print(f" Company : {tupleresult[i][0]} \n Compound : {tupleresult[i][1]} \n ESG : {tupleresult[i][2]} \n Opinion : {opinions[i]} \n")

def Opinionlist(tupleresult):
    opinions=""
    for i in range(len(tupleresult)):
        if (tupleresult[i][1]<0):
            opinions = "sell"
        elif (tupleresult[i][1]<1 and tupleresult[i][1]>=0):
            opinions = "wait"
        else:
            opinions = "buy"
    return opinions
    
def Search_opinion(Company,start_date,end_date):
    start_dt = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    end_dt = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    periode = end_dt - start_dt
    datetime_list = [start_dt + datetime.timedelta(i) for i in range(0,periode.days,30*3)]

    opinions = []
    for i in datetime_list:
        now = i
        td1 = datetime.timedelta(days = 1)
        td2 = datetime.timedelta(days = 4)
        end = now - td1
        start = end - td2
        print(end,start)
        test=Algo(0.7,0.2,0.1,85,Company,start,end)
        DisplayResults(test)
        ToString(test)
        opinions.append(Opinionlist(test))
    dict_date_opinion ={}
    for i in range(len(datetime_list)):
        dict_date_opinion[datetime_list[i].strftime("%Y-%m-%d")] = opinions[i]
    
    return dict_date_opinion
    
# %% Main
if __name__ == '__main__' :
    Company = "Alstom"
    Ticker="ALO.PA"
    start_date= "2020-01-02"
    end_date="2021-01-01"
    
    files = []
    getData(Ticker,start_date,end_date)
    path = os.getcwd()
    df1= pd.read_csv(path +"\\data\\"+ str(files[0])+".csv",index_col="Date")
    ts = df1["Open"]
    
    
    dico_opinion = Search_opinion(Company,start_date,end_date)
    X = list(dico_opinion.keys())
    Y=[]
    for i in X:
        if i in ts.keys():
            Y.append(ts[i])
        else:
            start_date = i
            start_dt = datetime.datetime.strptime(start_date,'%Y-%m-%d') + datetime.timedelta(2)
            start_date = start_dt.strftime("%Y-%m-%d")
            Y.append(ts[start_date])
    ts_index = date2num(ts.index)
    ts_value = list(ts)
    fig = plt.figure()
    graph = fig.add_subplot(111)
    graph.plot(ts_index,ts_value)
    
    
    my_list = list(dico_opinion.values())
    for i in range(len(my_list)):
        if my_list[i] =="sell":
            my_list[i] = 0
        if my_list[i] =="buy":
            my_list[i] = 1
        if my_list[i] =="wait":
            my_list[i] = 2
    colormap=np.array(['red','green','black'])
    graph.scatter(date2num(X),Y,marker="o",color= colormap[my_list])
            
    
    
     
    