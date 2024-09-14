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
from rapidfuzz import fuzz
import betfairlightweight
import configparser
import unicodedata
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
warnings.filterwarnings('ignore')

load_dotenv()

def calculate_similarity(vector, reference):
    return np.array([fuzz.ratio(reference, x) for x in vector])


# Define a function to normalize text using unicodedata
def normalize_text_unicode(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text.lower()

# Apply the function to the relevant columns
dataframe = pd.read_csv('src/data_live_engineer_filtered.csv', encoding='utf-8')

dataframe['league'] = dataframe['league'].apply(normalize_text_unicode)
dataframe['homeTeam'] = dataframe['homeTeam'].apply(normalize_text_unicode)
dataframe['awayTeam'] = dataframe['awayTeam'].apply(normalize_text_unicode)

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

def calculate_efficiency_attack(df):
    df['shotAccuracy_home'] = df['shotsOngoal_home'] / (df['shots_home'] + 0.01)
    df['shotAccuracy_away'] = df['shotsOngoal_away'] / (df['shots_away'] + 0.01)

def calculate_defense_performance(df):
    df['attackPressureOverTime_home'] = (df['shots_home'] + df['corners_home']) / df['minute']
    df['attackPressureOverTime_away'] = (df['shots_away'] + df['corners_away']) / df['minute']

    df['aggrressionOverTime_home'] = (df['redcards_home'] + df['yellowcards_home'] + df['fouls_home']) / df['minute']
    df['aggresssionOverTime_away'] = (df['redcards_away'] + df['yellowcards_away'] + df['fouls_away']) / df['minute']

    df['defensiveEfficacy_home'] = df['blockedShots_home'] / (df['shotsOngoal_home'] + 0.01) # chutes que foram bloqueados e chutes que foram no gol da equipe adversaria
    df['defensiveEfficacy_away'] = df['blockedShots_away'] / (df['shotsOngoal_away'] + 0.01) 

    df['taklesOverTime_home'] = df['tackles_home'] / df['minute']
    df['taklesOverTime_away'] = df['tackles_away'] / df['minute']

def calculate_passing_performance(df):
    df['possessionControl'] = abs(df['possessiontime_home'] - df['possessiontime_away'])
    df['passRisk_home'] = df['offsides_home'] / (df['possessiontime_home'] + 0.01)
    df['passRisk_away'] = df['offsides_away'] / (df['possessiontime_away'] + 0.01)

def calculate_cards(df):
    df['TotalCards_home'] = df['redcards_home'] + df['yellowcards_home']
    df['TotalCards_away'] = df['redcards_away'] + df['yellowcards_away']

id_jogos_mensagem = {
    "id_over05HTmodel": [],
    "id_over05HTRandomForest": [],
}


id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTRandomForest = []
winht_RandomForest = 0
loseht_RandomForest = 0

text = ' '
resultados = {}

minutoss = datetime.now().minute
flag = 0

id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTRandomForest = []
winht_RandomForest = 0
loseht_RandomForest = 0

id_evento = ''

value_pred_rede = 0
predictions = 0

df_jogos = {}

# Criar uma sessão
session = requests.Session()

while True:
    print('🤖 Procurando jogos...\n')

    try:

        url = "https://playscores.sportsat.app/gateway/api/v1/fixtures-svc/v2/fixtures/livescores?include=league,stats,pressureStats&take=3000"

        payload = ""
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'If-Modified-Since': 'Sun, 28 Jul 2024 17:44:41 GMT',
            'Origin': 'https://www.playscores.com',
            'Referer': 'https://www.playscores.com/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

        }

        response = session.request(
            "GET", url, data=payload, headers=headers)

        dic_response = response.json()
        numero_jogos = len(dic_response['data'])
        print(f'🤖 {numero_jogos} jogos ao vivo\n')


        for game in dic_response['data']:
            try:
                date = game['date']

                awayTeam = game['awayTeam']['name']
                homeTeam = game['homeTeam']['name']
                leagueName = game['league']['name']
                countryName = game['league']['countryName']
                league = f'{countryName} - {leagueName}'
                league = normalize_text_unicode(league)
                minute = game['currentTime']['minute']
                second = game['currentTime']['second']
                awayTeamScore = game['scores']['awayTeamScore']
                homeTeamScore = game['scores']['homeTeamScore']

                try:
                    injuryTime = int(game['currentTime']['injuryTime'])
                    extraMinute = int(game['currentTime']['extraMinute'])
                except:
                    injuryTime = 0
                    extraMinute = 0

                
                if minute == None:
                    minute = 0
                if second == None:
                    second = 0
                
                minute = f'{minute}.{second}'
                minute = float(minute)

                status = game['status']

                if game['stats'] == None:
                    continue

                iD = game['stats']['fixtureId']

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
                    'homeTeam': homeTeam,
                    'awayTeam': awayTeam,
                    'goal_home': goals_home,
                    'goal_away': goals_away,
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
                    'blockedShots_home': shotsBlocked_home,
                    'blockedShots_away': shotsBlocked_away,
                    

                }

                Xht = pd.DataFrame(novo_dado, index=[0])
                
                
                Xht['shots_home'] = Xht['shotsOngoal_home'] + Xht['shotsOffgoal_home']
                Xht['shots_away'] = Xht['shotsOngoal_away'] + Xht['shotsOffgoal_away']

                if minute > 1:
                    calculate_efficiency_attack(Xht)
                    calculate_defense_performance(Xht)
                    calculate_passing_performance(Xht)
                    calculate_cards(Xht)

                    Xht['league'] = Xht['league'].apply(normalize_text_unicode)
                    Xht['homeTeam'] = Xht['homeTeam'].apply(normalize_text_unicode)
                    Xht['awayTeam'] = Xht['awayTeam'].apply(normalize_text_unicode)
                    Xht['match_result'] = 0

                    

                    ligas_df = dataframe['league'].unique()

                    for l in ligas_df:
                        if league in l:
                            league = l
                    
                    if league not in ligas_df:
                        string_mais_similar_league = max(ligas_df, key=lambda item: fuzz.ratio(item, league))
                        league = string_mais_similar_league

                    dataframe_league = dataframe[dataframe['league'] == league]
                    if dataframe_league.shape[0] == 0:
                        print('Dataframe vazio')
                        continue

                    gols_columns = ['win_rate_home', 'draw_rate_home', 'loss_rate_home',
                                    'win_rate_away', 'draw_rate_away', 'loss_rate_away', 'f_attack_home',
                                    'f_attack_away', 'f_defensive_home', 'f_defensive_away', '05ht_home',
                                    '15ht_home', '25ht_home', '05ht_away', '15ht_away', '25ht_away']
                    
                    for gols_c in gols_columns:
                        if 'home' in gols_c:
                            Xht[gols_c] = dataframe_league.tail(1)[gols_c].values[0]
                        if 'away' in gols_c:
                            Xht[gols_c] = dataframe_league.tail(1)[gols_c].values[0]

                    # colunas_nulas = Xht.columns[Xht.isnull().any()].tolist()
                    # print("Colunas nulas: ", colunas_nulas)
                    
                    Xht.fillna(0, inplace=True)

                    shotsHome = Xht['shots_home'].values[0]
                    shotsAway = Xht['shots_away'].values[0]
                    shots_home = Xht['shots_home'].values[0]
                    shots_away = Xht['shots_away'].values[0]
                    league = Xht['league'].values[0]
                    corners_home = Xht['corners_home'].values[0]
                    corners_away = Xht['corners_away'].values[0]
                    shotsOffgoal_home = Xht['shotsOffgoal_home'].values[0]
                    shotsOffgoal_away = Xht['shotsOffgoal_away'].values[0]
                    fouls_home = Xht['fouls_home'].values[0]
                    fouls_away = Xht['fouls_away'].values[0]
                    tackles_home = Xht['tackles_home'].values[0]
                    tackles_away = Xht['tackles_away'].values[0]
                    possessiontime_home = Xht['possessiontime_home'].values[0]
                    possessiontime_away = Xht['possessiontime_away'].values[0]
                    f_attack_home = Xht['f_attack_home'].values[0]
                    f_defensive_away = Xht['f_defensive_away'].values[0]
                    f_defensive_home = Xht['f_defensive_home'].values[0]
                    f_attack_away = Xht['f_attack_away'].values[0]
                    win_rate_home = Xht['win_rate_home'].values[0]
                    win_rate_away = Xht['win_rate_away'].values[0]
                    loss_rate_home = Xht['loss_rate_home'].values[0]
                    loss_rate_away = Xht['loss_rate_away'].values[0]
                    draw_rate_home = Xht['draw_rate_home'].values[0]
                    draw_rate_away = Xht['draw_rate_away'].values[0]
                    shotAccuracy_home = Xht['shotAccuracy_home'].values[0]
                    shotAccuracy_away = Xht['shotAccuracy_away'].values[0]
                    attackPressureOverTime_home = Xht['attackPressureOverTime_home'].values[0]
                    attackPressureOverTime_away = Xht['attackPressureOverTime_away'].values[0]
                    aggrressionOverTime_home = Xht['aggrressionOverTime_home'].values[0]
                    aggresssionOverTime_away = Xht['aggresssionOverTime_away'].values[0]
                    defensiveEfficacy_home = Xht['defensiveEfficacy_home'].values[0]
                    defensiveEfficacy_away = Xht['defensiveEfficacy_away'].values[0]
                    possessiontime_home = Xht['possessiontime_home'].values[0]
                    possessiontime_away = Xht['possessiontime_away'].values[0]
                    taklesOverTime_home = Xht['taklesOverTime_home'].values[0]
                    taklesOverTime_away = Xht['taklesOverTime_away'].values[0]
                    passRisk_home = Xht['passRisk_home'].values[0]
                    passRisk_away = Xht['passRisk_away'].values[0]
                    zero_meioht_home = Xht['05ht_home'].values[0]
                    zero_meio_ht_away = Xht['05ht_away'].values[0]
                    
                    print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {homeTeamScore} x {awayTeamScore} ({league})')
                    print_jogos = f'''
                    🚨 Jogo: {homeTeam} x {awayTeam}
                    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
                    🏆 Liga: {league}
                    ⏱️ Minuto: {minute}

                    📋 Estatísticas
                    🎯 Chutes: {shotsHome} x {shotsAway}
                    🎯 Precisão de Chutes: {shotAccuracy_home:.2f} x {shotAccuracy_away:.2f}
                    ⚔️ Força de Ataque: {f_attack_home:.2f} x {f_attack_away:.2f}
                    🛡️ Força Defensiva: {f_defensive_home:.2f} x {f_defensive_away:.2f}
                    ⛳ Escanteios: {corners_home:.2f} x {corners_away:.2f}
                    🦵 Chutes Fora: {shotsOffgoal_home:.2f} x {shotsOffgoal_away:.2f}
                    🔴 Faltas: {fouls_home:.2f} x {fouls_away:.2f}
                    🛑 Desarmes: {tackles_home:.2f} x {tackles_away:.2f}
                    ⏰ Tempo de Posse: {possessiontime_home:.2f} x {possessiontime_away:.2f}
                    🎮 Controle de Posse: {possessiontime_home:.2f} x {possessiontime_away:.2f}
                    🏅 Taxa de Vitória: {win_rate_home:.2f} x {win_rate_away:.2f}
                    🏅 Taxa de Derrota: {loss_rate_home:.2f} x {loss_rate_away:.2f}
                    🏅 Taxa de Empate: {draw_rate_home:.2f} x {draw_rate_away:.2f}
                    ⚡ Pressão de Ataque ao Longo do Tempo: {attackPressureOverTime_home:.2f} x {attackPressureOverTime_away:.2f}
                    🚀 Agressividade ao Longo do Tempo: {aggrressionOverTime_home:.2f} x {aggresssionOverTime_away:.2f}
                    🛡️ Eficácia Defensiva: {defensiveEfficacy_home:.2f} x {defensiveEfficacy_away:.2f}
                    🎲 Risco de Passe: {passRisk_home:.2f} x {passRisk_away:.2f}
                    📊 Desarmes ao Longo do Tempo: {taklesOverTime_home:.2f} x {taklesOverTime_away:.2f}
                    📈 Zero a Meio Tempo: {zero_meioht_home:.2f} x {zero_meio_ht_away:.2f}
                    
                    '''


                    condicao_rede = 0
                    condicao_RandomForest = 0

                    # if status == 'LIVE' and minute <= 45:
                    if status == 'LIVE':
                        if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                            try:
                                X = dataframe_league.drop(['result', 'league', 'match_id', 'homeTeam', 'awayTeam'], axis=1)
                                colunas = X.columns

                                y = dataframe_league['result']

                                smote = SMOTE(random_state=42)

                                # Split the df into training and testing sets
                                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                                
                                X_train, y_train = smote.fit_resample(X_train, y_train)

                                # Normalize numerical features
                                scaler = StandardScaler()
                                X_train = scaler.fit_transform(X_train)
                                Xht = Xht[colunas]
                                Xht = scaler.transform(Xht)

                                # Train a Random Forest classifier
                                model = RandomForestClassifier(random_state=42)
                                model.fit(X_train, y_train)

                            except Exception as e:
                                traceback.print_exc()
                                continue
                            
                            
                            predictions = model.predict(Xht)[0]
                            
                            print(f"{homeTeam} x {awayTeam} RandomForest: {predictions}")
                            
                            if predictions >= 0.52:
                                condicao_RandomForest = 1

                            

                    for key, value in id_jogos_mensagem.items():
                        if key == 'id_over05HTRandomForest':
                            for jogos in value:
                                if jogos['id'] == iD:
                                    text = f'''
                                    👑 Modelo RandomForest
                                                                            
                                    💭 Previsão: {predictions}
                                    {print_jogos}
                                    '''
                                    if '&' in text:
                                        text = text.replace('&', '')
                                    editMessageTelegram(jogos['message_id'], text)


                    # RandomForest
                    if iD in id_over05HTRandomForest:
                        if (awayTeamScore + homeTeamScore) > 0:
                            winht_RandomForest += 1
                            id_over05HTRandomForest.remove(iD)
                            
                            for key, value in id_jogos_mensagem.items():
                                if key == 'id_over05HTRandomForest':
                                    for jogos in value:
                                        if jogos['id'] == iD:
                                            text = f'''
                                            👑 Modelo RandomForest

                                            ✅ Win {winht_RandomForest} - {loseht_RandomForest}
                                            {print_jogos}
                                            '''
                                            if '&' in text:
                                                text = text.replace('&', '')
                                            sendMenssageTelegram(text)
                                            id_jogos_mensagem[key].remove(jogos)
                        
                        if (minute > 45 and (awayTeamScore + homeTeamScore) == 0):
                            loseht_RandomForest += 1
                            id_over05HTRandomForest.remove(iD)
                            
                            # lucro -= 5
                            for key, value in id_jogos_mensagem.items():
                                if key == 'id_over05HTRandomForest':
                                    for jogos in value:
                                        if jogos['id'] == iD:
                                            text = f'''
                                            👑 Modelo RandomForest
                                                                                                
                                            🛑 Lose {winht_RandomForest} - {loseht_RandomForest}
                                            {print_jogos}
                                            '''
                                            if '&' in text:
                                                text = text.replace('&', '')
                                            
                                            sendMenssageTelegram(text)
                                            id_jogos_mensagem[key].remove(jogos)

                    if condicao_RandomForest == 1 and iD not in id_over05HTRandomForest:
                        id_over05HTRandomForest.append(iD)

                        text = f'''
                        👑 Modelo RandomForest 
                        
                        💭 Previsão: {predictions}
                        {print_jogos}
                        '''
                        if '&' in text:
                            text = text.replace('&', '')

                        id_jogos_mensagem["id_over05HTRandomForest"].append({"id": iD, "message_id": sendMenssageTelegram(text)})
            except Exception as e:
                time.sleep(60)
                traceback.print_exc()
                continue
        
        time.sleep(60)
    
    except Exception as e:
        traceback.print_exc()
        time.sleep(60)
        print(e)
        continue
