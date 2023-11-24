import requests
import traceback
import requests
import time
from datetime import datetime
import pandas as pd
import pickle
import warnings
import keras

import pandas as pd
import h2o
from dotenv import load_dotenv
import os
from datetime import datetime
# import betfairlightweight
# import configparser



warnings.filterwarnings('ignore')

load_dotenv()

chat_id = os.getenv('CHAT_ID')
token = os.getenv('TOKEN')


def sendMenssageTelegram(message):
    url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    results = requests.get(url_base)
    print(results)
    print(message)


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

model = keras.models.load_model('models/model_redeht.h5')

# Inicializar o cluster H2O
h2o.init()
model_Automl = loaded_model = h2o.load_model("./models/model_automl")

preprocessor = pickle.load(
                        open('models/preprocessor.pickle', 'rb'))

# carregando modelo
import torch
import torch.nn as nn

class BinaryClassificationModel(nn.Module):
    def __init__(self, input_shape):
        super(BinaryClassificationModel, self).__init__()
        self.layer1 = nn.Linear(input_shape, 128)
        self.layer2 = nn.Linear(128, 64)
        self.layer3 = nn.Linear(64, 1)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = torch.sigmoid(self.layer3(x))
        return x
# Crie uma instância do modelo
model_py = BinaryClassificationModel(input_shape=50)  # 50 é o número de colunas de recursos

# Carregue os pesos salvos
model_py.load_state_dict(torch.load('./models/model_redeht.pth'))

# Coloque o modelo em modo de avaliação (isso é importante para desativar características como dropout, se aplicável)
model_py.eval()

id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

id_over05HTmodelPy = []
winht_modelPy = 0
loseht_modelPy = 0

id_evento = ''

lucro = 0
valorEsperado = 0
state = ''
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

        for game in dic_response['data']:
            awayTeam = game['awayTeam']['name']
            homeTeam = game['homeTeam']['name']
            status = game['status']
            minute = game['currentTime']['minute']
            awayTeamScore = game['scores']['homeTeamScore']
            homeTeamScore = game['scores']['awayTeamScore']
            league = game['league']['name']

            print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {awayTeamScore} x {homeTeamScore} ({league})')

        for game in dic_response['data']:
            date = game['date']

            awayTeam = game['awayTeam']['name']
            homeTeam = game['homeTeam']['name']
            league = game['league']['name']
            minute = game['currentTime']['minute']
            second = game['currentTime']['second']
            awayTeamScore = game['scores']['homeTeamScore']
            homeTeamScore = game['scores']['awayTeamScore']

            status = game['status']

            if game['stats'] == None:
                continue

            iD = game['stats']['_id']

            attacks_home = game['stats']['attacks']['home']
            attacks_away = game['stats']['attacks']['away']

            corners_home = game['stats']['corners']['home']
            corners_away = game['stats']['corners']['away']

            # dangerousAttacks_home = game['stats']['dangerousAttacks']['home']
            # dangerousAttacks_away = game['stats']['dangerousAttacks']['away']

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

            shotsOutsidebox_home = game['stats']['shotsOutsidebox']['home']
            shotsOutsidebox_away = game['stats']['shotsOutsidebox']['away']

            tackles_home = game['stats']['tackles']['home']
            tackles_away = game['stats']['tackles']['away']

            yellowcards_home = game['stats']['yellowcards']['home']
            yellowcards_away = game['stats']['yellowcards']['away']

            novo_dado = {
                'minute': minute,
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

            }

            Xht = pd.DataFrame(novo_dado, index=[0])
            
            # Tratando ligas com nomes diferentes, varios grupos, etc..
            if 'Asia - AFC Champions League' in league:
                league = 'Asia - AFC Champions League'
                Xht['league'] = league

            # try:
            #     id_evento = game['betfairId']
            # except:
            #     continue

            if Xht.isna().sum().sum() > 0:
                continue

            # rede neural
            if iD in id_over05HTmodel:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_model += 1
                    id_over05HTmodel.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor

                    text = f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem over 0.5 ht

            ✅ Win {winht_model} - {loseht_model}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)

                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_model += 1
                    id_over05HTmodel.remove(iD)
                    lucro -= 5
                    text = f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem over 0.5 ht

            🛑 Lose {winht_model} - {loseht_model}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}
            
            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)
            
            # rede neural pytorch
            if iD in id_over05HTmodelPy:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_modelPy += 1
                    id_over05HTmodelPy.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor

                    text = f'''{len(id_over05HTmodelPy)} 👑 Modelo Rede Neural Pytorch over 0.5 ht

            ✅ Win {winht_modelPy} - {loseht_modelPy}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)

                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_modelPy += 1
                    id_over05HTmodelPy.remove(iD)
                    lucro -= 5
                    text = f'''{len(id_over05HTmodelPy)} 👑 Modelo Rede Neural Pytorch over 0.5 ht

            🛑 Lose {winht_modelPy} - {loseht_modelPy}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)

            # Automl
            if iD in id_over05HTAutoml:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_Automl += 1
                    id_over05HTAutoml.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor

                    text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl over 0.5 ht

            ✅ Win {winht_Automl} - {loseht_Automl}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)
                
                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_Automl += 1
                    id_over05HTAutoml.remove(iD)
                    lucro -= 5
                    text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl over 0.5 ht

            🛑 Lose {winht_Automl} - {loseht_Automl}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)
            


            condicao5min = 0
            condicao5min_Automl = 0
            condicao5minPy = 0

            if minute >= 1 and minute < 45:
                try:
                    

                    Xht = preprocessor.transform(Xht)
                    Xht_h2o = h2o.H2OFrame(Xht)

                    X_ht = torch.from_numpy(Xht).float()

                except Exception as e:
                    print(e)
                    continue

                if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                    print(
                        f'{homeTeam} x {awayTeam} rede: {model.predict(Xht)[0][0]}')

                    print(
                        f"{homeTeam} x {awayTeam} Automl: {h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']}")
                    
                    print(
                        f"{homeTeam} x {awayTeam} Pytorch: {model_py(X_ht)[0][0]}")

                    if model.predict(Xht)[0][0] >= 0.75:

                        condicao5min = 1

                    if h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1'] >= 0.75:
                        condicao5min_Automl = 1

                    if model_py(X_ht)[0][0] >= 0.75:
                        condicao5minPy = 1

            if condicao5min == 1 and iD not in id_over05HTmodel:
                id_over05HTmodel.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTmodel)} 👑 Modelo Rede Neural over 0.5 ht

    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {model.predict(Xht)[0][0]}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    📈 Ataques: {attacks_home} - {attacks_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''

                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)

            if condicao5min_Automl == 1 and iD not in id_over05HTAutoml:
                id_over05HTAutoml.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl over 0.5 ht
    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    📈 Ataques: {attacks_home} - {attacks_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''
                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)
            
            if condicao5minPy == 1 and iD not in id_over05HTmodelPy:
                id_over05HTmodelPy.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTmodelPy)} 👑 Modelo Rede Neural Pytorch over 0.5 ht
    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    📈 Ataques: {attacks_home} - {attacks_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''
                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)
                


        time.sleep(60)
    except Exception as e:
        traceback.print_exc()
        print(e)
        continue
