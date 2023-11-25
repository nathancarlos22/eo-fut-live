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

warnings.filterwarnings('ignore')

load_dotenv()

chat_id = os.getenv('CHAT_ID')
token = os.getenv('TOKEN')


def sendMenssageTelegram(message):
    url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    response = requests.get(url_base)
    print(message)
    return response.json()['result']['message_id']

def editMessageTelegram(message_id, new_message):
    url_base = f'https://api.telegram.org/bot{token}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={new_message}'
    requests.get(url_base)

id_jogos_mensagem = {
    "id_over05HTmodel": [],
    "id_over05HTAutoml": []
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

model = keras.models.load_model('models/model_redeht.h5')

# Inicializar o cluster H2O
h2o.init()
model_Automl = loaded_model = h2o.load_model("./models/model_automl")
# model_Automl = loaded_model = h2o.load_model("C:/Users/Pichau/Desktop/eo-fut-live/models/model_automl")

preprocessor = pickle.load(
                        open('models/preprocessor.pickle', 'rb'))


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
        print(f'🤖 {numero_jogos} jogos encontrados\n')

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

            print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {awayTeamScore} x {homeTeamScore} ({league})')

            for key, value in id_jogos_mensagem.items():
                if key == 'id_over05HTmodel':
                    for jogos in value:
                        if jogos['id'] == iD:
                            editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem
                                                
    🚨 Jogo: {homeTeam} x {awayTeam}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
        ''')
                if key == 'id_over05HTAutoml':
                    for jogos in value:
                        if jogos['id'] == iD:
                            editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTAutoml)} 👑 Modelo Automl
                                            
    🚨 Jogo: {homeTeam} x {awayTeam}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
        ''')
                                            
                


            # rede neural
            if iD in id_over05HTmodel:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_model += 1
                    id_over05HTmodel.remove(iD)
                    
                    valor = valorEsperado - 5
                    lucro += valor

                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTmodel':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem

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
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
    ''')
                    
                                    # remove do dicionario
                                    id_jogos_mensagem[key].remove(jogos)

                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_model += 1
                    id_over05HTmodel.remove(iD)
                    lucro -= 5
                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTmodel':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem

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
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
    ''')
                                    # remove do dicionario
                                    id_jogos_mensagem[key].remove(jogos)
            
            

            # Automl
            if iD in id_over05HTAutoml:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_Automl += 1
                    id_over05HTAutoml.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor
                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTAutoml':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTAutoml)} 👑 Modelo Automl

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
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
    ''')
                                    # remove do dicionario
                                    id_jogos_mensagem[key].remove(jogos)
                
                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_Automl += 1
                    id_over05HTAutoml.remove(iD)
                    lucro -= 5
                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTAutoml':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTAutoml)} 👑 Modelo Automl
                                                        
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
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
    ''')
                                    # remove do dicionario
                                    id_jogos_mensagem[key].remove(jogos)
            


            condicao5min = 0
            condicao5min_Automl = 0

            if minute >= 1 and minute < 45:
                try:
                    Xht = preprocessor.transform(Xht)
                    Xht_h2o = h2o.H2OFrame(Xht)


                except Exception as e:
                    print(e)
                    continue

                if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                    value_pred_rede = model.predict(Xht)[0][0]
                    value_pred_automl = h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']
                     
                    print(
                        f'{homeTeam} x {awayTeam} rede: {value_pred_rede}')

                    print(
                        f"{homeTeam} x {awayTeam} Automl: {value_pred_automl}")
                    
                    if value_pred_rede >= 0.75:

                        condicao5min = 1

                    if value_pred_automl >= 0.75:
                        condicao5min_Automl = 1


            if condicao5min == 1 and iD not in id_over05HTmodel:
                id_over05HTmodel.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTmodel)} 👑 Modelo Rede Neural 

    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {value_pred_rede}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''

                if '&' in text:
                    text = text.replace('&', '')
                id_jogos_mensagem["id_over05HTmodel"].append({"id": iD, "message_id": sendMenssageTelegram(text)})

            if condicao5min_Automl == 1 and iD not in id_over05HTAutoml:
                id_over05HTAutoml.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl 
    
    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {value_pred_automl}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''
                if '&' in text:
                    text = text.replace('&', '')
                id_jogos_mensagem["id_over05HTAutoml"].append({"id": iD, "message_id": sendMenssageTelegram(text)})
            
        time.sleep(60)
    except Exception as e:
        traceback.print_exc()
        print(e)
        continue
