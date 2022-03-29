#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 14:00:19 2022

@author: user
"""
# %% zone de l'algo

from SentimentIntensityAnalyzer import SentimentIntensityAnalyzerClass
from Twitter import TwitterClient
import YahooFinance
from DataSet import DataSet
import matplotlib.pyplot as plt

def Algo(Ecoef,Scoef,Gcoef,expectedscore):
    OurDataSet=DataSet("/Users/user/Documents/Finance/CAC40_valeurs_ESG.xlsx", Ecoef,Scoef,Gcoef,expectedscore)
    ssresultyahoo=[]
    ssresulttwitter=[]
    sumcyahooresult=[]
    sumctwitterresult=[]
    companies=[]
    esgscores=[]
    tupleresult=[]
    for i in OurDataSet.titres["Company"]:
        ssresultyahoo.append(YahooFinance.YahooFinanceSS(YahooFinance.CleaningData(str(i))))  #liste de dictionnaires selon company
        ssresulttwitter.append(TwitterClient.TwitterSS(str(i)))  #liste de dictionnaires selon company
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
    
    
        
    

# %% zone du main

if __name__ == '__main__' :
    test=Algo(0.7,0.2,0.1,85)
    DisplayResults(test)
    ToString(test)
     