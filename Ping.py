from numpy import *
def Maj(ch):#convertir une chaine de caractère en majuscule
    a=""
    for i in range(length(ch)):
        a+=ch[i].upper()
    return a
def Contain_mot(ch,tab):#verifier si un mot d'une phrase  existe dans un tableau
    L=ch.split()
    a=False
    for i in range(length(L)):
        for j in range(length(tab)):
            if (Maj(L[i])==Maj(tab[j])):
                a=True
    return a
def Coef_Env(text,tab,Neg,Coefficients):#tab: est un tableau N x 3 ( N lignes , 3 colonnes ) les 3 colonnes sont : émission,innovation,usage des ressources . N nombre de chaines de caractères.
    #text : liste qui contient les chaines de caractère de l'article en question , chaque element de ce tableau est une phrase
    #Neg : liste de termes/mots negatives
    #Coefficients: liste qui contient les coeffs des facteurs respectives ( émission,innovation,usage des ressources )
    coef=0
    for i in range(length(text)):
        if (Contain_mot(text[i],Neg)):
            a=-1
        else :
            a=1
        n,p=tab.shape
        for j in range(p):
            for k in range(n):
                if(Contain_mot(tab[k][j],text[i].split())):
                    coef+=Coefficients[i]*a
    return coef

                
            
            
               
        
