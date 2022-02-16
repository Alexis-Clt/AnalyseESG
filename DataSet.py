#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 15:38:20 2022

@author: user
"""
import numpy as np
import pandas as pd
import csv

class DataSet : #cette classe gère le fichier excel du dataset => va récupérer les coefs en entrée de l'interface
    
    def __init__(self,path):
        self.path=path
        self.titres = self.getOurCompaniesCoefs(0.7,0.2,0.1,75) #version avec coefs
        #self.titres = self.getOurCompaniesMean(75) sans coefs
        
    def getOurCompaniesMean(self,expectedscore):
        initialTable = pd.read_excel(self.path)
        datas = {"Company" : initialTable["Company"],
            "Ticker": initialTable["Ticker"],
            "ESG Score": initialTable["ESG Mean score"]}
        companies = pd.DataFrame(datas)
        companies = companies.drop(range(40, 44))
        for i in range(40):
            if (companies["ESG Score"][i]<expectedscore) : companies = companies.drop(i) 
        return companies
    
    def getOurCompaniesCoefs(self,Ecoef,Scoef,Gcoef,expectedscore):
        initialTable = pd.read_excel(self.path)
        datas = {"Company" : initialTable["Company"],
            "Ticker": initialTable["Ticker"],
            "E Score": initialTable["ENVIRONMENT"],
            "S Score": initialTable["SOCIAL"],
            "G Score": initialTable["GOVERNANCE"],
            "Final Score": initialTable["ENVIRONMENT"]*Ecoef+ initialTable["SOCIAL"]*Scoef+initialTable["GOVERNANCE"]*Gcoef}
        companies = pd.DataFrame(datas)
        companies = companies.drop(range(40, 44))
        for i in range(40):
            if (companies["Final Score"][i]<expectedscore) : companies = companies.drop(i) 
        return companies
    
    
if __name__ == "__main__":
    notreDataSet=DataSet("/Users/user/Documents/Finance/CAC40_valeurs_ESG.xlsx")
    print (notreDataSet.titres)
    
