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


def calculate_similarity(vector, reference):
    return np.array([fuzz.ratio(reference, x) for x in vector])


# Implementar o agente de Q-learning
state_size = 20
class QLearningAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.01
        self.memory = []

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        return np.argmax(self.q_table[state])

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = np.random.choice(len(self.memory), batch_size, replace=False)
        for index in minibatch:
            state, action, reward, next_state, done = self.memory[index]
            target = reward if done else reward + self.gamma * np.max(self.q_table[next_state])
            self.q_table[state][action] += self.learning_rate * (target - self.q_table[state][action])
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# Carregar o agente salvo
with open('models/best_q_learning_agent.pkl', 'rb') as f:
    saved_agent = pickle.load(f)

# Função para simular apostas ao vivo com o agente salvo
def simulate_with_saved_agent(agent, X_new):
    betting_stats = []
    for i in range(len(X_new)):
        state = prepare_state(X_new[i])
        action = agent.act(state)
        betting_stats.append((X_new[i], action))
    return betting_stats

# Função para preparar estado
def prepare_state(data_row):
    return int(data_row.sum()) % state_size

# Função para preparar dados
def prepare_data(df):
    X = df.drop(columns=['result', 'homeTeam', 'awayTeam', 'match_id'])
    y = df['result']
    return X, y

# Função para criar e aplicar o transformador de colunas
def create_preprocessor(X):
    numeric_features = X.select_dtypes(exclude=['object']).columns.tolist()
    categorical_features = ['league']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first'), categorical_features)
        ])
    return preprocessor.fit(X)

# Função para simular apostas ao vivo com os novos parâmetros
def simulate_live_betting(agent, X_test, y_test):
    total_money = 0
    betting_stats = []
    for i in range(len(X_test)):
        state = prepare_state(X_test[i])
        action = agent.act(state)
        if action == 1:  # Fez uma aposta
            reward = 100 if y_test.iloc[i] == 1 else -100
            total_money += reward
        else:
            reward = 0
        next_state = prepare_state(X_test[(i + 1) % len(X_test)])
        agent.remember(state, action, reward, next_state, reward != 0)
        agent.replay(batch_size)
        betting_stats.append((X_test[i], action, reward))
    return total_money, betting_stats

# Função para preparar estado
def prepare_state(data_row):
    return int(data_row.sum()) % state_size


warnings.filterwarnings('ignore')

load_dotenv()

dataframe = pd.read_csv('src/data_live_engineer_filtered.csv', encoding='utf-8')

# renomeando colunas para um padrao _home e _away
colunas = ['goal', 'shots', 'blockedShots' ]
for coluna in colunas:
    dataframe.rename(columns={coluna+'Home': coluna+'_home'}, inplace=True)
    dataframe.rename(columns={coluna+'Away': coluna+'_away'}, inplace=True)

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
model_Automl = joblib.load('./models/tpot_model.pkl')

preprocessor = pickle.load(open('models/preprocessor.pickle', 'rb'))

id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

id_evento = ''

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
            try:
                date = game['date']

                awayTeam = game['awayTeam']['name']
                homeTeam = game['homeTeam']['name']
                leagueName = game['league']['name']
                countryName = game['league']['countryName']
                league = f'{countryName} - {leagueName}'
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

                Xht.fillna(0, inplace=True)
                if minute > 1:
                    calculate_efficiency_attack(Xht)
                    calculate_defense_performance(Xht)
                    calculate_passing_performance(Xht)
                    calculate_cards(Xht)

                    gols_columns = ['f_attack_home', 'f_defensive_away', 'f_defensive_home', 'f_attack_away',
                                    'win_rate_home', 'loss_rate_home', 'draw_rate_home', 'win_rate_away',
                                    'loss_rate_away', 'draw_rate_away', '05ht_home', '05ht_away']

                    ligas_df = dataframe['league'].unique()

                    for l in ligas_df:
                        if league in l:
                            league = l
                            # break
                    
                    if league not in ligas_df:
                        continue
                    
                    
                    dataframe_league = dataframe[dataframe['league'] == league]

                    dataframe_league['similaridade_home'] = calculate_similarity(dataframe_league['homeTeam'], homeTeam)
                    dataframe_league['similaridade_away'] = calculate_similarity(dataframe_league['awayTeam'], awayTeam)

                    # Encontrando a string com a maior similaridade (usando a abordagem vetorizada)
                    string_mais_similar_home = dataframe_league.loc[dataframe_league['similaridade_home'].idxmax()]['homeTeam']
                    string_mais_similar_away = dataframe_league.loc[dataframe_league['similaridade_away'].idxmax()]['awayTeam']
                    
                    for gols_c in gols_columns:
                        if 'home' in gols_c:
                            Xht[gols_c] = dataframe_league[dataframe_league['homeTeam'] == string_mais_similar_home][gols_c].tail(1).values[0]
                        else:
                            Xht[gols_c] = dataframe_league[dataframe_league['awayTeam'] == string_mais_similar_away][gols_c].tail(1).values[0]

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
                    loss_rate_home = Xht['loss_rate_home'].values[0]
                    draw_rate_home = Xht['draw_rate_home'].values[0]
                    win_rate_away = Xht['win_rate_away'].values[0]
                    loss_rate_away = Xht['loss_rate_away'].values[0]
                    draw_rate_away = Xht['draw_rate_away'].values[0]
                    shotAccuracy_home = Xht['shotAccuracy_home'].values[0]
                    shotAccuracy_away = Xht['shotAccuracy_away'].values[0]
                    attackPressureOverTime_home = Xht['attackPressureOverTime_home'].values[0]
                    attackPressureOverTime_away = Xht['attackPressureOverTime_away'].values[0]
                    aggrressionOverTime_home = Xht['aggrressionOverTime_home'].values[0]
                    aggresssionOverTime_away = Xht['aggresssionOverTime_away'].values[0]
                    defensiveEfficacy_home = Xht['defensiveEfficacy_home'].values[0]
                    # defensiveEfficacy_away = Xht['defensiveEfficacy_away'].values[0]
                    possessionControl = Xht['possessionControl'].values[0]
                    taklesOverTime_home = Xht['taklesOverTime_home'].values[0]
                    taklesOverTime_away = Xht['taklesOverTime_away'].values[0]
                    passRisk_home = Xht['passRisk_home'].values[0]
                    passRisk_away = Xht['passRisk_away'].values[0]
                    zero_meioht_home = Xht['05ht_home'].values[0]
                    # zero_meioft_home = Xht['05ft_home'].values[0]
                    # zero_meio_home = Xht['05_home'].values[0]
                    zero_meio_ht_away = Xht['05ht_away'].values[0]
                    # zero_meioft_away = Xht['05ft_away'].values[0]
                    # zero_meio_away = Xht['05_away'].values[0]
                    
                    print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {homeTeamScore} x {awayTeamScore} ({league})')
                    print_jogos = f'''
                    🚨 Jogo: {homeTeam} x {awayTeam}
                    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
                    🏆 Liga: {league}
                    ⏱️ Minuto: {minute}

                    📋 Estatísticas
                    🎯 Chutes Casa: {shotsHome}
                    🎯 Chutes Fora: {shotsAway}
                    🎯 Precisão de Chutes Casa: {shotAccuracy_home:.2f}
                    🎯 Precisão de Chutes Fora: {shotAccuracy_away:.2f}
                    ⚔️ Força de Ataque Casa: {f_attack_home:.2f}
                    ⚔️ Força de Ataque Fora: {f_attack_away:.2f}
                    🛡️ Força Defensiva Casa: {f_defensive_home:.2f}
                    🛡️ Força Defensiva Fora: {f_defensive_away:.2f}
                    ⛳ Escanteios: {corners_home:.2f} - {corners_away:.2f}
                    🦵 Chutes fora Casa: {shotsOffgoal_home:.2f}
                    🦵 Chutes fora Fora: {shotsOffgoal_away:.2f}
                    🔴 Faltas Casa: {fouls_home:.2f}
                    🔴 Faltas Fora: {fouls_away:.2f}
                    🛑 Desarmes Casa: {tackles_home:.2f}
                    🛑 Desarmes Fora: {tackles_away:.2f}
                    ⏰ Tempo de posse Casa: {possessiontime_home:.2f}
                    ⏰ Tempo de posse Fora: {possessiontime_away:.2f}
                    🎮 Controle de Posse: {possessionControl:.2f}
                    🏅 Taxa de vitória Casa: {win_rate_home:.2f}
                    🏅 Taxa de derrota Casa: {loss_rate_home:.2f}
                    🏅 Taxa de empate Casa: {draw_rate_home:.2f}
                    🏅 Taxa de vitória Fora: {win_rate_away:.2f}
                    🏅 Taxa de derrota Fora: {loss_rate_away:.2f}
                    🏅 Taxa de empate Fora: {draw_rate_away:.2f}
                    ⚡ Pressão de Ataque ao Longo do Tempo Casa: {attackPressureOverTime_home:.2f}
                    ⚡ Pressão de Ataque ao Longo do Tempo Fora: {attackPressureOverTime_away:.2f}
                    🚀 Agressividade ao Longo do Tempo Casa: {aggrressionOverTime_home:.2f}
                    🚀 Agressividade ao Longo do Tempo Fora: {aggresssionOverTime_away:.2f}
                    🛡️ Eficácia Defensiva Casa: {defensiveEfficacy_home:.2f}
                    🎲 Risco de Passe Casa: {passRisk_home:.2f}
                    🎲 Risco de Passe Fora: {passRisk_away:.2f}
                    📊 Desarmes ao Longo do Tempo Casa: {taklesOverTime_home:.2f}
                    📊 Desarmes ao Longo do Tempo Fora: {taklesOverTime_away:.2f}
                    📈 Zero a Meio Tempo Casa: {zero_meioht_home:.2f}
                    📈 Zero a Meio Tempo Fora: {zero_meio_ht_away:.2f}

                    '''

                    condicao_rede = 0
                    condicao_Automl = 0

                    # ordenando as colunas
                    colunas = ['minute', 'shots_home', 'shots_away', 'league', 'corners_home',
                                'corners_away', 'shotsOffgoal_home', 'shotsOffgoal_away',
                                'shotsOngoal_home', 'fouls_home', 'fouls_away', 'tackles_home',
                                'tackles_away', 'possessiontime_away', 'possessiontime_home',
                                'f_attack_home', 'f_defensive_away', 'f_defensive_home',
                                'f_attack_away', 'win_rate_home', 'loss_rate_home', 'draw_rate_home',
                                'win_rate_away', 'loss_rate_away', 'draw_rate_away',
                                'shotAccuracy_home', 'shotAccuracy_away', 'attackPressureOverTime_home',
                                'attackPressureOverTime_away', 'aggrressionOverTime_home',
                                'aggresssionOverTime_away', 'defensiveEfficacy_home',
                                'defensiveEfficacy_away', 'taklesOverTime_home', 'taklesOverTime_away',
                                'possessionControl', 'passRisk_home', 'passRisk_away', '05ht_home',
                                '05ft_home', '05_home', '05ht_away', '05ft_away', '05_away']
                    
                    Xht = Xht[colunas]

                    if status == 'LIVE' and minute < 45:

                        if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                            try:
                                Xht = preprocessor.transform(Xht)
                            except Exception as e:
                                traceback.print_exc()
                                continue

                            # value_pred_automl = model_Automl.predict(Xht)[0]
                            value_pred_automl = simulate_with_saved_agent(saved_agent, Xht)[0][1]

                            
                            print(f"{homeTeam} x {awayTeam} Automl: {value_pred_automl}")
                            
                            if value_pred_automl >= 0.52:
                                condicao_Automl = 1

                            

                    for key, value in id_jogos_mensagem.items():
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


                    # Automl
                    if iD in id_over05HTAutoml:
                        if (awayTeamScore + homeTeamScore) > 0:
                            winht_Automl += 1
                            id_over05HTAutoml.remove(iD)
                            
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
                        
                        if (minute > 45 and (awayTeamScore + homeTeamScore) == 0):
                            loseht_Automl += 1
                            id_over05HTAutoml.remove(iD)
                            
                            # lucro -= 5
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
                                            id_jogos_mensagem[key].remove(jogos)

                    if condicao_Automl == 1 and iD not in id_over05HTAutoml:
                        id_over05HTAutoml.append(iD)

                        text = f'''
                        👑 Modelo Automl 
                        
                        💭 Previsão: {value_pred_automl}
                        {print_jogos}
                        '''
                        if '&' in text:
                            text = text.replace('&', '')

                        id_jogos_mensagem["id_over05HTAutoml"].append({"id": iD, "message_id": sendMenssageTelegram(text)})
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
