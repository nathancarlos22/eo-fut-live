# ## Objetivo específico do trabalho: analisar a base construída com dados de jogos esportivos ao vivo e prever um evento específico e isolado por meio de automl e redes neurais com bons resultados

# # Load and imports

import pandas as pd

import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

df05ht = pd.read_csv('src\data_live_scores_full.csv', encoding='utf-8')
print(df05ht.shape)

date_object = pd.to_datetime(df05ht['date'], format='%Y-%m-%d')

min_date = date_object.min()
max_date = date_object.max()

print("Os dados vão de {} até {}".format(min_date, max_date))

df05ht.drop_duplicates(subset=df05ht.columns.difference(['match_id']), keep='last')

# # Analisando e tratando os dados

df = df05ht.copy()
print(f'Dimensão do DataFrame antes remoção: {df05ht.shape}')
print(f'Valores únicos de minutos antes da conversão: {df05ht.minute.unique()} \n')
registros_duplicados = len(df05ht[df05ht.duplicated()])
print(f'Registros duplicados: {registros_duplicados}')
df.drop_duplicates(keep='last', inplace=True)

registros_nulos = df.isnull().sum().sum()
print(f'Registros nulos: {registros_nulos}\n')
df.dropna(inplace=True)

df_optimized = df.copy()

for col in df_optimized.select_dtypes(include=['object']).columns:
    num_unique_values = df_optimized[col].nunique()
    num_total_values = len(df_optimized[col])
    if num_unique_values / num_total_values < 0.5:  # Convert to category if less than 50% unique values
        df_optimized[col] = df_optimized[col].astype('category')

# Convert integer columns to the smallest possible integer type
int_columns = df_optimized.select_dtypes(include=['int']).columns
df_optimized[int_columns] = df_optimized[int_columns].apply(pd.to_numeric, downcast='integer')

# Convert float columns to the smallest possible float type
float_columns = df_optimized.select_dtypes(include=['float']).columns
df_optimized[float_columns] = df_optimized[float_columns].apply(pd.to_numeric, downcast='float')

# Check the memory usage after optimization
memory_usage_before = df.memory_usage(deep=True).sum() / 1024 ** 2  # in MB
memory_usage_after = df_optimized.memory_usage(deep=True).sum() / 1024 ** 2  # in MB

df = df_optimized.copy()

# Copiar o DataFrame original
df_final_reset = df.copy()
df_final_reset = df_final_reset.reset_index(drop=True)

# Recalcular o resultado do jogo (1 para vitória em casa, 0 para empate, -1 para derrota em casa)
df_final_reset['match_result'] = df_final_reset.apply(lambda row: 1 if row['goalHome'] > row['goalAway'] 
                                                      else (0 if row['goalHome'] == row['goalAway'] else -1), axis=1)

# Calcular as taxas de vitória, empate e derrota por liga
# Proporção de vitórias, empates e derrotas para times de casa
df_final_reset['win_rate_home'] = df_final_reset.groupby('league')['match_result'].transform(lambda x: (x == 1).mean())
df_final_reset['draw_rate_home'] = df_final_reset.groupby('league')['match_result'].transform(lambda x: (x == 0).mean())
df_final_reset['loss_rate_home'] = df_final_reset.groupby('league')['match_result'].transform(lambda x: (x == -1).mean())

# Proporção de vitórias, empates e derrotas para times de fora (invertendo o resultado do jogo)
df_final_reset['win_rate_away'] = df_final_reset.groupby('league')['match_result'].transform(lambda x: (x == -1).mean())
df_final_reset['draw_rate_away'] = df_final_reset.groupby('league')['match_result'].transform(lambda x: (x == 0).mean())
df_final_reset['loss_rate_away'] = df_final_reset.groupby('league')['match_result'].transform(lambda x: (x == 1).mean())

# Substituir -0.0 por 0.0 no DataFrame
df_final_reset.replace(-0.0, 0.0, inplace=True)

# Filtrar para incluir apenas as colunas relevantes
df_final_result_fixed = df_final_reset[['date', 'homeTeam', 'awayTeam', 'goalHome', 'goalAway', 'match_result', 
                                        'win_rate_home', 'draw_rate_home', 'loss_rate_home',
                                        'win_rate_away', 'draw_rate_away', 'loss_rate_away']].sort_values(by='date')

df_full = df_final_reset.copy()

df = df_full.copy()

# Calcular a média de gols marcados em casa e fora de todas as ligas
avg_home_goals = df['goalHome'].mean()
avg_away_goals = df['goalAway'].mean()

# Calcular a média de gols marcados e sofridos por liga em casa e fora
home_goals_scored_avg_per_league = df.groupby('league')['goalHome'].mean()
away_goals_scored_avg_per_league = df.groupby('league')['goalAway'].mean()
home_goals_conceded_avg_per_league = df.groupby('league')['goalAway'].mean()
away_goals_conceded_avg_per_league = df.groupby('league')['goalHome'].mean()

# Calcular as forças de ataque e defesa comparando com a média geral
df['f_attack_home'] = df.apply(lambda row: home_goals_scored_avg_per_league[row['league']] / avg_home_goals, axis=1)
df['f_attack_away'] = df.apply(lambda row: away_goals_scored_avg_per_league[row['league']] / avg_away_goals, axis=1)

df['f_defensive_home'] = df.apply(lambda row: (avg_away_goals / home_goals_conceded_avg_per_league[row['league']])
                                   if home_goals_conceded_avg_per_league[row['league']] != 0 else 0, axis=1)

df['f_defensive_away'] = df.apply(lambda row: (avg_home_goals / away_goals_conceded_avg_per_league[row['league']])
                                   if away_goals_conceded_avg_per_league[row['league']] != 0 else 0, axis=1)

# apenas o primeiro tempo
df = df[df['minute'].str.match(r"^(45\+([0-9]|\d+):\d+|4[0-4]:\d+|[0-3]?[0-9]:\d+|45:([0-5][0-9]|\d))$")]

# Assuming that goalHome and goalAway are the goals scored in the first half.
# Calculate the proportion of games where more than 0.5, 1.5, 2.5 goals were scored in the first half for home and away teams.

# Proporções para times da casa (home teams)
df['05ht_home'] = df.groupby('league')['goalHome'].transform(lambda x: (x > 0.5).mean())
df['15ht_home'] = df.groupby('league')['goalHome'].transform(lambda x: (x > 1.5).mean())
df['25ht_home'] = df.groupby('league')['goalHome'].transform(lambda x: (x > 2.5).mean())

# Proporções para times de fora (away teams)
df['05ht_away'] = df.groupby('league')['goalAway'].transform(lambda x: (x > 0.5).mean())
df['15ht_away'] = df.groupby('league')['goalAway'].transform(lambda x: (x > 1.5).mean())
df['25ht_away'] = df.groupby('league')['goalAway'].transform(lambda x: (x > 2.5).mean())

# Função para converter o formato de tempo para decimal
def convert_to_decimal(time_str):
    # Separar os minutos dos segundos
    if '+' in time_str:
        main_minutes, extra = time_str.split('+')
        extra_minutes, seconds = extra.split(':')
        total_minutes = int(main_minutes) + int(extra_minutes)
    else:
        total_minutes, seconds = time_str.split(':')
        total_minutes = int(total_minutes)
    
    # Converter segundos em fração de minutos e adicionar aos minutos
    total_seconds = int(seconds)
    # decimal_time = total_minutes + total_seconds / 60
    decimal_time = float(f'{total_minutes}.{total_seconds}')

    # return float(f'{decimal_time:.2f}')
    return decimal_time
# Aplicando a função na coluna 'minute'
df['minute_decimal'] = df['minute'].apply(convert_to_decimal)

# Removendo os minutos iguais a 0
df = df[df['minute_decimal'] != 0]
df['minute'] = df['minute_decimal']
df.drop(columns=['minute_decimal'], inplace=True)

print(f'Valores únicos de minutos após a conversão: {df.minute.unique()} \n')

print(f'Dimensão do DataFrame após remoção: {df.shape}')
print(f'Total de registros retirados: {df05ht.shape[0] - df.shape[0]}')

for l in df['league'].unique():
    print(l)

df_ht = df.copy()

# ordenar por data
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df.sort_values(by=['date', 'minute'], inplace=True)

df = df_ht.copy()

# Configurações iniciais
janela_tempo = 5
# Ordenando o DataFrame por 'match_id' e 'minute'
df.sort_values(by=['match_id', 'minute', 'goalHome', 'goalAway'], inplace=True, ascending=True)
df.drop_duplicates(subset=['match_id', 'minute'], keep='last', inplace=True)
df.reset_index(drop=True, inplace=True)

# Função para identificar os últimos registros antes do primeiro gol em cada partida
def marcar_ultimos_antes_do_gol(df):
    # Identificando o índice do primeiro gol
    primeiro_gol_idx = df[(df['goalHome'] > 0) | (df['goalAway'] > 0)].index.min()
    # Verificando se existe um gol na partida
    if pd.notna(primeiro_gol_idx):
        # Calculando o índice inicial para marcar os x registros anteriores
        inicio_intervalo = max(primeiro_gol_idx - janela_tempo, 0)
        # Marcando os registros
        df.loc[inicio_intervalo:primeiro_gol_idx - 1, 'result'] = 1
        # Retirando o resto dos registros
        df = df.loc[:primeiro_gol_idx]
    return df

# Aplicando a função a cada grupo de partida
df = df.groupby('match_id').apply(marcar_ultimos_antes_do_gol)

# retirar registros onde houve gol
df = df[(df['goalHome'] == 0) & (df['goalAway'] == 0)]

# Calculando o tempo de posse de bola
total_passes = df['passes_away'] + df['passes_home']
df['possessiontime_away'] = round((df['passes_away'] / total_passes) * 100)
df['possessiontime_home'] = round((df['passes_home'] / total_passes) * 100)

df['possessiontime_home'].fillna(method='bfill', inplace=True)
df['possessiontime_away'].fillna(method='bfill', inplace=True)

print("\nDados de posse de bola:\n", df[['possessiontime_away', 'possessiontime_home']].head())

# Renomeando colunas
new_column_names = {'fouls_won_away': 'fouls_away', 'fouls_won_home': 'fouls_home'}
df.rename(columns=new_column_names, inplace=True)
print("\nColunas renomeadas:\n", df.columns)

# Removendo colunas desnecessárias e limpando o DataFrame
columns_to_drop = ["date", 'passes_home', 'passes_away', 'fouls_c_home', 'fouls_c_away', 'assistsHome',
       'assistsAway']
df.drop(columns=columns_to_drop, inplace=True)
print("\nDataFrame após remover colunas:\n", df.columns)

df.reset_index(drop=True, inplace=True)
print(f'Dimensão do DataFrame após modificações: {df.shape}')

# ## Tratando o formato das ligas para ligas existentes 

# Obtendo ligas únicas
leagues_opta = df['league'].unique()
print("Ligas únicas:", leagues_opta)

# Iterando através das ligas únicas
for league in leagues_opta:
    print("Liga atual:", league)

# Mapeamento de nomes de ligas
name_mapping = {
    'England - Premier League': 'England - Premier League',
    'Germany - Bundesliga': 'Germany - Bundesliga',
    'Spain - Primera División': 'Spain - La Liga',
    'France - Ligue 1': 'France - Ligue 1',
    'Italy - Serie A': 'Italy - Serie A',
    'USA - MLS': 'USA - Major League Soccer',
    'Brazil - Serie A': 'Brazil - Serie A',
    'Netherlands - Eredivisie': 'Netherlands - Eredivisie',
    'England - Championship': 'England - Championship',
    'Portugal - Primeira Liga': 'Portugal - Liga Portugal',
    'Romania - Liga I': 'Romania - Liga 1',
    "World - FIFA Women's World Cup": 'World - World Cup Women',
    'England - League One': 'England - League One',
    'England - League Two': 'England - League Two',
    'Europe - UEFA Europa Conference League': 'Europe - Europa Conference League',
    'England - League Cup': 'England - Carabao Cup',
    'Europe - UEFA Super Cup': 'Europe - Uefa Super Cup',
    'Europe - UEFA Champions League': 'Europe - Champions League',
    'Germany - DFB Pokal': 'Germany - DFB Pokal',
    'Italy - Coppa Italia': 'Italy - Coppa Italia',
    'Scotland - Premiership': 'Scotland - Premiership',
    'Germany - Super Cup': 'Germany - Super Cup',
    'South America - CONMEBOL Libertadores': 'South America - Copa Libertadores',
    'England - Community Shield': 'England - Community Shield',
    'N/C America - Concacaf Gold Cup': 'World - CONCACAF Gold Cup',
    'Europe - UEFA U21 Championship': 'Europe - Euro U21',
    'Australia - A-League Men': 'Australia - A-League',
    'Portugal - Play-offs 1/2': 'Portugal - Primeira Liga - Play-offs',
    'Europe - UEFA European Championship Qualifiers': 'Europe - Euro Qualification',
    'Germany - Play-offs 1/2': 'Germany - Bundesliga Play-offs',
    'Europe - UEFA Nations League': 'Europe - UEFA Nations League',
    'Europe - UEFA Europa League': 'Europe - Europa League',
    'England - FA Cup': 'England - FA Cup',
    'Spain - Copa del Rey': 'Spain - Copa Del Rey',
    'World - FIFA World Cup': 'World - FIFA World Cup',
    'France - Coupe de France': 'France - Coupe de France',
    'Spain - Super Cup': 'Spain - Super Cup',
    'Italy - Super Cup': 'Italy - Super Cup',
    'World - FIFA Club World Cup': 'World - FIFA Club World Cup',
    'Argentina - Liga Profesional Argentina': "Argentina - Superliga",
    'Brazil - Paulista A1': 'Brazil - Paulista A1',
    'Brazil - Copa do Brasil': 'Brazil - Copa Do Brasil',
    'Denmark - Superliga':'Denmark - Superliga',
    'Mexico - Liga MX': 'Mexico - Liga MX',
    'Greece - Super League 1': 'Greece - Super League',
    'Asia - AFC Champions League': 'Asia - AFC Champions League', 
    'South America - CONMEBOL Sudamericana': 'South America - Copa Sudamericana', 
    'Spain - Segunda División': 'Spain - La Liga 2',
    'Saudi Arabia - Saudi League': 'Saudi Arabia - Pro League',
    'Italy - Serie B': 'Italy - Serie B',
    'Japan - J1 League': 'Japan - J-League',
    'South America - CONMEBOL World Cup Qualifiers': 'World - WC Qualification South America',
    'Europe - UEFA World Cup Qualifiers': 'Europe - WC Qualification Europe', 
    "Europe - UEFA Women's Championship": "Europe - UEFA Women's EURO",
    "France - Trophée des Champions": 'France - Super Cup',
    'Brazil - Supercopa do Brasil': 'Brazil - Supercopa do Brasil',
    'South America - CONMEBOL Recopa': 'South America - Recopa Sudamericana',
    'Europe - UEFA European Championship': 'Europe - European Championship', 
    'N/C America - Leagues Cup': 'North & Central America - Leagues Cup',
    'South America - CONMEBOL Copa America': 'South America - Copa America',
    'World - Friendlies': 'World - International Friendlies',
    'Africa - CAF Africa Cup of Nations': 'Africa - Africa Cup of Nations',
    'Asia - AFC Asian Cup': 'Asia - AFC Asian Cup',
    'World - Friendlies Women': 'World - International Friendlies Women',
    "Europe - UEFA Women's Championship Qualification": "Europe - UEFA Women’s EURO Qualification",
    'Asia - AFC Champions League Elite': 'Asia - AFC Champions League Elite',
    'Europe - UEFA Conference League': 'Europe - Europa Conference League',
    'World - Olympics': 'World - Olympics',
    'World - Olympics Women': 'World - Olympics Women',
    'Belgium - First Division A': 'Belgium - First Division A',
    'Türkiye - Süper Lig': 'Turkey - Super Lig',
    'Romania - Play-offs 1/2': 'Romania - Liga 1 Play-offs',

}
print("\nTamanho do mapeamento de nomes de ligas:", len(name_mapping))

# Verificando o número de ligas únicas
print("Número de ligas únicas:", len(leagues_opta))
print("Número de ligas únicas após o mapeamento:", len(name_mapping))

# Atualizando os nomes das ligas no DataFrame
# df['league'] = df['league'].replace(name_mapping)

# Verificando algumas linhas do DataFrame após a atualização dos nomes das ligas
for league in df['league'].unique():
    print("Liga atual no dataframe:", league)

# df.to_csv('data_trated.csv', index=False, encoding='utf-8')

# ## Balanceamento de Dados e Visualização da Distribuição de Resultados por Liga

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
tota_leagues = len(df['league'].unique())
print("Total de ligas:", tota_leagues)
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
tota_leagues = len(balanced_data['league'].unique())
print("Total de ligas:", tota_leagues)
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
balanced_data.to_csv("src\data_balanced.csv", index=False, encoding='utf-8')
