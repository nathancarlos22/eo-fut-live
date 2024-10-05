# # Imports e carregamentos

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import pickle

import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('src\data_live_engineer.csv', encoding='utf-8')

# # Salvando dados
df.to_csv("src\data_live_engineer_filtered.csv", index=False, encoding="utf-8")
