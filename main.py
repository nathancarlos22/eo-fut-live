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

model = keras.models.load_model('models/model_redeht.h5')
# model_Randomf = pickle.load(open('models/model_randomf_Brazil - Serie A.sav', 'rb')) # inicializado

# Inicializar o cluster H2O
h2o.init()
model_Automl = loaded_model = h2o.load_model("./models/model_automl")
# model_Automl = loaded_model = h2o.load_model("C:/Users/Pichau/Desktop/eo-fut-live/models/model_automl")

preprocessor = pickle.load(open('models/preprocessor.pickle', 'rb'))
preprocessor_league = pickle.load(open('models/preprocessor_league.pickle','rb'))


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
value_pred_randomf = 0

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
                'blockedShotsHome': shotsBlocked_home,
                'blockedShotsAway': shotsBlocked_away,
                

            }

            Xht = pd.DataFrame(novo_dado, index=[0])
            
            # Tratando ligas com nomes diferentes, varios grupos, etc..
            if 'Asia - AFC Champions League' in league:
                league = 'Asia - AFC Champions League'
                Xht['league'] = league
            if 'Europe - Champions League' in league:
                league = 'Europe - Champions League'
                Xht['league'] = league

            Xht['shotsHome'] = Xht['shotsOngoal_home'] + Xht['shotsOffgoal_home']
            Xht['shotsAway'] = Xht['shotsOngoal_away'] + Xht['shotsOffgoal_away']

            Xht['total_cards'] = Xht['yellowcards_home'] + Xht['yellowcards_away'] + Xht['redcards_home'] + Xht['redcards_away']
            Xht['total_cards_home'] = Xht['yellowcards_home'] + Xht['redcards_home']
            Xht['total_cards_away'] = Xht['yellowcards_away'] + Xht['redcards_away']

            # Agressividade ao longo do tempo: combinando faltas e cartões amarelos com minutos
            Xht['aggressiveness_over_time_home'] = (Xht['fouls_home'] + Xht['yellowcards_home']) * Xht['minute']
            Xht['aggressiveness_over_time_away'] = (Xht['fouls_away'] + Xht['yellowcards_away']) * Xht['minute']

            # chances de jogo
            # chances criadas por cada equipe, calculadas pela soma de chutes, faltas, escanteios e arremessos laterais
            Xht['chances_home'] = Xht['shotsOngoal_home'] + Xht['fouls_home'] + Xht['corners_home'] + Xht['offsides_home']
            Xht['chances_away'] = Xht['shotsOngoal_away'] + Xht['fouls_away'] + Xht['corners_away'] + Xht['offsides_away']

            # Defensive Pressure
            # Reflete a soma dos desarmes e chutes bloqueados pela equipe em casa/fora. Indica a intensidade com que a equipe está defendendo e impedindo o adversário de finalizar com sucesso.
            Xht['defensive_pressure_home'] = Xht['tackles_home'] + Xht['blockedShotsHome']
            Xht['defensive_pressure_away'] = Xht['tackles_away'] + Xht['blockedShotsAway']
            
            # Attack Efficiency
            # Mede a proporção de chutes ao gol em relação ao total de chutes feitos pela equipe em casa/fora. Valores mais altos indicam maior precisão nos ataques.
            Xht['attack_efficiency_home'] = (Xht['shotsOngoal_home'] / (Xht['shotsHome'] + 1))  # +1 to avoid division by zero
            Xht['attack_efficiency_away'] = (Xht['shotsOngoal_away'] / (Xht['shotsAway'] + 1))
            Xht['attack_efficiency_home'] = round(Xht['attack_efficiency_home'].values[0], 2)
            Xht['attack_efficiency_away'] = round(Xht['attack_efficiency_away'].values[0], 2)

            # Game Control
            # É o produto do tempo de posse de bola pela soma dos chutes e faltas da equipe em casa/fora. Pode ser usado para avaliar como a equipe controla o jogo através da posse e criação de chances.
            Xht['game_control_home'] = Xht['possessiontime_home'] * (Xht['shotsHome'] + Xht['fouls_home'])
            Xht['game_control_away'] = Xht['possessiontime_away'] * (Xht['shotsAway'] + Xht['fouls_away'])

            # Attack Risk
            # Calcula a razão entre chutes que não vão ao gol e o total de chutes menos os chutes ao gol para a equipe em casa/fora. Mostra a tendência da equipe em arriscar chutes que não são precisos.
            Xht['attack_risk_home'] = (Xht['shotsOffgoal_home'] / (Xht['shotsHome'] - Xht['shotsOngoal_home']+ 1))
            Xht['attack_risk_away'] = (Xht['shotsOffgoal_away'] / (Xht['shotsAway'] - Xht['shotsOngoal_away']+ 1))
            Xht['attack_risk_home'] = round(Xht['attack_risk_home'].values[0], 2)
            Xht['attack_risk_away'] = round(Xht['attack_risk_away'].values[0], 2)

            # Pressure Over Time
            # Multiplica a soma dos chutes ao gol e o tempo de posse pela duração do jogo até o momento (minutos). Esta métrica pode indicar como a pressão de jogo da equipe se acumula ao longo da partida.
            Xht['pressure_over_time_home'] = ((Xht['shotsOngoal_home'] + Xht['possessiontime_home']) * Xht['minute'])
            Xht['pressure_over_time_away'] = ((Xht['shotsOngoal_away'] + Xht['possessiontime_away']) * Xht['minute'])

            # Attack Intensity
            # Relaciona o número de chutes ao gol com o tempo de jogo, indicando a intensidade do ataque da equipe em casa/fora ao longo dos minutos da partida.
            Xht['attack_intensity_home'] = (Xht['shotsOngoal_home'] / (Xht['minute'] + 1))  # +1 to avoid division by zero
            Xht['attack_intensity_away'] = (Xht['shotsOngoal_away'] / (Xht['minute'] + 1))  # +1 to avoid division by zero
            Xht['attack_intensity_home'] = round(Xht['attack_intensity_home'].values[0], 2)
            Xht['attack_intensity_away'] = round(Xht['attack_intensity_away'].values[0], 2)

            # Defensive Performance
            # A relação entre o número de desarmes e o tempo de jogo, indicando o desempenho defensivo da equipe em casa/fora ao longo do tempo.
            Xht['defensive_performance_home'] = (Xht['tackles_home'] / (Xht['minute'] + 1))  # +1 to avoid division by zero
            Xht['defensive_performance_away'] = (Xht['tackles_away'] / (Xht['minute'] + 1))  # +1 to avoid division by zero
            Xht['defensive_performance_home'] = round(Xht['defensive_performance_home'].values[0], 2)
            Xht['defensive_performance_away'] = round(Xht['defensive_performance_away'].values[0], 2)

            # Game Momentum
            # Considera a soma dos chutes ao gol e o tempo de posse dividido pelo tempo restante na partida. Mostra a capacidade da equipe de construir ímpeto à medida que o jogo avança.
            Xht['game_momentum_home'] = ((Xht['shotsOngoal_home'] + Xht['possessiontime_home']) / (90 - Xht['minute'] + 1))
            Xht['game_momentum_away'] = ((Xht['shotsOngoal_away'] + Xht['possessiontime_away']) / (90 - Xht['minute'] + 1))
            Xht['game_momentum_home'] = round(Xht['game_momentum_home'].values[0], 2)
            Xht['game_momentum_away'] = round(Xht['game_momentum_away'].values[0], 2)

            # Progresso da posse de bola: incorporando tempo de posse e minutos
            Xht['possession_progress_home'] = (Xht['possessiontime_home'] * Xht['minute'])
            Xht['possession_progress_away'] = (Xht['possessiontime_away'] * Xht['minute'])

            # Total de faltas por jogo
            Xht['total_fouls'] = Xht['fouls_home'] + Xht['fouls_away']

            # caracteristicas sem importancia para os modelos
            Xht = Xht.drop(columns=['yellowcards_home', 'blockedShotsAway', 
                                    'yellowcards_away', 'blockedShotsHome', 
                                    'offsides_home', 'offsides_away', 'redcards_away', 
                                    'redcards_home','shotsOngoal_away', 'total_cards', 
                                    'corners_home', 'shotsOffgoal_home', 'attack_risk_home', 
                                    'shotsOffgoal_away', 'total_cards_home', 
                                    'attack_risk_away', 'corners_away', 'total_cards_away', 
                                    'minute', 'aggressiveness_over_time_home', 
                                    'pressure_over_time_home', 'aggressiveness_over_time_away', 
                                    'possession_progress_away', 'pressure_over_time_away', 
                                    'chances_home', 'game_control_home', 'possession_progress_home', 
                                    'defensive_pressure_away', 'game_momentum_away', 'chances_away'])

            shotsHome = Xht['shotsHome'].values[0]
            shotsAway = Xht['shotsAway'].values[0]
            # total_cards = Xht['total_cards'].values[0]
            # total_cards_home = Xht['total_cards_home'].values[0]
            # total_cards_away = Xht['total_cards_away'].values[0]
            # aggressiveness_over_time_home = Xht['aggressiveness_over_time_home'].values[0]
            # aggressiveness_over_time_away = Xht['aggressiveness_over_time_away'].values[0]
            # chances_home = Xht['chances_home'].values[0]
            # chances_away = Xht['chances_away'].values[0]
            defensive_pressure_home = Xht['defensive_pressure_home'].values[0]
            # defensive_pressure_away = Xht['defensive_pressure_away'].values[0]
            attack_efficiency_home = Xht['attack_efficiency_home'].values[0]
            attack_efficiency_away = Xht['attack_efficiency_away'].values[0]
            # game_control_home = Xht['game_control_home'].values[0]
            game_control_away = Xht['game_control_away'].values[0]
            # attack_risk_home = Xht['attack_risk_home'].values[0]
            # attack_risk_away = Xht['attack_risk_away'].values[0]
            # pressure_over_time_home = Xht['pressure_over_time_home'].values[0]
            # pressure_over_time_away = Xht['pressure_over_time_away'].values[0]
            attack_intensity_home = Xht['attack_intensity_home'].values[0]
            attack_intensity_away = Xht['attack_intensity_away'].values[0]
            defensive_performance_home = Xht['defensive_performance_home'].values[0]
            defensive_performance_away = Xht['defensive_performance_away'].values[0]
            game_momentum_home = Xht['game_momentum_home'].values[0]
            # game_momentum_away = Xht['game_momentum_away'].values[0]
            # possession_progress_home = Xht['possessiontime_home'].values[0]
            # possession_progress_away = Xht['possessiontime_away'].values[0]
            total_fouls = Xht['total_fouls'].values[0]

            # try:
            #     id_evento = game['betfairId']
            # except:
            #     continue

            if Xht.isna().sum().sum() > 0:
                continue

            Xht_league = Xht.drop(columns=['league'])
            print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {homeTeamScore} x {awayTeamScore} ({league})')
            print_jogos = f'''
            🚨 Jogo: {homeTeam} x {awayTeam}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    ⏰ Tempo de posse Casa: x
    ⏰ Tempo de posse Fora: x
    🎯 Chutes: {shotsHome} - {shotsAway}
    🔴 Cartões totais: x
    🟥 Cartões Casa: x
    🟨 Cartões Fora: x
    🌟 Chances criadas Casa: x
    🌟 Chances criadas Fora: x
    🛡️ Pressão defensiva Casa: x
    🛡️ Pressão defensiva Fora: x
    ⚡ Eficiência de ataque Casa: {attack_efficiency_home}
    ⚡ Eficiência de ataque Fora: {attack_efficiency_away}
    🎮 Controle do jogo Casa: x
    🎮 Controle do jogo Fora: {game_control_away}
    🔥 Risco de ataque Casa: x
    🔥 Risco de ataque Fora: x
    🕒 Pressão ao longo do tempo Casa: x
    🕒 Pressão ao longo do tempo Fora: x
    💥 Intensidade de ataque Casa: {attack_intensity_home}
    💥 Intensidade de ataque Fora: {attack_intensity_away}
    🛠️ Desempenho defensivo Casa: {defensive_performance_home}
    🛠️ Desempenho defensivo Fora: {defensive_performance_away}
    🌪️ Momentum do jogo Casa: {game_momentum_home}
    🌪️ Momentum do jogo Fora: x
    🏁 Total de faltas: {total_fouls}
    🚀 Agressividade ao longo do tempo Casa: x
    🚀 Agressividade ao longo do tempo Fora: x
'''

    #         print_jogos = f'''

    # 🚨 Jogo: {homeTeam} x {awayTeam}
    # ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    # 🏆 Liga: {league}
    # ⏱️ Minuto: {minute}

    # 📋 Estatísticas
    # 🎯 Chutes: {shotsHome} - {shotsAway}
    # 🔴 Cartões totais: {total_cards}
    # 🟥 Cartões Casa: {total_cards_home}
    # 🟨 Cartões Fora: {total_cards_away}
    # 🌟 Chances criadas Casa: {chances_home}
    # 🌟 Chances criadas Fora: {chances_away}
    # 🛡️ Pressão defensiva Casa: {defensive_pressure_home}
    # 🛡️ Pressão defensiva Fora: {defensive_pressure_away}
    # ⚡ Eficiência de ataque Casa: {attack_efficiency_home}
    # ⚡ Eficiência de ataque Fora: {attack_efficiency_away}
    # 🎮 Controle do jogo Casa: {game_control_home}
    # 🎮 Controle do jogo Fora: {game_control_away}
    # 🔥 Risco de ataque Casa: {attack_risk_home}
    # 🔥 Risco de ataque Fora: {attack_risk_away}
    # 🕒 Pressão ao longo do tempo Casa: {pressure_over_time_home}
    # 🕒 Pressão ao longo do tempo Fora: {pressure_over_time_away}
    # 💥 Intensidade de ataque Casa: {attack_intensity_home}
    # 💥 Intensidade de ataque Fora: {attack_intensity_away}
    # 🛠️ Desempenho defensivo Casa: {defensive_performance_home}
    # 🛠️ Desempenho defensivo Fora: {defensive_performance_away}
    # 🌪️ Momentum do jogo Casa: {game_momentum_home}
    # 🌪️ Momentum do jogo Fora: {game_momentum_away}
    # 🏁 Total de faltas: {total_fouls}
    # 🚀 Agressividade ao longo do tempo Casa: {aggressiveness_over_time_home}
    # 🚀 Agressividade ao longo do tempo Fora: {aggressiveness_over_time_away}

    # '''
            
            
    # 🚨 Jogo: {homeTeam} x {awayTeam}
    # ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    # 🏆 Liga: {league}
    # ⏱️ Minuto: {minute}

    # 📋 Estatísticas
    # ⛳ Escanteios: {corners_home} - {corners_away}
    # 🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    # 🔴 Faltas: {fouls_home} - {fouls_away}
    # 🛑 Desarmes: {tackles_home} - {tackles_away}
    # ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    # 📊 Aggressividade ao longo do tempo: {aggressiveness_over_time_home} - {aggressiveness_over_time_away}
    # 🛡️ Eficiência defensiva: {defensive_efficiency_away} - {defensive_performance_away}
    # ⚽ Eficiência de posse: {possession_efficiency_home} - {possession_efficiency_away}
    # 🏰 Estabilidade defensiva: {defensive_stability_home} - {defensive_stability_away}
    # 📈 Pressão ao longo do tempo: {pressure_over_time_home} - {pressure_over_time_away}
    # 🔄 Progresso de posse: {possession_progress_home} - {possession_progress_away}
    # 🛠️ Desempenho defensivo: {defensive_performance_home} - {defensive_efficiency_away}
    # 🌪️ Momentum do jogo: {game_momentum_home} - {game_momentum_away}
    # ⚖️ Eficiência de progresso no jogo: {game_progress_efficiency_home} - {game_progress_efficiency_away}
    # 🏁 Total de faltas: {total_fouls}
    # '''

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
                if key == 'id_over05HTRandomf':
                    for jogos in value:
                        if jogos['id'] == iD:
                            text = f'''
    👑 Modelo Random Forest

    💭 Previsão: {value_pred_randomf}
    {print_jogos}
    '''
                            if '&' in text:
                                text = text.replace('&', '')
                            editMessageTelegram(jogos['message_id'], text)


        #     # rede neural
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

                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
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
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
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
                
                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
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
            if iD in id_over05HTRandomf:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_Randomf += 1
                    id_over05HTRandomf.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor
                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTRandomf':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    text = f'''
        👑 Modelo Random Forest

        ✅ Win {winht_Randomf} - {loseht_Randomf}
        {print_jogos}
        '''
                                    if '&' in text:
                                        text = text.replace('&', '')
                                    sendMenssageTelegram(text)
                                    id_jogos_mensagem[key].remove(jogos)

                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_Randomf += 1
                    id_over05HTRandomf.remove(iD)
                    lucro -= 5
                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTRandomf':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    text = f'''
        👑 Modelo Random Forest

        🛑 Lose {winht_Randomf} - {loseht_Randomf}
        {print_jogos}
        '''
                                    if '&' in text:
                                        text = text.replace('&', '')
                                    sendMenssageTelegram(text)
                                    # remove do dicionario
                                    id_jogos_mensagem[key].remove(jogos)


            condicao_rede = 0
            condicao_Automl = 0
            condicao_Randomf = 0

            if minute >= 15 and minute < 45:
                try:

                    # Xht_transform = preprocessor_league.transform(Xht_league)


                    if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                        Xht = preprocessor.transform(Xht)
                        Xht_league_transform = preprocessor_league.transform(Xht_league)
                        Xht_h2o = h2o.H2OFrame(Xht)
                        # model = keras.models.load_model(f'models/model_redeht_{league}.h5')
                        model_Randomf = pickle.load(open(f'models/model_randomf_{league}.sav', 'rb'))
                        # value_pred_rede = model.predict(Xht_transform)[0][0]                      
                        
                        value_pred_rede = model.predict(Xht)[0][0]
                        value_pred_automl = h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']
                        value_pred_randomf = model_Randomf.predict_proba(Xht_league_transform)[0][1]
                        
                        print(f'{homeTeam} x {awayTeam} rede: {value_pred_rede}')
                        print(f"{homeTeam} x {awayTeam} Automl: {value_pred_automl}")
                        print(f"{homeTeam} x {awayTeam} Random Forest: {value_pred_randomf}")
                        
                        if value_pred_rede >= 0.52:

                            condicao_rede = 1

                        if value_pred_automl >= 0.52:
                            condicao_Automl = 1
                        
                        if value_pred_randomf >= 0.55:
                            condicao_Randomf = 1

                except Exception as e:
                    print(e)
                    continue

            



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

            if condicao_Randomf == 1 and iD not in id_over05HTRandomf:
                id_over05HTRandomf.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''
        👑 Modelo Random Forest

        💭 Previsão: {value_pred_randomf}
        {print_jogos}
        '''
                if '&' in text:
                    text = text.replace('&', '')
                # sendMenssageTelegram(text)
                id_jogos_mensagem["id_over05HTRandomf"].append({"id": iD, "message_id": sendMenssageTelegram(text)})

            
        time.sleep(60)
    
    except Exception as e:
        traceback.print_exc()
        print(e)
        continue
