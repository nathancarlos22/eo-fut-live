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
# import h2o
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
    "id_over05HTAutoml": [],
    "id_over05HTRandomf": []
}


id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

id_over05HTRandomf = []
winht_Randomf = 0
loseht_Randomf = 0

text = ' '
resultados = {}

minutoss = datetime.now().minute
flag = 0

# model = keras.models.load_model('models/model_redeht.h5')
# Carregar o modelo do arquivo

model = pickle.load(open('models/modelo_mlp.pkl', 'rb'))

# model_Randomf = pickle.load(open('models/model_randomf_Brazil - Serie A.sav', 'rb')) # inicializado

# Inicializar o cluster H2O
# h2o.init()
# model_Automl = loaded_model = h2o.load_model("./models/model_automl")
# model_Automl = loaded_model = h2o.load_model("C:/Users/Pichau/Desktop/eo-fut-live/models/model_automl")
model_Automl = pickle.load(open('./models/tpot_model.pkl', 'rb'))

preprocessor = pickle.load(open('models/preprocessor.pickle', 'rb'))
# preprocessor_league = pickle.load(open('models/preprocessor_league.pickle','rb'))


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
# value_pred_randomf = 0

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

        # import json

        # with open('data.json', 'w') as outfile:
        #     json.dump(dic_response, outfile)

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

            if minute == 0:
                continue

            Xht = pd.DataFrame(novo_dado, index=[0])

            # caracteristicas sem importancia para os modelos

            if Xht.isna().sum().sum() > 0:
                # print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {homeTeamScore} x {awayTeamScore} ({league})')
                # print(Xht.isna().sum())
                # time.sleep(60)
                continue
            
            # Tratando ligas com nomes diferentes, varios grupos, etc..
            if 'Asia - AFC Champions League' in league:
                league = 'Asia - AFC Champions League'
                Xht['league'] = league
            if 'Europe - Champions League' in league:
                league = 'Europe - Champions League'
                Xht['league'] = league
            
            if 'urope - Europa League' in league:
                league = 'Europe - Europa League'
                Xht['league'] = league

            Xht['shotsHome'] = Xht['shotsOngoal_home'] + Xht['shotsOffgoal_home']
            Xht['shotsAway'] = Xht['shotsOngoal_away'] + Xht['shotsOffgoal_away']

            # Desempenho Relacionado ao Ataque
            Xht['shotsOnGoalEfficiency'] = (Xht['shotsOngoal_home'] + Xht['shotsOngoal_away']) / (Xht['shotsHome'].values[0] + Xht['shotsAway'].values[0] + 1) # A eficiência do ataque em termos de chutes que realmente vão em direção ao gol.
            Xht['attackPressure'] = (Xht['shotsHome'] + Xht['shotsAway'] + Xht['corners_home'] + Xht['corners_away']) / Xht['minute'] # Uma medida de quão ofensivas as equipes estão ao longo do jogo.
            Xht['shotAccuracy_home'] = round(Xht['shotsOngoal_home'].values[0] / (Xht['shotsHome'].values[0] + 1), 2) # Proporção de chutes no gol em relação ao total de chutes.
            Xht['shotAccuracy_away'] = round(Xht['shotsOngoal_away'].values[0] / (Xht['shotsAway'].values[0] + 1), 2)

            # Desempenho Relacionado com Passes
            Xht['possessionControl'] = abs(Xht['possessiontime_home'] - Xht['possessiontime_away']) # Diferença absoluta do tempo de posse entre as equipes, indicando qual equipe dominou a posse de bola.
            Xht['passRisk'] = (Xht['offsides_home'] + Xht['offsides_away']) / (Xht['possessiontime_home'] + Xht['possessiontime_away']) # Indicativo de quão arriscados são os passes, resultando em impedimentos.

            # Desempenho Relacionado com Defesa
            Xht['defensiveDiscipline'] = (1 - (Xht['redcards_home'] + Xht['yellowcards_home'] + Xht['fouls_home'] + 
                                            Xht['redcards_away'] + Xht['yellowcards_away'] + Xht['fouls_away']) / Xht['minute']) # Uma medida de quão disciplinadas as equipes estão em termos de cartões e faltas.

            Xht['defensiveEfficacy'] = (Xht['blockedShotsHome'] + Xht['blockedShotsAway']) / round((Xht['shotsOnGoalEfficiency'].values[0] + 1), 2) # Avalia a habilidade da defesa de bloquear chutes eficientes.
            Xht['defensiveAggression'] = (Xht['tackles_home'] + Xht['tackles_away']) / Xht['minute']

            # Total de faltas por jogo
            Xht['total_fouls'] = Xht['fouls_home'] + Xht['fouls_away']

            Xht = Xht.drop(columns=['redcards_away', 'redcards_home'])
            
            shotsHome = Xht['shotsHome'].values[0]
            shotsAway = Xht['shotsAway'].values[0]
            shotsOnGoalEfficiency = Xht['shotsOnGoalEfficiency'].values[0]
            attackPressure = Xht['attackPressure'].values[0]
            shotAccuracy_home = Xht['shotAccuracy_home'].values[0]
            shotAccuracy_away = Xht['shotAccuracy_away'].values[0]
            possessionControl = Xht['possessionControl'].values[0]
            passRisk = Xht['passRisk'].values[0]
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
            total_fouls = Xht['total_fouls'].values[0]


            # try:
            #     id_evento = game['betfairId']
            # except:
            #     continue

            

            Xht_league = Xht.drop(columns=['league'])
            print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {homeTeamScore} x {awayTeamScore} ({league})')
            print_jogos = f'''
            🚨 Jogo: {homeTeam} x {awayTeam}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🎯 Chutes Casa: {shotsHome}
    🎯 Chutes Fora: {shotsAway}
    🎯 Eficiência de Chutes no Gol: {shotsOnGoalEfficiency}
    ⚡ Pressão de Ataque: {attackPressure}
    🎯 Precisão de Chutes Casa: {shotAccuracy_home}
    🎯 Precisão de Chutes Fora: {shotAccuracy_away}
    🎮 Controle de Posse: {possessionControl}
    🎲 Risco de Passe: {passRisk}
    🛡️ Disciplina Defensiva: {defensiveDiscipline}
    🛡️ Eficácia Defensiva: {defensiveEfficacy}
    🛡️ Agressão Defensiva: {defensiveAggression}
    ⛳ Escanteios: {corners_home} - {corners_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🎯 Chutes ao gol Casa: {shotsOngoal_home}
    🎯 Chutes ao gol Fora: {shotsOngoal_away}
    🦵 Chutes fora Casa: {shotsOffgoal_home}
    🦵 Chutes fora Fora: {shotsOffgoal_away}
    🚩 Impedimentos Casa: {offsides_home}
    🚩 Impedimentos Fora: {offsides_away}
    🚫 Chutes bloqueados Casa: {shotsBlocked_home}
    🚫 Chutes bloqueados Fora: {shotsBlocked_away}
    🔴 Faltas Casa: {fouls_home}
    🔴 Faltas Fora: {fouls_away}
    🛑 Desarmes Casa: {tackles_home}
    🛑 Desarmes Fora: {tackles_away}
    🏁 Total de faltas: {total_fouls}
    🟨 Cartões amarelos Casa: {yellowcards_home}
    🟨 Cartões amarelos Fora: {yellowcards_away}
'''

    #         print_jogos = f'''

    # 🚨 Jogo: {homeTeam} x {awayTeam}
    # ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    # 🏆 Liga: {league}
    # ⏱️ Minuto: {minute}

    # 🎯 Chutes Casa: {shotsHome}
    # 🎯 Chutes Fora: {shotsAway}
    # 🎯 Eficiência de Chutes no Gol: {shotsOnGoalEfficiency}
    # ⚡ Pressão de Ataque: {attackPressure}
    # 🎯 Precisão de Chutes Casa: {shotAccuracy_home}
    # 🎯 Precisão de Chutes Fora: {shotAccuracy_away}
    # 🎮 Controle de Posse: {possessionControl}
    # 🎲 Risco de Passe: {passRisk}
    # 🛡️ Disciplina Defensiva: {defensiveDiscipline}
    # 🛡️ Eficácia Defensiva: {defensiveEfficacy}
    # 🛡️ Agressão Defensiva: {defensiveAggression}
    # ⛳ Escanteios: {corners_home} - {corners_away}
    # ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    # 🔴 Cartões vermelhos Casa: {redcards_home}
    # 🔴 Cartões vermelhos Fora: {redcards_away}
    # 🎯 Chutes ao gol Casa: {shotsOngoal_home}
    # 🎯 Chutes ao gol Fora: {shotsOngoal_away}
    # 🦵 Chutes fora Casa: {shotsOffgoal_home}
    # 🦵 Chutes fora Fora: {shotsOffgoal_away}
    # 🟨 Cartões amarelos Casa: {yellowcards_home}
    # 🟨 Cartões amarelos Fora: {yellowcards_away}
    # 🔴 Faltas Casa: {fouls_home}
    # 🔴 Faltas Fora: {fouls_away}
    # 🚩 Impedimentos Casa: {offsides_home}
    # 🚩 Impedimentos Fora: {offsides_away}
    # 🛑 Desarmes Casa: {tackles_home}
    # 🛑 Desarmes Fora: {tackles_away}
    # 🚫 Chutes bloqueados Casa: {shotsBlocked_home}
    # 🚫 Chutes bloqueados Fora: {shotsBlocked_away}
    # 🏁 Total de faltas: {total_fouls}

    # '''

            condicao_rede = 0
            condicao_Automl = 0
            # condicao_Randomf = 0

            if minute > 10 and minute < 90 and status != 'HT':
                try:

                    # Xht_transform = preprocessor_league.transform(Xht_league)


                    if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                        Xht = preprocessor.transform(Xht)
                        # Xht_league_transform = preprocessor_league.transform(Xht_league)
                        # Xht_h2o = h2o.H2OFrame(Xht)
                        # model = keras.models.load_model(f'models/model_redeht_{league}.h5')
                        # model_Randomf = pickle.load(open(f'models/model_randomf_{league}.sav', 'rb'))
                        # value_pred_rede = model.predict(Xht_transform)[0][0]                      
                        
                        value_pred_rede = model.predict(Xht)[0][0]
                        # value_pred_automl = h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']
                        value_pred_automl = model_Automl.predict(Xht)[0]
                        # value_pred_randomf = model_Randomf.predict_proba(Xht_league_transform)[0][1]
                        
                        print(f'{homeTeam} x {awayTeam} rede: {value_pred_rede}')
                        print(f"{homeTeam} x {awayTeam} Automl: {value_pred_automl}")
                        # print(f"{homeTeam} x {awayTeam} Random Forest: {value_pred_randomf}")
                        
                        if value_pred_rede >= 0.52:

                            condicao_rede = 1

                        if value_pred_automl >= 0.52:
                            condicao_Automl = 1
                        
                        # if value_pred_randomf >= 0.55:
                        #     condicao_Randomf = 1

                except Exception as e:
                    print(e)
                    continue

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
    #                         if '&' in text:
    #                             text = text.replace('&', '')
    #                         editMessageTelegram(jogos['message_id'], text)
    #             if key == 'id_over05HTRandomf':
    #                 for jogos in value:
    #                     if jogos['id'] == iD:
    #                         text = f'''
    # 👑 Modelo Random Forest

    # 💭 Previsão: {value_pred_randomf}
    # {print_jogos}
    # '''
                            # if '&' in text:
                            #     text = text.replace('&', '')
                            # editMessageTelegram(jogos['message_id'], text)


        #     # rede neural
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
                if status == 'HT' or minute == 90 and (awayTeamScore + homeTeamScore) == 0:
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
                                    # editMessageTelegram(jogos['message_id'], f'''{len(id_over05HTmodel)} 
    
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
                
                # if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                if status == 'HT' or minute == 90 and (awayTeamScore + homeTeamScore) == 0:
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
            
            # Random Forest
        #     if iD in id_over05HTRandomf:
        #         if minute <= 90 and (awayTeamScore + homeTeamScore) > 0:
        #             winht_Randomf += 1
        #             id_over05HTRandomf.remove(iD)
        #             valor = valorEsperado - 5
        #             lucro += valor
        #             for key, value in id_jogos_mensagem.items():
        #                 if key == 'id_over05HTRandomf':
        #                     for jogos in value:
        #                         if jogos['id'] == iD:
        #                             text = f'''
        # 👑 Modelo Random Forest

        # ✅ Win {winht_Randomf} - {loseht_Randomf}
        # {print_jogos}
        # '''
        #                             if '&' in text:
        #                                 text = text.replace('&', '')
        #                             sendMenssageTelegram(text)
        #                             id_jogos_mensagem[key].remove(jogos)

                # if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    # if minute == 90 and (awayTeamScore + homeTeamScore) == 0:
        #             loseht_Randomf += 1
        #             id_over05HTRandomf.remove(iD)
        #             lucro -= 5
        #             for key, value in id_jogos_mensagem.items():
        #                 if key == 'id_over05HTRandomf':
        #                     for jogos in value:
        #                         if jogos['id'] == iD:
        #                             text = f'''
        # 👑 Modelo Random Forest

        # 🛑 Lose {winht_Randomf} - {loseht_Randomf}
        # {print_jogos}
        # '''
        #                             if '&' in text:
        #                                 text = text.replace('&', '')
        #                             sendMenssageTelegram(text)
        #                             # remove do dicionario
        #                             id_jogos_mensagem[key].remove(jogos)


            

            



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
                # sendMenssageTelegram(text)
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

        #     if condicao_Randomf == 1 and iD not in id_over05HTRandomf:
        #         id_over05HTRandomf.append(iD)
        #         # state, valorEsperado = makeBet(id_evento)
        #         state, valorEsperado = 'SUCCESS', 10

        #         text = f'''
        # 👑 Modelo Random Forest

        # 💭 Previsão: {value_pred_randomf}
        # {print_jogos}
        # '''
        #         if '&' in text:
        #             text = text.replace('&', '')
        #         # sendMenssageTelegram(text)
        #         id_jogos_mensagem["id_over05HTRandomf"].append({"id": iD, "message_id": sendMenssageTelegram(text)})

            
        time.sleep(60)
    
    except Exception as e:
        traceback.print_exc()
        time.sleep(60)
        print(e)
        continue
