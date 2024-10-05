# # Load e imports

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('src\data_balanced.csv', encoding='utf-8')

df['result'].value_counts()

# renomeando colunas para um padrao _home e _away
colunas = ['goal', 'shots', 'blockedShots' ]
for coluna in colunas:
    df.rename(columns={coluna+'Home': coluna+'_home'}, inplace=True)
    df.rename(columns={coluna+'Away': coluna+'_away'}, inplace=True)

final_data_with_all_info = df.copy()

def calculate_efficiency_attack(df):
    df['shotAccuracy_home'] = df['shotsOngoal_home'] / (df['shots_home'] + 0.01)
    df['shotAccuracy_away'] = df['shotsOngoal_away'] / (df['shots_away'] + 0.01)
calculate_efficiency_attack(final_data_with_all_info)

def calculate_defense_performance(df):
    df['attackPressureOverTime_home'] = (df['shots_home'] + df['corners_home']) / df['minute']
    df['attackPressureOverTime_away'] = (df['shots_away'] + df['corners_away']) / df['minute']

    df['aggrressionOverTime_home'] = (df['redcards_home'] + df['yellowcards_home'] + df['fouls_home']) / df['minute']
    df['aggresssionOverTime_away'] = (df['redcards_away'] + df['yellowcards_away'] + df['fouls_away']) / df['minute']

    df['defensiveEfficacy_home'] = df['blockedShots_home'] / (df['shotsOngoal_home'] + 0.01) # chutes que foram bloqueados e chutes que foram no gol da equipe adversaria
    df['defensiveEfficacy_away'] = df['blockedShots_away'] / (df['shotsOngoal_away'] + 0.01) 

    df['taklesOverTime_home'] = df['tackles_home'] / df['minute']
    df['taklesOverTime_away'] = df['tackles_away'] / df['minute']
calculate_defense_performance(final_data_with_all_info)

def calculate_passing_performance(df):
    df['possessionControl'] = abs(df['possessiontime_home'] - df['possessiontime_away'])
    df['passRisk_home'] = df['offsides_home'] / (df['possessiontime_home'] + 0.01)
    df['passRisk_away'] = df['offsides_away'] / (df['possessiontime_away'] + 0.01)
calculate_passing_performance(final_data_with_all_info)

def calculate_cards(df):
    df['TotalCards_home'] = df['redcards_home'] + df['yellowcards_home']
    df['TotalCards_away'] = df['redcards_away'] + df['yellowcards_away']
calculate_cards(final_data_with_all_info)

df = final_data_with_all_info
final_data_with_all_info = df.copy()

# Função para filtrar ligas com base no número mínimo de partidas
def filter_leagues(df, league_col, matches, min_matches=10):
    # Agrupa o DataFrame por liga e conta o número único de partidas para cada liga
    league_game_counts = df.groupby(league_col)[matches].nunique()
    # Filtra para manter apenas as ligas com um número de partidas igual ou maior que min_matches
    leagues_filtered = league_game_counts[league_game_counts >= min_matches].index
    # Filtra o DataFrame original para incluir apenas linhas das ligas selecionadas
    filtered_data = df[df[league_col].isin(leagues_filtered)]
    return filtered_data

def balance_data(df, league_col='league', result_col='result'):
    leagues = df[league_col].unique()
    # Lista para armazenar os DataFrames balanceados para cada liga
    balanced_dfs = []

    # Cria uma cópia do DataFrame para não alterar a coluna 'minute' original
    df_copy = df.copy()

    # Itera sobre cada liga para balancear os dados
    for league in leagues:
        # Filtra o DataFrame para incluir apenas dados da liga atual
        league_df = df_copy[df_copy[league_col] == league]
        
        # Arredondando os minutos para o inteiro mais próximo para fins de balanceamento
        league_df['minute_rounded'] = league_df['minute'].round()

        # Selecionando os registros onde 'result' é 1
        result_1 = league_df[league_df[result_col] == 1]

        # Contando os minutos únicos arredondados e suas ocorrências em 'result' 1
        minutes_counts = result_1['minute_rounded'].value_counts()

        # Selecionando registros onde 'result' é 0 e amostrando aleatoriamente com base no número de ocorrências do mesmo minuto arredondado
        result_0_sample = pd.DataFrame()
        for minute, count in minutes_counts.items():
            # Filtra registros com 'result' 0 e o minuto arredondado correspondente
            potential_samples = league_df[(league_df['result'] == 0) & (league_df['minute_rounded'] == minute)]
            
            # Verifica se há registros suficientes para amostrar
            if potential_samples.shape[0] >= count:
                sample = potential_samples.sample(n=count, replace=True, random_state=42)
            else:
                # Se não houver registros suficientes, considera todos os registros disponíveis
                sample = potential_samples

            # Removendo a coluna 'minute_rounded' para manter o formato original de 'minute'
            sample = sample.drop(columns=['minute_rounded'])

            result_0_sample = pd.concat([result_0_sample, sample])

        # Combinando os dois conjuntos de dados para formar um novo dataframe balanceado
        balanced_dfs.append(pd.concat([result_1.drop(columns=['minute_rounded']), result_0_sample]))
    
    # Combina todos os DataFrames balanceados em um único DataFrame
    balanced_data = pd.concat(balanced_dfs).reset_index(drop=True)
    return balanced_data


print("Contando partidas por time...")
total_matches_per_team = len(df['match_id'].unique())
print("Total de partidas:", total_matches_per_team)

print("\nFiltrando dados de ligas...")
filtered_data = filter_leagues(df, 'league', 'match_id')
print("Dados filtrados:\n")
print(filtered_data['league'].value_counts())

print("\nBalanceando dados...")

balanced_data = balance_data(filtered_data)

print("Dados balanceados:\n")
print(balanced_data['result'].value_counts())

league_distribution = balanced_data.groupby(['league', 'result']).size().unstack()
sorted_leagues = league_distribution.sum(axis=1).sort_values(ascending=False).head(100).index

print("Contando partidas depois dos filtros...")
total_matches_per_team = len(balanced_data['match_id'].unique())
print("Total de partidas:", total_matches_per_team)

# plt.figure(figsize=(15, 10))
# ax = league_distribution.loc[sorted_leagues].plot(kind='bar', stacked=True, ax=plt.gca())
# plt.title('Distribuição do Resultado por Liga')
# plt.ylabel('Número de Jogos')
# plt.xlabel('Liga')
# plt.tight_layout()
# plt.xticks(rotation=90)

# for p in ax.patches:
#     width = p.get_width()
#     height = p.get_height()
#     x, y = p.get_xy() 
#     ax.annotate(f'{height:.0f}', (x + width/2, y + height), ha='center')

# plt.show()
# plt.clf()  

# Ordenando o DataFrame
df.sort_values(by=['match_id', 'minute'], inplace=True)

balanced_data.reset_index(drop=True, inplace=True)

balanced_data.to_csv("src\data_live_engineer_filtered.csv", index=False, encoding="utf-8")
