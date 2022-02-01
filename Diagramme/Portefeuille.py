import numpy as np
import yfinance as yf
import pandas as pd
import datetime


class Portefeuille :
    def __init__(self, soldeEspece, titres, frais_achat, frais_vente):
        self.soldeEspece=soldeEspece
        self.titres=titres
        self.frais_achat = frais_achat
        self.frais_vente = frais_vente
    def __init__(self, solde_initial, path, expectedScore, frais_achat, frais_vente):
        #solde_initial : le solde initial du portefeuille
        #path : le chemin d'accès du fichier excel contenant l'ensemble des entreprises de la cible
        #expectedScore : le score ESG minimal qu'une entreprise doit avoir pour rentrer dans le portefeuille. Les scores ESG doivent êtres stockés dans une colonne "Finale Score" du fichier .xlsx
        #frais_achat : frais de courtiers à l'achat, compris entre 0 et 1
        #frais_vente : frais de courtiers à la vente, compris entre 0 et 1
        self.soldeEspece = solde_initial
        self.frais_achat = frais_achat
        self.frais_vente = frais_vente
        self.titres = self.getOurCompanies(path, expectedScore)
    def getOurCompanies(self, path, expectedscore):
        #Méthode utilisée pour __init__ qui récupère (depuis un fichier .xlse) et renvoie sous forme de pd.dataframe l'ensembles des entreprises suceptibles d'être comprises dans le portefeuille
        #path : le chemin d'accès du fichier excel contenant l'ensemble des entreprises de la cible
        #expectedScore : le score ESG minimal qu'une entreprise doit avoir pour rentrer dans le portefeuille. Les scores ESG doivent êtres stockés dans une colonne "Finale Score" du fichier .xlsx
        initialTable = pd.read_excel(path)
        datas = {"Company" : initialTable["Company"],
            "Ticker": initialTable["Ticker"],
            "ESG Score": initialTable["Final Score"],
            "Nombre":np.zeros(initialTable["Company"].size)}
        companies = pd.DataFrame(datas)
        companies = companies.drop(range(40, 44))
        for i in range(40):
            if (companies["ESG Score"][i]<expectedscore) : companies = companies.drop(i) 
        return companies

    def acheter(self, action, nombre=1):
        # Simule l'achat d'une action donnée pour le portefeuille
        # action : nom de l'entreprise
        # nombre : nombre d'actions achetées
        ligne = self.titres.index[self.titres["Company"]==action]
        code = self.titres.at[ligne[0], "Ticker"]
        ticker = yf.Ticker(code)
        prixActuel =ticker.info['regularMarketPrice']
        achetees = 0
        while(achetees<nombre and self.soldeEspece > prixActuel):
             achetees +=1
             self.soldeEspece -= prixActuel*(1+frais_achat)
             self.titres.at[ligne[0], "Nombre"]+=1
        return achetees
    def vendre(self, action, nombre=1):
        # Simule la vente d'une action donnée pour le portefeuille
        # action : nom de l'entreprise
        # nombre : nombre d'actions vendue
        ligne = self.titres.index[self.titres["Company"]==action]
        code = self.titres.at[ligne[0], "Ticker"]
        ticker = yf.Ticker(code)
        prixActuel =ticker.info['regularMarketPrice']
        vendues = 0
        while(vendues<nombre and self.titres.at[ligne[0], "Nombre"]>0):
             vendues +=1
             self.soldeEspece += prixActuel*(1-frais_vente)
             self.titres.at[ligne[0], "Nombre"]-=1
        return vendues
    def verserDividende(self, action):
        # Vérifie et simule le cas échéan le versage des dividendes tombés la veille, à ne faire tourner qu'une fois par jour
        # action : le nom de l'entreprise
        ligne = self.titres.index[self.titres["Company"]==action]
        if(self.titres.at[ligne[0], "Nombre"]>0):
            code = self.titres.at[ligne[0], "Ticker"]
            div=yf.Ticker(code).dividends
            hier = datetime.date.today()-datetime.timedelta(days=1)
            dernier_div = div.index[div.size-1].date()
            if (hier==dernier_div): self.soldeEspece+= self.titres.at[ligne[0], "Nombre"]*div.iloc[div.size-1]
    def gestionDividendes(self):
        #actualise tous les dividendes de la journée, à appliquer une fois par jour
        for index in self.titres.index:
            self.verserDividende(self.titres.at[index, "Company"])

    def valeur(self):
        # Calcule la valeur du portefeuille, la méthode peut être optimisée si on arrive à récupérer tous les yf.Ticker dans un seul call yf.Tickers
        valeur = self.soldeEspece
        symboles = self.titres["Ticker"]
        for index in self.titres.index:
            if (self.titres.at[index, "Nombre"]>0):
                ticker = yf.Ticker(symboles[index])
                valeur+= self.titres.at[index, "Nombre"]*ticker.info['regularMarketPrice']
        return valeur
    def __str__(self):
        # Décris le portefeuille : son solde, ses actions et sa valeur
        toreturn= "Solde espèce : "+str(self.soldeEspece)+"\n"
        for index in self.titres.index:
            if (self.titres.at[index, "Nombre"]>0):
                toreturn += str(self.titres.at[index, "Nombre"])+ " " + str(self.titres.at[index, "Company"]) + " - " + str(self.titres.at[index, "Ticker"]) +"\n"
        return toreturn + "La valeur totale du portefeuille est "+str(self.valeur())


if __name__ == "__main__":
    solde_initial = 10000 #Vérifier les parametres
    path = "CAC40_valeurs_ESG.xlsx" 
    scoreESG = 78
    frais_achat = 0
    frais_vente = 0
    notrePortefeuille = Portefeuille(solde_initial, path, scoreESG, frais_achat, frais_vente)
    notrePortefeuille.acheter("AXA")
    notrePortefeuille.acheter("AXA", 2)
    notrePortefeuille.gestionDividendes()
