import requests
import traceback
import requests
import time
from datetime import datetime
import pandas as pd
import pickle
import warnings
import keras
import joblib
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
import numpy as np
from fuzzywuzzy import fuzz

def calculate_similarity(vector, reference):
    return np.array([fuzz.ratio(reference, x) for x in vector])


warnings.filterwarnings('ignore')

load_dotenv()

df = pd.read_csv('src/data_live_engineer_filtered.csv', encoding='utf-8')

chat_id = os.getenv('CHAT_ID')
token = os.getenv('TOKEN')

def sendMenssageTelegram(message):
    try:
        url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
        response = requests.get(url_base)
        print(message)
        result = response.json()['result']['message_id']
        return result
    except Exception as e:
        print(e)
        return None

def editMessageTelegram(message_id, new_message):
    url_base = f'https://api.telegram.org/bot{token}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={new_message}'
    requests.get(url_base)

id_jogos_mensagem = {
    "id_over05HTmodel": [],
    "id_over05HTAutoml": [],
}


id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0


text = ' '
resultados = {}

minutoss = datetime.now().minute
flag = 0

# Carregar o modelo do arquivo
# model = keras.models.load_model('models/model_redeht.h5')
# carregar modelo torch
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader

# Definindo o modelo
class NeuralNetwork(nn.Module):
    def __init__(self, input_size, neurons, dropout_rate, activation_type, normalization_type):
        super(NeuralNetwork, self).__init__()
        layers = []


        # Primeira camada
        layers.append(nn.Linear(input_size, neurons[0]))
        if normalization_type == 'batch':
            layers.append(nn.BatchNorm1d(neurons[0]))
        layers.append(self._get_activation(activation_type))
        if dropout_rate > 0:
            layers.append(nn.Dropout(dropout_rate))

        # Camadas ocultas
        for i in range(1, len(neurons)):
            layers.append(nn.Linear(neurons[i-1], neurons[i]))
            if normalization_type == 'batch':
                layers.append(nn.BatchNorm1d(neurons[i]))
            layers.append(self._get_activation(activation_type))
            if dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))


        # Camada de saída
        self.layers = nn.Sequential(*layers)
        self.output = nn.Linear(neurons[-1], 1)
        self.sigmoid = nn.Sigmoid()

    def _get_activation(self, activation_type):
        if activation_type == 'relu':
            return nn.ReLU()
        elif activation_type == 'tanh':
            return nn.Tanh()
        elif activation_type == 'leaky_relu':
            return nn.LeakyReLU()
        elif activation_type == 'elu':
            return nn.ELU()
        # Adicione outras funções de ativação conforme necessário
        else:
            raise ValueError(f"Tipo de ativação desconhecido: {activation_type}")

    def forward(self, x):
        x = self.layers(x)
        x = self.output(x)
        x = self.sigmoid(x)
        return x

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")

# Definição da arquitetura do modelo com a mesma configuração usada para treinar e salvar o estado do modelo
input_size = 72  # Certifique-se de que 'X_train' está definido e é acessível neste ponto do seu código
lr = 1e-05  # Voltar para a taxa de aprendizado anterior para estabilidade
batch_size = 64
num_layers = 4  # Voltar para a quantidade de camadas anterior
neurons = (921, 768, 615, 461)  # Ajustar número de neurônios, mantendo uma distribuição densa
dropout_rate = 0.2  # Reduzir a taxa de dropout
activation_type = 'relu'  # Manter ReLU
normalization_type = 'batch'  # Manter normalização em lote


model = NeuralNetwork(input_size, neurons, dropout_rate, activation_type, normalization_type)

checkpoint = torch.load('models/model_redeht.pth',map_location=torch.device('cpu'))
model.load_state_dict(checkpoint)
model = model.to(device)

# model.load_state_dict(torch.load('models/model_redeht.pth',map_location=torch.device('cpu')))
model.eval()  # Coloca o modelo em modo de avaliação

model_Automl = pickle.load(open('./models/tpot_model.pkl', 'rb'))

preprocessor = pickle.load(open('models/preprocessor.pickle', 'rb'))

id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

id_evento = ''

lucro = 0
valorEsperado = 0
state = ''

value_pred_rede = 0
value_pred_automl = 0

df_jogos = {}

while True:
    print('🤖 Procurando jogos...\n')

    try:

        url = "https://api.sportsanalytics.com.br/api/v1/fixtures-svc/fixtures/livescores"

        querystring = {"matchSlug": "\"31-01-2023-union-berlin-vfl-wolfsburg\"", "sportSlug": "soccer",
                       "include": "weatherReport,additionalInfo,league,stats,pressureStats,probabilities"}

        payload = ""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Cookie': 'route=f69973370a0dd0883a57c7b955dfc742',
            'If-Modified-Since': 'Sat, 05 Aug 2023 14:38:28 GMT',
            'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }

        response = requests.request(
            "GET", url, data=payload, headers=headers, params=querystring)

        dic_response = response.json()
        numero_jogos = len(dic_response['data'])
        print(f'🤖 {numero_jogos} jogos ao vivo\n')

        for game in dic_response['data']:
            date = game['date']

            awayTeam = game['awayTeam']['name']
            homeTeam = game['homeTeam']['name']
            league = game['league']['name']
            minute = game['currentTime']['minute']
            second = game['currentTime']['second']
            awayTeamScore = game['scores']['awayTeamScore']
            homeTeamScore = game['scores']['homeTeamScore']

            status = game['status']

            if game['stats'] == None:
                continue

            if minute == 0:
                continue
            

            iD = game['stats']['_id']

            corners_home = game['stats']['corners']['home']
            corners_away = game['stats']['corners']['away']

            fouls_home = game['stats']['fouls']['home']
            fouls_away = game['stats']['fouls']['away']

            goals_home = game['stats']['goals']['home']
            goals_away = game['stats']['goals']['away']

            offsides_home = game['stats']['offsides']['home']
            offsides_away = game['stats']['offsides']['away']

            possessiontime_home = game['stats']['possessiontime']['home']
            possessiontime_away = game['stats']['possessiontime']['away']

            redcards_home = game['stats']['redcards']['home']
            redcards_away = game['stats']['redcards']['away']

            shotsOffgoal_home = game['stats']['shotsOffgoal']['home']
            shotsOffgoal_away = game['stats']['shotsOffgoal']['away']

            shotsOngoal_home = game['stats']['shotsOngoal']['home']
            shotsOngoal_away = game['stats']['shotsOngoal']['away']

            shotsBlocked_home = game['stats']['shotsBlocked']['home']
            shotsBlocked_away = game['stats']['shotsBlocked']['away']

            tackles_home = game['stats']['tackles']['home']
            tackles_away = game['stats']['tackles']['away']

            yellowcards_home = game['stats']['yellowcards']['home']
            yellowcards_away = game['stats']['yellowcards']['away']

            novo_dado = {
                'goalHome': goals_home,
                'goalAway': goals_away,
                'minute': int(minute),
                'league': league,
                'corners_home': corners_home,
                'corners_away': corners_away,
                'possessiontime_home': possessiontime_home,
                'possessiontime_away': possessiontime_away,
                'redcards_home': redcards_home,
                'redcards_away': redcards_away,
                'shotsOngoal_home': shotsOngoal_home,
                'shotsOngoal_away': shotsOngoal_away,
                'shotsOffgoal_home': shotsOffgoal_home,
                'shotsOffgoal_away': shotsOffgoal_away,
                'yellowcards_home': yellowcards_home,
                'yellowcards_away': yellowcards_away,
                'fouls_home': fouls_home,
                'fouls_away': fouls_away,
                'offsides_home': offsides_home,
                'offsides_away': offsides_away,
                'tackles_home': tackles_home,
                'tackles_away': tackles_away,
                'blockedShotsHome': shotsBlocked_home,
                'blockedShotsAway': shotsBlocked_away,
                

            }

            Xht = pd.DataFrame(novo_dado, index=[0])
            Xht['shotsHome'] = Xht['shotsOngoal_home'] + Xht['shotsOffgoal_home']
            Xht['shotsAway'] = Xht['shotsOngoal_away'] + Xht['shotsOffgoal_away']

            if Xht.isna().sum().sum() > 0:
                continue

            # Tratando ligas com nomes diferentes, varios grupos, etc..
            if 'Asia - AFC Champions League' in league:
                league = 'Asia - AFC Champions League'
                Xht['league'] = league
            if 'Europe - Champions League' in league:
                league = 'Europe - Champions League'
                Xht['league'] = league
            
            if 'Europe - Europa League' in league:
                league = 'Europe - Europa League'
                Xht['league'] = league

            if minute > 1:
                Xht['shotsOnGoalEfficiency'] = (Xht['shotsOngoal_home'] + Xht['shotsOngoal_away']) / (Xht['shotsHome'] + Xht['shotsAway'] + 1) # A eficiência do ataque em termos de chutes que realmente vão em direção ao gol.
                Xht['attackPressure'] = (Xht['shotsHome'] + Xht['shotsAway'] + Xht['corners_home'] + Xht['corners_away']) / Xht['minute'] # Uma medida de quão ofensivas as equipes estão ao longo do jogo.
                Xht['shotAccuracy_home'] = Xht['shotsOngoal_home'] / (Xht['shotsHome'] + 1) # Proporção de chutes no gol em relação ao total de chutes.
                Xht['shotAccuracy_away'] = Xht['shotsOngoal_away'] / (Xht['shotsAway'] + 1)

                # Desempenho relacionado com chutes 
                Xht['shotsMinute_Home'] = Xht['minute'].where(Xht['shotsHome'].diff().fillna(0) > 0)
                Xht['shotsMinute_Away'] = Xht['minute'].where(Xht['shotsAway'].diff().fillna(0) > 0)

                # Desempenho Relacionado com Passes
                Xht['possessionControl'] = abs(Xht['possessiontime_home'] - Xht['possessiontime_away']) # Diferença absoluta do tempo de posse entre as equipes, indicando qual equipe dominou a posse de bola.
                # Xht['passRisk'] = (Xht['offsides_home'] + Xht['offsides_away']) / (Xht['possessiontime_home'] + Xht['possessiontime_away']) # Indicativo de quão arriscados são os passes, resultando em impedimentos.
                Xht['passRiskHome'] = Xht['offsides_home'] / (Xht['possessiontime_home']+ 0.01)
                Xht['passRiskAway'] = Xht['offsides_away'] / (Xht['possessiontime_away']+ 0.01)

                # Desempenho Relacionado com Defesa
                Xht['TotalCards_home'] = Xht['redcards_home'] + Xht['yellowcards_home']
                Xht['TotalCards_away'] = Xht['redcards_away'] + Xht['yellowcards_away']

                Xht['defensiveDiscipline'] = (1 - (Xht['redcards_home'] + Xht['yellowcards_home'] + Xht['fouls_home'] + 
                                                Xht['redcards_away'] + Xht['yellowcards_away'] + Xht['fouls_away']) / Xht['minute']) # Uma medida de quão disciplinadas as equipes estão em termos de cartões e faltas.

                Xht['defensiveEfficacy'] = (Xht['blockedShotsHome'] + Xht['blockedShotsAway']) / (Xht['shotsOnGoalEfficiency'] + 1) # Avalia a habilidade da defesa de bloquear chutes eficientes.
                Xht['defensiveAggression'] = (Xht['tackles_home'] + Xht['tackles_away']) / Xht['minute'] # Indicativo de quão agressiva a equipe é na defesa ao longo do jogo.

                # Desempenho Relacionado a chutes
                Xht['shotsMinute_Home'] = Xht['minute'].where(Xht['shotsHome'].diff().fillna(0) > 0)
                Xht['shotsMinute_Away'] = Xht['minute'].where(Xht['shotsAway'].diff().fillna(0) > 0)
                Xht['timeSinceLastEventShots_Home'] = Xht['minute'] - Xht.groupby(Xht['shotsMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEventShots_Away'] = Xht['minute'] - Xht.groupby(Xht['shotsMinute_Away'].notnull().cumsum())['minute'].transform('first')

                #  Desempenho relacionado com escanteios
                Xht['cornersMinute_Home'] = Xht['minute'].where(Xht['corners_home'].diff().fillna(0) > 0)
                Xht['cornersMinute_Away'] = Xht['minute'].where(Xht['corners_away'].diff().fillna(0) > 0)
                Xht['timeSinceLastEventCorners_Home'] = Xht['minute'] - Xht.groupby(Xht['cornersMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEventCorners_Away'] = Xht['minute'] - Xht.groupby(Xht['cornersMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho relacionado com passes
                Xht['passesMinute_Home'] = Xht['minute'].where(Xht['possessiontime_home'].diff().fillna(0) > 0)
                Xht['passesMinute_Away'] = Xht['minute'].where(Xht['possessiontime_away'].diff().fillna(0) > 0)
                Xht['timeSinceLastEventPasses_Home'] = Xht['minute'] - Xht.groupby(Xht['passesMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEventPasses_Away'] = Xht['minute'] - Xht.groupby(Xht['passesMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho Relacionado com Gols
                Xht['goalMinute_Home'] = Xht['minute'].where(Xht['goalHome'].diff().fillna(0) > 0)
                Xht['goalMinute_Away'] = Xht['minute'].where(Xht['goalAway'].diff().fillna(0) > 0)
                Xht['timeSinceLastEvent_Home'] = Xht['minute'] - Xht.groupby(Xht['goalMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEvent_Away'] = Xht['minute'] - Xht.groupby(Xht['goalMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho relacionado com faltas
                Xht['foulsMinute_Home'] = Xht['minute'].where(Xht['fouls_home'].diff().fillna(0) > 0)
                Xht['foulsMinute_Away'] = Xht['minute'].where(Xht['fouls_away'].diff().fillna(0) > 0)
                Xht['timeSinceLastEventFouls_Home'] = Xht['minute'] - Xht.groupby(Xht['foulsMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEventFouls_Away'] = Xht['minute'] - Xht.groupby(Xht['foulsMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho relacionado com cartões
                Xht['TotalCardsMinute_Home'] = Xht['minute'].where(Xht['TotalCards_home'].diff().fillna(0) > 0)
                Xht['TotalCardsMinute_Away'] = Xht['minute'].where(Xht['TotalCards_away'].diff().fillna(0) > 0)
                Xht['timeSinceLastEventTotalCards_Home'] = Xht['minute'] - Xht.groupby(Xht['TotalCardsMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEventTotalCards_Away'] = Xht['minute'] - Xht.groupby(Xht['TotalCardsMinute_Away'].notnull().cumsum())['minute'].transform('first')

                event_columns = ['shotsHome', 'shotsAway', 'possessiontime_home', 'possessiontime_away', 'blockedShotsHome', 'blockedShotsAway', 'corners_home', 'corners_away', 'redcards_home', 'redcards_away',
                    'shotsOffgoal_home', 'shotsOffgoal_away', 'shotsOngoal_home',
                    'shotsOngoal_away', 'yellowcards_home', 'yellowcards_away',
                    'fouls_home', 'fouls_away', 'offsides_home', 'offsides_away',
                    'tackles_home', 'tackles_away']
                
                gols_columns = ['05ht_home', '05ft_home',
                                '15ft_home', '25ft_home', '15_home', '05ht_away', '05ft_away',
                                '15ft_away', '05_away', '15_away']
                

                df['similaridade_home'] = calculate_similarity(df['homeTeam'], homeTeam)
                df['similaridade_away'] = calculate_similarity(df['awayTeam'], awayTeam)

                # Encontrando a string com a maior similaridade (usando a abordagem vetorizada)
                string_mais_similar_home = df.loc[df['similaridade_home'].idxmax()]
                string_mais_similar_away = df.loc[df['similaridade_away'].idxmax()]
                
                for gols_c in gols_columns:
                    if 'home' in gols_c:
                        Xht[gols_c] = df[df['homeTeam'] == string_mais_similar_home][gols_c].tail(1).values[0]
                    else:
                        Xht[gols_c] = df[df['awayTeam'] == string_mais_similar_away][gols_c].tail(1).values[0]

                def calculate_event_change(data, event_column, lookback=10):
                    """
                    Calcula a mudança no evento especificado para cada linha, olhando para os 
                    10 registros anteriores. A diferença entre os valores máximo e mínimo nesse
                    intervalo é calculada.
                    """
                    # Nome da nova coluna
                    new_column = f'total_change_{event_column}'

                    # Calculando o valor máximo e mínimo em uma janela deslizante
                    rolling_max = data[event_column].rolling(window=lookback, min_periods=1).max()
                    rolling_min = data[event_column].rolling(window=lookback, min_periods=1).min()

                    # Calculando a diferença e atribuindo à nova coluna
                    data[new_column] = rolling_max - rolling_min

                    return data

                # Aplicando a função ao dataframe 'data_teste' para a coluna os eventos
                # Criando uma cópia do data_copyframe original para trabalhar com as mudanças
                data = Xht.copy()
                for event_column in event_columns:
                    Xht = calculate_event_change(data, event_column)
                
                if iD not in df_jogos:
                    df_jogos[iD] = []

                df_jogos[iD].append(Xht)
                df = pd.concat(df_jogos[iD], axis=0)
                df.sort_values(by=['minute'], inplace=True)
                df.reset_index(drop=True, inplace=True)
                df['shotsOnGoalEfficiency'] = (df['shotsOngoal_home'] + df['shotsOngoal_away']) / (df['shotsHome'] + df['shotsAway'] + 1) # A eficiência do ataque em termos de chutes que realmente vão em direção ao gol.
                df['attackPressure'] = (df['shotsHome'] + df['shotsAway'] + df['corners_home'] + df['corners_away']) / df['minute'] # Uma medida de quão ofensivas as equipes estão ao longo do jogo.
                df['shotAccuracy_home'] = df['shotsOngoal_home'] / (df['shotsHome'] + 1) # Proporção de chutes no gol em relação ao total de chutes.
                df['shotAccuracy_away'] = df['shotsOngoal_away'] / (df['shotsAway'] + 1)

                # Desempenho relacionado com chutes 
                df['shotsMinute_Home'] = df['minute'].where(df['shotsHome'].diff().fillna(0) > 0)
                df['shotsMinute_Away'] = df['minute'].where(df['shotsAway'].diff().fillna(0) > 0)

                # Desempenho Relacionado com Passes
                df['possessionControl'] = abs(df['possessiontime_home'] - df['possessiontime_away']) # Diferença absoluta do tempo de posse entre as equipes, indicando qual equipe dominou a posse de bola.
                # df['passRisk'] = (df['offsides_home'] + df['offsides_away']) / (df['possessiontime_home'] + df['possessiontime_away']) # Indicativo de quão arriscados são os passes, resultando em impedimentos.
                df['passRiskHome'] = df['offsides_home'] / (df['possessiontime_home']+ 0.01)
                df['passRiskAway'] = df['offsides_away'] / (df['possessiontime_away']+ 0.01)

                # Desempenho Relacionado com Defesa
                df['TotalCards_home'] = df['redcards_home'] + df['yellowcards_home']
                df['TotalCards_away'] = df['redcards_away'] + df['yellowcards_away']

                df['defensiveDiscipline'] = (1 - (df['redcards_home'] + df['yellowcards_home'] + df['fouls_home'] + 
                                                df['redcards_away'] + df['yellowcards_away'] + df['fouls_away']) / df['minute']) # Uma medida de quão disciplinadas as equipes estão em termos de cartões e faltas.

                df['defensiveEfficacy'] = (df['blockedShotsHome'] + df['blockedShotsAway']) / (df['shotsOnGoalEfficiency'] + 1) # Avalia a habilidade da defesa de bloquear chutes eficientes.
                df['defensiveAggression'] = (df['tackles_home'] + df['tackles_away']) / df['minute'] # Indicativo de quão agressiva a equipe é na defesa ao longo do jogo.

                # Desempenho Relacionado a chutes
                df['shotsMinute_Home'] = df['minute'].where(df['shotsHome'].diff().fillna(0) > 0)
                df['shotsMinute_Away'] = df['minute'].where(df['shotsAway'].diff().fillna(0) > 0)
                df['timeSinceLastEventShots_Home'] = df['minute'] - df.groupby(df['shotsMinute_Home'].notnull().cumsum())['minute'].transform('first')
                df['timeSinceLastEventShots_Away'] = df['minute'] - df.groupby(df['shotsMinute_Away'].notnull().cumsum())['minute'].transform('first')

                #  Desempenho relacionado com escanteios
                df['cornersMinute_Home'] = df['minute'].where(df['corners_home'].diff().fillna(0) > 0)
                df['cornersMinute_Away'] = df['minute'].where(df['corners_away'].diff().fillna(0) > 0)
                df['timeSinceLastEventCorners_Home'] = df['minute'] - df.groupby(df['cornersMinute_Home'].notnull().cumsum())['minute'].transform('first')
                df['timeSinceLastEventCorners_Away'] = df['minute'] - df.groupby(df['cornersMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho relacionado com passes
                df['passesMinute_Home'] = df['minute'].where(df['possessiontime_home'].diff().fillna(0) > 0)
                df['passesMinute_Away'] = df['minute'].where(df['possessiontime_away'].diff().fillna(0) > 0)
                df['timeSinceLastEventPasses_Home'] = df['minute'] - df.groupby(df['passesMinute_Home'].notnull().cumsum())['minute'].transform('first')
                df['timeSinceLastEventPasses_Away'] = df['minute'] - df.groupby(df['passesMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho Relacionado com Gols
                df['goalMinute_Home'] = df['minute'].where(df['goalHome'].diff().fillna(0) > 0)
                df['goalMinute_Away'] = df['minute'].where(df['goalAway'].diff().fillna(0) > 0)
                df['timeSinceLastEvent_Home'] = df['minute'] - df.groupby(df['goalMinute_Home'].notnull().cumsum())['minute'].transform('first')
                df['timeSinceLastEvent_Away'] = df['minute'] - df.groupby(df['goalMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho relacionado com faltas
                df['foulsMinute_Home'] = df['minute'].where(df['fouls_home'].diff().fillna(0) > 0)
                df['foulsMinute_Away'] = df['minute'].where(df['fouls_away'].diff().fillna(0) > 0)
                df['timeSinceLastEventFouls_Home'] = df['minute'] - df.groupby(df['foulsMinute_Home'].notnull().cumsum())['minute'].transform('first')
                df['timeSinceLastEventFouls_Away'] = df['minute'] - df.groupby(df['foulsMinute_Away'].notnull().cumsum())['minute'].transform('first')

                # Desempenho relacionado com cartões
                Xht['TotalCardsMinute_Home'] = Xht['minute'].where(Xht['TotalCards_home'].diff().fillna(0) > 0)
                Xht['TotalCardsMinute_Away'] = Xht['minute'].where(Xht['TotalCards_away'].diff().fillna(0) > 0)
                Xht['timeSinceLastEventTotalCards_Home'] = Xht['minute'] - Xht.groupby(Xht['TotalCardsMinute_Home'].notnull().cumsum())['minute'].transform('first')
                Xht['timeSinceLastEventTotalCards_Away'] = Xht['minute'] - Xht.groupby(Xht['TotalCardsMinute_Away'].notnull().cumsum())['minute'].transform('first')

                event_columns = ['shotsHome', 'shotsAway', 'possessiontime_home', 'possessiontime_away', 'blockedShotsHome', 'blockedShotsAway', 'corners_home', 'corners_away', 'redcards_home', 'redcards_away',
                    'shotsOffgoal_home', 'shotsOffgoal_away', 'shotsOngoal_home',
                    'shotsOngoal_away', 'yellowcards_home', 'yellowcards_away',
                    'fouls_home', 'fouls_away', 'offsides_home', 'offsides_away',
                    'tackles_home', 'tackles_away']
                
                gols_columns = ['05ht_home', '05ft_home',
                                '15ft_home', '25ft_home', '15_home', '05ht_away', '05ft_away',
                                '15ft_away', '05_away', '15_away']
                

                df['similaridade_home'] = calculate_similarity(df['homeTeam'], homeTeam)
                df['similaridade_away'] = calculate_similarity(df['awayTeam'], awayTeam)

                # Encontrando a string com a maior similaridade (usando a abordagem vetorizada)
                string_mais_similar_home = df.loc[df['similaridade_home'].idxmax()]
                string_mais_similar_away = df.loc[df['similaridade_away'].idxmax()]
                
                for gols_c in gols_columns:
                    if 'home' in gols_c:
                        Xht[gols_c] = df[df['homeTeam'] == string_mais_similar_home][gols_c].tail(1).values[0]
                    else:
                        Xht[gols_c] = df[df['awayTeam'] == string_mais_similar_away][gols_c].tail(1).values[0]
                

                def calculate_event_change(data, event_column, lookback=10):
                    """
                    Calcula a mudança no evento especificado para cada linha, olhando para os 
                    10 registros anteriores. A diferença entre os valores máximo e mínimo nesse
                    intervalo é calculada.
                    """
                    # Nome da nova coluna
                    new_column = f'total_change_{event_column}'

                    # Calculando o valor máximo e mínimo em uma janela deslizante
                    rolling_max = data[event_column].rolling(window=lookback, min_periods=1).max()
                    rolling_min = data[event_column].rolling(window=lookback, min_periods=1).min()

                    # Calculando a diferença e atribuindo à nova coluna
                    data[new_column] = rolling_max - rolling_min

                    return data

                # Aplicando a função ao dataframe 'data_teste' para a coluna os eventos
                # Criando uma cópia do data_copyframe original para trabalhar com as mudanças
                data = df.copy()
                for event_column in event_columns:
                    df = calculate_event_change(data, event_column)
                Xht = df.tail(1)
                
                if Xht['shotsHome'].values[0] == 0:
                    Xht['timeSinceLastEventShots_Home'] = Xht['minute'] - 1
                
                if Xht['shotsAway'].values[0] == 0:
                    Xht['timeSinceLastEventShots_Away'] = Xht['minute'] - 1
                
                if Xht['possessiontime_home'].values[0] == 0:
                    Xht['timeSinceLastEventPasses_Home'] = Xht['minute'] - 1
                
                if Xht['possessiontime_away'].values[0] == 0:
                    Xht['timeSinceLastEventPasses_Away'] = Xht['minute'] - 1
                
                if Xht['fouls_home'].values[0] == 0:
                    Xht['timeSinceLastEventFouls_Home'] = Xht['minute'] - 1
                
                if Xht['fouls_away'].values[0] == 0:
                    Xht['timeSinceLastEventFouls_Away'] = Xht['minute'] - 1
                
                if Xht['TotalCards_home'].values[0] == 0:
                    Xht['timeSinceLastEventTotalCards_Home'] = Xht['minute'] - 1
                
                if Xht['TotalCards_away'].values[0] == 0:
                    Xht['timeSinceLastEventTotalCards_Away'] = Xht['minute'] - 1
                
                if Xht['goalHome'].values[0] == 0:
                    Xht['timeSinceLastEvent_Home'] = Xht['minute'] - 1
                
                if Xht['goalAway'].values[0] == 0:
                    Xht['timeSinceLastEvent_Away'] = Xht['minute'] - 1
                
                if Xht['corners_home'].values[0] == 0:
                    Xht['timeSinceLastEventCorners_Home'] = Xht['minute'] - 1
                
                if Xht['corners_away'].values[0] == 0:
                    Xht['timeSinceLastEventCorners_Away'] = Xht['minute'] - 1
                
                Xht.drop(columns=['goalMinute_Home', 
                                  'goalMinute_Away', 
                                  'shotsMinute_Home', 
                                  'shotsMinute_Away', 
                                  'passesMinute_Home', 
                                  'passesMinute_Away', 
                                  'foulsMinute_Home', 
                                  'foulsMinute_Away', 
                                  'TotalCardsMinute_Home', 
                                  'TotalCardsMinute_Away'], inplace=True)

                Xht.drop(columns=['25_away',
                                '15ht_home',
                                '25ft_away',
                                '05_home',
                                '25ht_away',
                                '15ht_away',
                                '25_home',
                                '25ht_home',
                                'goalHome',
                                'goalAway',
                                'total_change_tackles_away',
                                'total_change_tackles_home',
                                'shotsOngoal_away',
                                'TotalCards_away',
                                'corners_away',
                                'yellowcards_away',
                                'blockedShotsHome',
                                'offsides_home',
                                'total_change_shotsHome',
                                'total_change_shotsOngoal_home',
                                'TotalCards_home',
                                'total_change_shotsAway',
                                'timeSinceLastEventPasses_Home',
                                'yellowcards_home',
                                'total_change_shotsOngoal_away',
                                'blockedShotsAway',
                                'timeSinceLastEventPasses_Away',
                                'total_change_fouls_away',
                                'offsides_away',
                                'total_change_blockedShotsHome',
                                'total_change_fouls_home',
                                'total_change_offsides_away',
                                'total_change_corners_away',
                                'total_change_corners_home',
                                'total_change_awayellowcards_home',
                                'total_change_blockedShotsAway',
                                'total_change_offsides_home',
                                'total_change_awayellowcards_away',
                                'total_change_shotsOffgoal_away',
                                'total_change_shotsOffgoal_home',
                                'redcards_away',
                                'redcards_home',
                                'total_change_redcards_home',
                                'total_change_redcards_away'], inplace=True)
                                                
                shotsHome = Xht['shotsHome'].values[0]
                shotsAway = Xht['shotsAway'].values[0]
                shotsOnGoalEfficiency = Xht['shotsOnGoalEfficiency'].values[0]
                attackPressure = Xht['attackPressure'].values[0]
                shotAccuracy_home = Xht['shotAccuracy_home'].values[0]
                shotAccuracy_away = Xht['shotAccuracy_away'].values[0]
                possessionControl = Xht['possessionControl'].values[0]
                defensiveDiscipline = Xht['defensiveDiscipline'].values[0]
                defensiveEfficacy = Xht['defensiveEfficacy'].values[0]
                defensiveAggression = Xht['defensiveAggression'].values[0]
                shotsOngoal_home = Xht['shotsOngoal_home'].values[0]
                shotsOngoal_away = Xht['shotsOngoal_away'].values[0]
                shotsOffgoal_away = Xht['shotsOffgoal_away'].values[0]
                shotsOffgoal_home = Xht['shotsOffgoal_home'].values[0]
                fouls_home = Xht['fouls_home'].values[0]
                fouls_away = Xht['fouls_away'].values[0]
                tackles_away = Xht['tackles_away'].values[0]
                tackles_home = Xht['tackles_home'].values[0]
                corners_home = Xht['corners_home'].values[0]
                corners_away = Xht['corners_away'].values[0]
                possessiontime_home = Xht['possessiontime_home'].values[0]
                possessiontime_away = Xht['possessiontime_away'].values[0]
                shotsBlocked_home = Xht['blockedShotsHome'].values[0]
                # shotsBlocked_away = Xht['blockedShotsAway'].values[0]
                passRiskHome = Xht['passRiskHome'].values[0]
                passRiskAway = Xht['passRiskAway'].values[0]
                timeSinceLastEvent_Home = Xht['timeSinceLastEvent_Home'].values[0]
                timeSinceLastEvent_Away = Xht['timeSinceLastEvent_Away'].values[0]
                timeSinceLastEventShots_Home = Xht['timeSinceLastEventShots_Home'].values[0]
                timeSinceLastEventShots_Away = Xht['timeSinceLastEventShots_Away'].values[0]
                # timeSinceLastEventPasses_Away = Xht['timeSinceLastEventPasses_Away'].values[0]
                timeSinceLastEventFouls_Home = Xht['timeSinceLastEventFouls_Home'].values[0]
                timeSinceLastEventFouls_Away = Xht['timeSinceLastEventFouls_Away'].values[0]
                timeSinceLastEventTotalCards_Home = Xht['timeSinceLastEventTotalCards_Home'].values[0]
                timeSinceLastEventTotalCards_Away = Xht['timeSinceLastEventTotalCards_Away'].values[0]
                timeSinceLastEventCorners_Home = Xht['timeSinceLastEventCorners_Home'].values[0]
                timeSinceLastEventCorners_Away = Xht['timeSinceLastEventCorners_Away'].values[0]
                total_change_possessiontime_home = Xht['total_change_possessiontime_home'].values[0]
                total_change_possessiontime_away = Xht['total_change_possessiontime_away'].values[0]
                total_change_tackles_home = Xht['total_change_tackles_home'].values[0]
                total_change_tackles_away = Xht['total_change_tackles_away'].values[0]
                zero_meioht_home = Xht['05ht_home'].values[0]
                zero_meioft_home = Xht['05ft_home'].values[0]
                um_meioft_home = Xht['15ft_home'].values[0]
                dois_meioft_home = Xht['25ft_home'].values[0]
                um_meio_home = Xht['15_home'].values[0]
                zero_meioht_away = Xht['05ht_away'].values[0]
                zero_meioft_away = Xht['05ft_away'].values[0]
                um_meioft_away = Xht['15ft_away'].values[0]
                dois_meioft_away = Xht['25ft_away'].values[0]
                um_meio_away = Xht['15_away'].values[0]
                zero_meio_away = Xht['05_away'].values[0]

                # ordenando as colunas
                colunas = ['minute', 'shotsHome', 'shotsAway', 'league',
                            'corners_home', 'shotsOffgoal_home', 'shotsOffgoal_away',
                            'shotsOngoal_home', 'fouls_home', 'fouls_away', 'tackles_home',
                            'tackles_away', 'result', 'possessiontime_away',
                            'possessiontime_home', 'shotsOnGoalEfficiency', 'attackPressure',
                            'shotAccuracy_home', 'shotAccuracy_away', 'possessionControl',
                            'passRiskHome', 'passRiskAway', 'defensiveDiscipline',
                            'defensiveEfficacy', 'defensiveAggression',
                            'timeSinceLastEventShots_Home', 'timeSinceLastEventShots_Away',
                            'timeSinceLastEventCorners_Home', 'timeSinceLastEventCorners_Away',
                            'timeSinceLastEvent_Home', 'timeSinceLastEvent_Away',
                            'timeSinceLastEventFouls_Home', 'timeSinceLastEventFouls_Away',
                            'timeSinceLastEventTotalCards_Home',
                            'timeSinceLastEventTotalCards_Away', 'total_change_possessiontime_home',
                            'total_change_possessiontime_away', '05ht_home', '05ft_home',
                            '15ft_home', '25ft_home', '15_home', '05ht_away', '05ft_away',
                            '15ft_away', '05_away', '15_away']
                
                Xht = Xht[colunas]

                # try:
                #     id_evento = game['betfairId']
                # except:
                #     continue

            

                print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {homeTeamScore} x {awayTeamScore} ({league})')
                print_jogos = f'''
                🚨 Jogo: {homeTeam} x {awayTeam}
                🏆 Liga: {league}
                ⏱️ Minuto: {minute}

                📋 Estatísticas
                🎯 Chutes Casa: {shotsHome}
                🎯 Chutes Fora: {shotsAway}
                ⛳ Escanteios Casa: {corners_home}
                🦵 Chutes fora Casa: {shotsOffgoal_home}
                🦵 Chutes fora Fora: {shotsOffgoal_away}
                🎯 Chutes ao gol Casa: {shotsOngoal_home}
                🔴 Faltas Casa: {fouls_home}
                🔴 Faltas Fora: {fouls_away}
                🛑 Desarmes Casa: {tackles_home}
                🛑 Desarmes Fora: {tackles_away}
                ⏰ Tempo de posse Casa: {possessiontime_home}
                ⏰ Tempo de posse Fora: {possessiontime_away}
                🎯 Eficiência de Chutes no Gol: {shotsOnGoalEfficiency}
                ⚡ Pressão de Ataque: {attackPressure}
                🎯 Precisão de Chutes Casa: {shotAccuracy_home}
                🎯 Precisão de Chutes Fora: {shotAccuracy_away}
                🎮 Controle de Posse: {possessionControl}
                🎲 Risco de Passe Casa: {passRiskHome}
                🎲 Risco de Passe Fora: {passRiskAway}
                🛡️ Disciplina Defensiva: {defensiveDiscipline}
                🛡️ Eficácia Defensiva: {defensiveEfficacy}
                🛡️ Agressão Defensiva: {defensiveAggression}
                ⏱️ Tempo desde o último chute Casa: {timeSinceLastEventShots_Home}
                ⏱️ Tempo desde o último chute Fora: {timeSinceLastEventShots_Away}
                ⏱️ Tempo desde o último escanteio Casa: {timeSinceLastEventCorners_Home}
                ⏱️ Tempo desde o último escanteio Fora: {timeSinceLastEventCorners_Away}
                ⏱️ Tempo desde o último evento Casa: {timeSinceLastEvent_Home}
                ⏱️ Tempo desde o último evento Fora: {timeSinceLastEvent_Away}
                ⏱️ Tempo desde a última falta Casa: {timeSinceLastEventFouls_Home}
                ⏱️ Tempo desde a última falta Fora: {timeSinceLastEventFouls_Away}
                ⏱️ Tempo desde o último cartão Casa: {timeSinceLastEventTotalCards_Home}
                ⏱️ Tempo desde o último cartão Fora: {timeSinceLastEventTotalCards_Away}
                ⏱️ Mudança no tempo de posse Casa: {total_change_possessiontime_home}
                ⏱️ Mudança no tempo de posse Fora: {total_change_possessiontime_away}
                📊 05 HT Casa: {zero_meioht_home}
                📊 05 FT Casa: {zero_meioft_home}
                📊 15 FT Casa: {um_meioft_home}
                📊 25 FT Casa: {dois_meioft_home}
                📊 15 Casa: {um_meio_home}
                📊 05 HT Fora: {zero_meioht_away}
                📊 05 FT Fora: {zero_meioft_away}
                📊 15 FT Fora: {um_meioft_away}
                📊 05 Fora: {zero_meio_away}
                📊 15 Fora: {um_meio_away}
                '''

                condicao_rede = 0
                condicao_Automl = 0

                if status == 'LIVE':

                    if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                        try:
                            Xht = preprocessor.transform(Xht)
                        except:
                            continue
                        novo_dado = torch.tensor(Xht, dtype=torch.float32)

                        with torch.no_grad():
                            value_pred_rede = model(novo_dado)[0][0]
                        value_pred_automl = model_Automl.predict(Xht)[0]
                        
                        print(f'{homeTeam} x {awayTeam} rede: {value_pred_rede}')
                        print(f"{homeTeam} x {awayTeam} Automl: {value_pred_automl}")
                        
                        if value_pred_rede >= 0.52:

                            condicao_rede = 1

                        if value_pred_automl >= 0.52:
                            condicao_Automl = 1

                for key, value in id_jogos_mensagem.items():
                    if key == 'id_over05HTmodel':
                        for jogos in value:
                            if jogos['id'] == iD:
                                text = f'''
                                👑 Modelo Rede Neural
                                                                            
                                💭 Previsão: {value_pred_rede}
                                {print_jogos}
                                '''
                                if '&' in text:
                                    text = text.replace('&', '')
                                editMessageTelegram(jogos['message_id'], text)
                    if key == 'id_over05HTAutoml':
                        for jogos in value:
                            if jogos['id'] == iD:
                                text = f'''
                                👑 Modelo Automl
                                                                        
                                💭 Previsão: {value_pred_automl}
                                {print_jogos}
                                '''
                                if '&' in text:
                                    text = text.replace('&', '')
                                editMessageTelegram(jogos['message_id'], text)


                # rede neural
                if iD in id_over05HTmodel:
                    if minute <= 90 and (awayTeamScore + homeTeamScore) > 0:
                        winht_model += 1
                        id_over05HTmodel.remove(iD)
                        
                        
                        valor = valorEsperado - 5
                        lucro += valor

                        for key, value in id_jogos_mensagem.items():
                            if key == 'id_over05HTmodel':
                                for jogos in value:
                                    if jogos['id'] == iD:
                                        text = f'''
                                        👑 Modelo Rede Neural

                                        ✅ Win {winht_model} - {loseht_model}
                                        {print_jogos}
                                        '''
                                        if '&' in text:
                                            text = text.replace('&', '')
                                        sendMenssageTelegram(text)
                        
                                        # remove do dicionario
                                        id_jogos_mensagem[key].remove(jogos)

                    # if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    if status != 'LIVE' and (awayTeamScore + homeTeamScore) == 0:
                        loseht_model += 1
                        id_over05HTmodel.remove(iD)
                        
                        lucro -= 5
                        for key, value in id_jogos_mensagem.items():
                            if key == 'id_over05HTmodel':
                                for jogos in value:
                                    if jogos['id'] == iD:
                                        text = f'''
                                        👑 Modelo Rede Neural

                                        🛑 Lose {winht_model} - {loseht_model}
                                        {print_jogos}
                                        '''
                                        if '&' in text:
                                            text = text.replace('&', '')
                                        sendMenssageTelegram(text)
        
                                        # remove do dicionario
                                        id_jogos_mensagem[key].remove(jogos)
                
                

                # Automl
                if iD in id_over05HTAutoml:
                    if minute <= 90 and (awayTeamScore + homeTeamScore) > 0:
                        winht_Automl += 1
                        id_over05HTAutoml.remove(iD)
                        
                        valor = valorEsperado - 5
                        lucro += valor
                        for key, value in id_jogos_mensagem.items():
                            if key == 'id_over05HTAutoml':
                                for jogos in value:
                                    if jogos['id'] == iD:
                                        text = f'''
                                        👑 Modelo Automl

                                        ✅ Win {winht_Automl} - {loseht_Automl}
                                        {print_jogos}
                                        '''
                                        if '&' in text:
                                            text = text.replace('&', '')
                                        sendMenssageTelegram(text)
                                        id_jogos_mensagem[key].remove(jogos)
                    
                    if status != 'LIVE' and (awayTeamScore + homeTeamScore) == 0:
                        loseht_Automl += 1
                        id_over05HTAutoml.remove(iD)
                        
                        lucro -= 5
                        for key, value in id_jogos_mensagem.items():
                            if key == 'id_over05HTAutoml':
                                for jogos in value:
                                    if jogos['id'] == iD:
                                        text = f'''
                                        👑 Modelo Automl
                                                                                            
                                        🛑 Lose {winht_Automl} - {loseht_Automl}
                                        {print_jogos}
                                        '''
                                        if '&' in text:
                                            text = text.replace('&', '')
                                        
                                        sendMenssageTelegram(text)
                                        # remove do dicionario
                                        id_jogos_mensagem[key].remove(jogos)

                if condicao_rede == 1 and iD not in id_over05HTmodel:
                    id_over05HTmodel.append(iD)
                    # state, valorEsperado = makeBet(id_evento)
                    state, valorEsperado = 'SUCCESS', 10

                    text = f'''
                    👑 Modelo Rede Neural 

                    💭 Previsão: {value_pred_rede}
                    {print_jogos}
                    
                    '''

                    if '&' in text:
                        text = text.replace('&', '')
                    sendMenssageTelegram(text)
                    id_jogos_mensagem["id_over05HTmodel"].append({"id": iD, "message_id": sendMenssageTelegram(text)})

                if condicao_Automl == 1 and iD not in id_over05HTAutoml:
                    id_over05HTAutoml.append(iD)
                    # state, valorEsperado = makeBet(id_evento)
                    state, valorEsperado = 'SUCCESS', 10

                    text = f'''
                    👑 Modelo Automl 
                    
                    💭 Previsão: {value_pred_automl}
                    {print_jogos}
                    '''
                    if '&' in text:
                        text = text.replace('&', '')
                    # sendMenssageTelegram(text)
                    id_jogos_mensagem["id_over05HTAutoml"].append({"id": iD, "message_id": sendMenssageTelegram(text)})

                
        time.sleep(60)
    
    except Exception as e:
        traceback.print_exc()
        # sendMenssageTelegram(f'Erro: {e}')
        time.sleep(60)
        print(e)
        continue
