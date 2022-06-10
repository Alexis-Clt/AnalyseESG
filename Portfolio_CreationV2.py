# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 12:30:23 2022

@author: alexm
"""


# %% Importation
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
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

import os
from matplotlib.dates import date2num
import numpy as np
import tweepy
import Credentials
from SentimentIntensityAnalyzer import SentimentIntensityAnalyzerClass

# %% Get Stock and Ticker
def Get_Stock_Ticker():
    path = os.getcwd() + "\\CAC40_valeurs_ESG.xlsx"
    initialTable = pd.read_excel(path)
    dict_Stock_Ticker = {}
    for i in range(len(list(initialTable["Company"]))):
        data = {initialTable["Company"][i]:initialTable["Ticker"][i]}
        dict_Stock_Ticker.update(data)
    return dict_Stock_Ticker
# %% Class Twitter
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

def RecupTweetCsv(company,start,end):
    path = os.getcwd()
    df = pd.read_csv(path+"\\TweetsFinal.csv")
    df = df[df["Company"]==company]
    df = df[df["Start"] > start]
    df = df[df["End"] < end]
    ssresult=[]
    for sentence in list(df.Tweet):
        sid = SentimentIntensityAnalyzerClass() 
        ss = sid.polarity_scores(sentence)
        ssresult.append(ss)
    return ssresult
    
# %% Algorithme 
def Algo(Ecoef,Scoef,Gcoef,expectedscore,start,end):
    path = r"C:\Users\alexm\Desktop\VI-AnalyseESG-main\Analyse du sentiment\CAC40_valeurs_ESG.xlsx"

    OurDataSet=DataSet(path, Ecoef,Scoef,Gcoef,expectedscore)
    ssresultyahoo=[]
    ssresulttwitter=[]
    sumcyahooresult=[]
    sumctwitterresult=[]
    companies=[]
    esgscores=[]
    tupleresult=[]
    for i in OurDataSet.titres["Company"]:
        ssresultyahoo.append(YahooFinance.YahooFinanceSS(YahooFinance.CleaningData(str(i))))  #liste de dictionnaires selon company
        ssresulttwitter.append(RecupTweetCsv(str(i),start,end))  #liste de dictionnaires selon company
        companies.append(str(i))
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

def Compound(tupleresult):
    
    dict_compound={}
    dict_compound_buy={}
    dict_compound_sell={}
    dict_compound_wait={}
    for i in range(len(tupleresult)):
        data ={tupleresult[i][0] : tupleresult[i][1]}
        dict_compound.update(data)
        if (tupleresult[i][1]<0):
            data ={tupleresult[i][0] : tupleresult[i][1]}
            dict_compound_sell.update(data)
        elif (tupleresult[i][1]<1 and tupleresult[i][1]>=0):
            data ={tupleresult[i][0] : tupleresult[i][1]}
            dict_compound_wait.update(data)
        else:
            data ={tupleresult[i][0] : tupleresult[i][1]}
            dict_compound_buy.update(data)
    return dict_compound_buy,dict_compound_wait,dict_compound_sell

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
        test=Algo(0.7,0.2,0.1,85,start,end)
        DisplayResults(test)
        ToString(test)
        opinions.append(Opinionlist(test))
    dict_date_opinion ={}
    for i in range(len(datetime_list)):
        dict_date_opinion[datetime_list[i].strftime("%Y-%m-%d")] = opinions[i]
    
    return dict_date_opinion

# %% Calcul des poids
def weightCalc(list_buy):
    val = list(list_buy.values())
    s = sum(val)
    weights = [i/s for i in val]
    for i in range(len(list_buy.keys())):
        list_buy[list(list_buy.keys())[i]] = weights[i]
    return list_buy

# %% Recupération des data

def Portfolio(start_date,end_date,members,weight):


    # history(start=start_date,end = end_date)
    firstdata = yf.Ticker(members[0]).history(start=start_date,end=end_date).reset_index()[["Date","Open"]]
    firstdata["Date"] = pd.to_datetime(firstdata["Date"])
    firstdata = firstdata.rename(columns={"Open":members[0]})
    basedata = firstdata
    if len(members)>1 :
        for i in range(1,len(members)):
            data = yf.Ticker(members[i]).history(start=start_date,end=end_date).reset_index()[["Date","Open"]]
            data["Date"] = pd.to_datetime(data["Date"])
            data = data.rename(columns={"Open":members[i]})
            basedata = pd.merge(basedata,data,on="Date")
    return basedata
def portfolioCalc(weight,data,name):
    data[name] = sum([weight[x]*data[x] /100 for x in list(weight.keys()) ])
    return data 
    # %% Normalisation
def Normalisation(basedata,members,final_price):
    for stock in members:
        basedata[stock] = basedata[stock]/basedata[stock].iloc[0]*final_price
    return basedata
    #print(basedata) 

    # %% Tracé du graphique
def Graph(data2):
    for i in list(data2.columns)[1:]:
        label = i
        plt.plot(data2["Date"],data2[i],label=i)
        plt.legend(loc=0)
    final_price = data2["Portfolio"][data2.shape[0]-1]

# %% Traitement du fichier CAC 40 ESG csv
def TraitementCAC40ESGcsv():
    path = os.getcwd()
    df = pd.read_csv(path+"\\CAC 40 ESG GR_historical_price (1).csv",sep=";",header=3,index_col = False)
    df["Date"] = df["Date"].apply(lambda datess :datetime.datetime.strptime(datess,'%d/%m/%Y') )
    
    return(df[["Date","Open"]])
    
# %% Main
#Dates de début et de fin du Backtest
start_date="2020-06-01"
end_date="2022-01-01"

start_dt = datetime.datetime.strptime(start_date,'%Y-%m-%d')
end_dt = datetime.datetime.strptime(end_date,'%Y-%m-%d')
periode = end_dt - start_dt
datetime_list = [start_dt + datetime.timedelta(i) for i in range(0,periode.days,30*2)]
time_list = [datetime_list[i].strftime("%Y-%m-%d") for i in range(len(datetime_list))]

Portfolio_value = []
Portfolio_Dates = []
final_price = 1
for i in range(1,len(time_list)-1):
    start_date_tweet = time_list[i-1]
    end_date_tweet = time_list[i]
    start_date_observation=time_list[i]
    end_date_observation=time_list[i+1]
    test=Algo(0.7,0.2,0.1,85,start_date_tweet,end_date_tweet)
    #DisplayResults(test)
    #ToString(test)
    list_buy,list_wait,list_sell = Compound(test)
    
    dict_Stock_Ticker = Get_Stock_Ticker()
    members = [dict_Stock_Ticker[i] for i in list(list_buy.keys()) ]
    eachweight = weightCalc(list_buy)
    weight = {dict_Stock_Ticker[i] : eachweight[i]*100 for i in list(list_buy.keys())}
    data = Portfolio(start_date_observation, end_date_observation, members, weight)
    print(start_date_observation + "-" + end_date_observation + " : " + str(weight))
    
    data = Normalisation(data, members,final_price)
    data = portfolioCalc(weight, data, "Portfolio")
    data2 = data
    
    #print(data2["Portfolio"][data2.shape[0]-1])
    final_price = data2["Portfolio"][data2.shape[0]-1]
    Portfolio_value.extend(list(data2["Portfolio"]))
    Portfolio_Dates.extend(list(data2["Date"]))
    
    
dfPortfolio = pd.DataFrame({"Date":Portfolio_Dates,"Portfolio":Portfolio_value})
#Graph(dfPortfolio)

#Attention le ficfier csv CAC40ESG ne contient des données que sur 2 ans
firstdata = TraitementCAC40ESGcsv()
firstdata["Date"] = pd.to_datetime(firstdata["Date"])
firstdata = firstdata.rename(columns={"Open":"CAC 40 ESG"})
Result = pd.merge(dfPortfolio,firstdata,on="Date")
Result["CAC 40 ESG"] = Result["CAC 40 ESG"]/Result["CAC 40 ESG"].iloc[0]
#Graph Comparaison
Graph(Result)

"""
members =["AAPL","TSLA"]
weight ={"AAPL":"50" , "TSLA":"50"}
data = Portfolio(start_date, end_date, members, weight)
data = Normalisation(data, members)
data2 = portfolioCalc(weight, data, "Portfolio")
Graph(data2)
"""



