import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import nltk
from nltk.tokenize import word_tokenize

import os
for f in os.listdir("C:/Users/alexi/OneDrive/Documents/ESILV/PING/VI-AnalyseESG/Analyse du sentiment"):
	print(f)

data = pd.read_csv("Training.csv")