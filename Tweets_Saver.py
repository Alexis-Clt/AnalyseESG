#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 30 12:29:15 2022

@author: user
"""
from Twitter import TwitterClient
import datetime
from DataSet import DataSet
import time
import csv

def SaveTweets (Company,start,end):
    client = TwitterClient()
    collected_data=client.lastTweets(Company,start,end).data
    file = open('Tweets2.csv','a')
    obj = csv.writer(file)
    if collected_data!=None:
        for i in range(len(collected_data)):
            data=(Company,start,end,collected_data[i].text)
            obj.writerow(data)
        file.close()
        print("Data written for the company ", {Company})
    else:
        print("No data for the company", {Company})

    
def Write_Csv(Companies,start,end):
    start = datetime.datetime.strptime(start,'%Y-%m-%d')
    end = datetime.datetime.strptime(end,'%Y-%m-%d')
    periode = end - start
    datetime_list = [start + datetime.timedelta(i) for i in range(0,periode.days,30)]
    for i in datetime_list:
        now = i
        td1 = datetime.timedelta(days = 1)
        td2 = datetime.timedelta(days = 30)
        end = now - td1
        start = end - td2
        print(end,start)
        for i in Companies.iteritems():
            SaveTweets(i[1], start, end)
            time.sleep(1)
        time.sleep(60*2)
        

if __name__ == '__main__' :
    notreDataSet=DataSet("/Users/user/Documents/Finance/CAC40_valeurs_ESG.xlsx",0.7,0.2,0.1,0)
    #file = open('Tweets.csv','w') #dans celui-là j'ai du 02 Janvier 2020 au 21 Mai 2022
    #obj = csv.writer(file)
    #data=("Company","Start","End","Tweet")
    #obj.writerow(data)
    #file.close()
    file=open("Tweets2.csv",'w') #de 2015 au 02 Janvier 2020
    obj = csv.writer(file)
    data=("Company","Start","End","Tweet")
    obj.writerow(data)
    file.close()
    start="2015-02-01" #pour commencer un mois plus tôt
    end="2020-01-01" #jusqu'au 1 janvier 2020
    Write_Csv(notreDataSet.titres.Company, start, end)
    
    
    