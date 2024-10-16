import requests
import re
from io import StringIO
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import unicodedata
import time
import os
import warnings
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Configurações do WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

# Função para capturar e processar os jogos da página
def fetch_games(url):
    driver.get(url)
    time.sleep(10)
    print(f"URL: {url}")
    # driver.maximize_window()

    # Espera a página carregar
    WebDriverWait(driver, 30).until(lambda d: d.execute_script(
        'return document.readyState') == 'complete')

    # close_icon = WebDriverWait(driver, 30).until(
    #     EC.element_to_be_clickable(
    #         (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
    # )
    # close_icon.click()

    time.sleep(10)

    # Agora capturando o conteúdo da página
    page_source = driver.page_source

    # Analisa o conteúdo com BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    match_containers = soup.find_all(class_='livescores-match-container')

    links = []

    for container in match_containers:
        score_live = container.find('div', class_='score-live')
        match_time = container.find('div', class_='match-time')

        if score_live and match_time:
            link = container['href']
            links.append(link)

    get_links = []
    for link in links:
        get_links.append(f'https://optaplayerstats.statsperform.com{link}')
    
    return get_links

def get_league_info(html):
    # soup = BeautifulSoup(html, 'html.parser')

    liga_element = html.find("span", class_="name")
    pais = None
    

    if liga_element:
        pais = html.find("span", class_="flag").find("img")["alt"]
        league = f'{pais} - {liga_element.text}'
    
    else:
        liga_element = html.find('h2', title=True)['title']
        pais = html.find("span", class_="flag").find("img")["alt"]
        league = f'{pais} - {liga_element}'

    return league

# Função para extrair estatísticas de uma partida
def extract_match_stats(match_url):
    driver.get(match_url)
    # Espera a página carregar
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="Opta_2"]/div/div/div[2]/div/div[2]/button[1]'))
    )
    time.sleep(10)

    # Agora capturando o conteúdo da página
    page_source = driver.page_source

    # Analisa o conteúdo com BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Encontre o elemento que contém a liga
    league = get_league_info(soup)

    dataframes = pd.read_html(StringIO(page_source))

    team1_stats = dataframes[2]
    team2_stats = dataframes[3]

    # Get the current date
    current_date = datetime.today()

    # Format the date as YYYY-MM-DD
    date_str = current_date.strftime('%Y-%m-%d')

    date = []
    minute = []
    match_id_list = []
    homeTeam = []
    awayTeam = []
    goalHome = []
    goalAway = []
    shotsHome = []
    shotsAway = []
    crossesHome = []
    crossesAway = []
    assistsHome = []
    assistsAway = []
    blockedShotsHome = []
    blockedShotsAway = []
    liga = []
    corners_home = []
    corners_away = []
    redcards_home = []
    redcards_away = []
    shotsOffgoal_home = []
    shotsOffgoal_away = []
    shotsOngoal_home = []
    shotsOngoal_away = []
    yellowcards_home = []
    yellowcards_away = []
    passes_home = []
    passes_away = []
    fouls_c_home = []
    fouls_c_away = []
    fouls_won_home = []
    fouls_won_away = []
    offsides_home = []
    offsides_away = []
    tackles_home = []
    tackles_away = []

    script = """
    return document.querySelector('g.Opta-TimeBox.Opta-end text').textContent;
    """

    

    home_team = driver.find_element(
        By.XPATH, '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[2]/a').text
    away_team = driver.find_element(
        By.XPATH, '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[3]').text
    match_id = date_str + '-' + home_team + '-' + away_team

    minute.append(driver.execute_script(script))

    date.append(date_str)
    match_id_list.append(match_id)
    homeTeam.append(home_team)
    awayTeam.append(away_team)
    liga.append(league)
    try:
        goalHome.append(team1_stats['G'].iloc[-1])
        goalAway.append(team2_stats['G'].iloc[-1])
        shotsHome.append(team1_stats['S'].iloc[-1])
        shotsAway.append(team2_stats['S'].iloc[-1])
        crossesHome.append(team1_stats['Crn'].iloc[-1])
        crossesAway.append(team2_stats['Crn'].iloc[-1])
        assistsHome.append(team1_stats['A'].iloc[-1])
        assistsAway.append(team2_stats['A'].iloc[-1])
        blockedShotsHome.append(team1_stats['BS'].iloc[-1])
        blockedShotsAway.append(team2_stats['BS'].iloc[-1])

        corners_home.append(team1_stats['Crn'].iloc[-1])
        redcards_home.append(team1_stats['RC'].iloc[-1])
        shotsOffgoal_home.append(team1_stats['S'].iloc[-1] - team1_stats['SOnT'].iloc[-1])
        shotsOngoal_home.append(team1_stats['SOnT'].iloc[-1])
        yellowcards_home.append(team1_stats['YC'].iloc[-1])
        passes_home.append(team1_stats['P'].iloc[-1])
        fouls_c_home.append(team1_stats['FC'].iloc[-1])
        fouls_won_home.append(team1_stats['FW'].iloc[-1])
        offsides_home.append(team1_stats['O'].iloc[-1])
        tackles_home.append(team1_stats['Tk'].iloc[-1])

        corners_away.append(team2_stats['Crn'].iloc[-1])
        redcards_away.append(team2_stats['RC'].iloc[-1])
        shotsOffgoal_away.append(team2_stats['S'].iloc[-1] - team2_stats['SOnT'].iloc[-1])
        shotsOngoal_away.append(team2_stats['SOnT'].iloc[-1])
        yellowcards_away.append(team2_stats['YC'].iloc[-1])
        passes_away.append(team2_stats['P'].iloc[-1])
        fouls_c_away.append(team2_stats['FC'].iloc[-1])
        fouls_won_away.append(team2_stats['FW'].iloc[-1])
        offsides_away.append(team2_stats['O'].iloc[-1])
        tackles_away.append(team2_stats['Tk'].iloc[-1])
    
    except:
        return None

    return {
    'minute': minute,
    'homeTeam': homeTeam,
    'awayTeam': awayTeam,
    'goal_home': goalHome,
    'goal_away': goalAway,
    'shots_home': shotsHome,
    'shots_away': shotsAway,
    'crossesHome': crossesHome,
    'crossesAway': crossesAway,
    'assistsHome': assistsHome,
    'assistsAway': assistsAway,
    'blockedShots_home': blockedShotsHome,
    'blockedShots_away': blockedShotsAway,
    'league': liga,
    'corners_home': corners_home,
    'corners_away': corners_away,
    'redcards_home': redcards_home,
    'redcards_away': redcards_away,
    'shotsOffgoal_home': shotsOffgoal_home,
    'shotsOffgoal_away': shotsOffgoal_away,
    'shotsOngoal_home': shotsOngoal_home,
    'shotsOngoal_away': shotsOngoal_away,
    'yellowcards_home': yellowcards_home,
    'yellowcards_away': yellowcards_away,
    'passes_home': passes_home,
    'passes_away': passes_away,
    'fouls_c_home': fouls_c_home,
    'fouls_c_away': fouls_c_away,
    'fouls_home': fouls_won_home,
    'fouls_away': fouls_won_away,
    'offsides_home': offsides_home,
    'offsides_away': offsides_away,
    'tackles_home': tackles_home,
    'tackles_away': tackles_away,
    'match_id': match_id  # Adicionei o match_id aqui
}

# Função para normalizar texto unicode
def normalize_text_unicode(text):
    """
    Normalize the input text by removing accents and converting to lowercase.
    """
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text.lower()

# Função para carregar e preparar o dataset
def load_data():
    dataframe = pd.read_csv('src\data_live_engineer_filtered.csv', encoding='utf-8')
    dataframe['league'] = dataframe['league'].apply(normalize_text_unicode)
    return dataframe

# Função para realizar previsões com modelo de RandomForest
def predict_game(Xht, dataframe_league):

    # Preparar dados para previsão
    X = dataframe_league.drop(['result', 'league', 'match_result', 'match_id', 'homeTeam', 'awayTeam'], axis=1)
    y = dataframe_league['result']
    scaler = StandardScaler()
    X_resampled = scaler.fit_transform(X)
    Xht_model = scaler.transform(Xht[X.columns])

    model = RandomForestClassifier(random_state=42)
    model.fit(X_resampled, y)

    prediction = model.predict(Xht_model)[0]
    return prediction

def calculate_efficiency_attack(df):
    df['shotAccuracy_home'] = df['shotsOngoal_home'] / (df['shots_home'] + 0.01)
    df['shotAccuracy_away'] = df['shotsOngoal_away'] / (df['shots_away'] + 0.01)

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



def calculate_defense_performance(df):
    df['attackPressureOverTime_home'] = (df['shots_home'] + df['corners_home']) / df['minute']
    df['attackPressureOverTime_away'] = (df['shots_away'] + df['corners_away']) / df['minute']

    # Use the misspelled column names to match your dataset
    df['aggrressionOverTime_home'] = (
        df['redcards_home'] + df['yellowcards_home'] + df['fouls_home']
    ) / df['minute']
    df['aggresssionOverTime_away'] = (
        df['redcards_away'] + df['yellowcards_away'] + df['fouls_away']
    ) / df['minute']

    df['defensiveEfficacy_home'] = df['blockedShots_home'] / (df['shotsOngoal_home'] + 0.01)
    df['defensiveEfficacy_away'] = df['blockedShots_away'] / (df['shotsOngoal_away'] + 0.01)

    # Use the misspelled column names to match your dataset
    df['taklesOverTime_home'] = df['tackles_home'] / df['minute']
    df['taklesOverTime_away'] = df['tackles_away'] / df['minute']


def calculate_passing_performance(df):
    df['possessionControl'] = abs(df['possessiontime_home'] - df['possessiontime_away'])
    df['passRisk_home'] = df['offsides_home'] / (df['possessiontime_home'] + 0.01)
    df['passRisk_away'] = df['offsides_away'] / (df['possessiontime_away'] + 0.01)


def calculate_cards(df):
    df['TotalCards_home'] = df['redcards_home'] + df['yellowcards_home']
    df['TotalCards_away'] = df['redcards_away'] + df['yellowcards_away']

def calculate_possession(df):
    total_passes = df['passes_away'] + df['passes_home']
    df['possessiontime_away'] = round((df['passes_away'] / total_passes) * 100)
    df['possessiontime_home'] = round((df['passes_home'] / total_passes) * 100)

    df['possessiontime_home'].fillna(method='bfill', inplace=True)
    df['possessiontime_away'].fillna(method='bfill', inplace=True)

def calculate_shots(df):
    df['shots_home'] = df['shotsOngoal_home'] + df['shotsOffgoal_home']
    df['shots_away'] = df['shotsOngoal_away'] + df['shotsOffgoal_away']

def send_message_telegram(token, chat_id, message):
    """
    Send a message via Telegram bot.
    """
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {'chat_id': chat_id, 'text': message}
        response = requests.get(url, params=payload)
        response.raise_for_status()
        result = response.json().get('result', {})
        message_id = result.get('message_id')
        print(message)
        return message_id
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


def edit_message_telegram(token, chat_id, message_id, new_message):
    """
    Edit a previously sent message via Telegram bot.
    """
    try:
        url = f'https://api.telegram.org/bot{token}/editMessageText'
        payload = {'chat_id': chat_id, 'message_id': message_id, 'text': new_message}
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error editing message: {e}")


def load_environment():
    """
    Load environment variables.
    """
    load_dotenv()
    chat_id = os.getenv('CHAT_ID')
    token = os.getenv('TOKEN')
    return chat_id, token

dataframe = load_data()
chat_id, token = load_environment()

# Inicialização das variáveis globais
id_over05HTRandomForest = set()
id_jogos_mensagem = {"id_over05HTRandomForest": []}
winht_RandomForest = 0
loseht_RandomForest = 0

# Aplicação geral
def run_code():
    global id_over05HTRandomForest, id_jogos_mensagem, winht_RandomForest, loseht_RandomForest
    url = 'https://optaplayerstats.statsperform.com/en_GB/soccer'

    # Coletar informações dos jogos
    jogos_links = fetch_games(url)
    print(jogos_links)

    if jogos_links == []:
        print("Não há jogos ao vivo")

    else:
        current_matches = {}
    
        for match in jogos_links:

            match_stats = extract_match_stats(match)
            if match_stats == None:
                print("Erro ao pegar dados da tabela de jogo")
                continue
            
            Xht = pd.DataFrame(match_stats)
            
            print(Xht)

            # Aplicando a função na coluna 'minute'
            Xht['minute_decimal'] = Xht['minute'].apply(convert_to_decimal)

            # Removendo os minutos iguais a 0
            Xht = Xht[Xht['minute_decimal'] != 0]
            Xht['minute'] = Xht['minute_decimal']
            Xht.drop(columns=['minute_decimal'], inplace=True)

            calculate_efficiency_attack(Xht)
            calculate_defense_performance(Xht)
            calculate_possession(Xht)
            calculate_passing_performance(Xht)
            calculate_cards(Xht)

            Xht.drop(columns=['fouls_c_home', 'fouls_c_away', 'passes_home', 'passes_away', 'assistsHome', 'assistsAway'], inplace=True)

            # Processar previsões
            league = normalize_text_unicode(str(Xht['league'].values[0]))
            Xht['league'] = league  # Atualiza o valor normalizado
            if league not in dataframe['league'].unique():
                print(f"liga {league} não está no dataframe")
                continue

            dataframe_league = dataframe[dataframe['league'] == league]

            # Merge historical data
            gols_columns = [
                'win_rate_home', 'draw_rate_home', 'loss_rate_home',
                'win_rate_away', 'draw_rate_away', 'loss_rate_away', 'f_attack_home',
                'f_attack_away', 'f_defensive_home', 'f_defensive_away', '05ht_home',
                '15ht_home', '25ht_home', '05ht_away', '15ht_away', '25ht_away'
            ]
            for col in gols_columns:
                if col in dataframe_league.columns:
                    Xht[col] = dataframe_league.iloc[-1][col]
                else:
                    Xht[col] = 0

            Xht.fillna(0, inplace=True)
            
            prediction = predict_game(Xht, dataframe_league)
            print(f"Previsão: {prediction}")

            # Extraindo informações necessárias
            match_id = Xht['match_id'].iloc[0]
            home_team = Xht['homeTeam'].iloc[0]
            away_team = Xht['awayTeam'].iloc[0]
            minute = Xht['minute'].iloc[0]
            goal_home = Xht['goal_home'].iloc[0]
            goal_away = Xht['goal_away'].iloc[0]
            total_goals = goal_home + goal_away

            # Verificando condições para envio de mensagem
            if total_goals == 0 and prediction >= 0.52 and match_id not in id_over05HTRandomForest and minute < 45:
                id_over05HTRandomForest.add(match_id)
                message = f'''
👑 Modelo RandomForest 

💭 Previsão: {prediction}
🚨 Jogo: {home_team} x {away_team}
⚔️ Placar: {goal_home} x {goal_away}
🏆 Liga: {Xht['league'].iloc[0]}
⏱️ Minuto: {minute}
'''
                message_id = send_message_telegram(token, chat_id, message)
                id_jogos_mensagem["id_over05HTRandomForest"].append({
                    "id": match_id,
                    "message_id": message_id,
                    "url": match
                })

            # Armazenando dados atuais do jogo
            current_matches[match_id] = Xht

        # Verificando atualizações nos jogos em andamento
        for jogo in id_jogos_mensagem["id_over05HTRandomForest"][:]:
            match_id = jogo['id']
            message_id = jogo['message_id']
            match_url = jogo['url']

            # Re-extract match stats
            try:
                Xht = pd.DataFrame(extract_match_stats(match_url))
                if Xht.empty:
                    continue

                minute = Xht['minute'].iloc[0]
                minute = convert_to_decimal(minute)
                total_goals = Xht['goal_home'].iloc[0] + Xht['goal_away'].iloc[0]
                home_team = Xht['homeTeam'].iloc[0]
                away_team = Xht['awayTeam'].iloc[0]
                goal_home = Xht['goal_home'].iloc[0]
                goal_away = Xht['goal_away'].iloc[0]
                league = Xht['league'].iloc[0]

                if total_goals > 0:

                    winht_RandomForest +=1
                    message = f'''
👑 Modelo RandomForest

✅ Win {winht_RandomForest} - {loseht_RandomForest}
🚨 Jogo: {home_team} x {away_team}
⚔️ Placar: {goal_home} x {goal_away}
🏆 Liga: {league}
⏱️ Minuto: {minute}
'''
                    send_message_telegram(token, chat_id, message)
                    id_over05HTRandomForest.remove(match_id)
                    id_jogos_mensagem["id_over05HTRandomForest"].remove(jogo)

                elif minute > 45 and total_goals == 0:

                    loseht_RandomForest += 1
                    message = f'''
👑 Modelo RandomForest

🛑 Lose {winht_RandomForest} - {loseht_RandomForest}
🚨 Jogo: {home_team} x {away_team}
⚔️ Placar: {goal_home} x {goal_away}
🏆 Liga: {league}
⏱️ Minuto: {minute}
'''
                    send_message_telegram(token, chat_id, message)
                    id_over05HTRandomForest.remove(match_id)
                    id_jogos_mensagem["id_over05HTRandomForest"].remove(jogo)

            except Exception as e:
                print(f"Error updating match {match_id}: {e}")
                continue

while True:
    try:
        run_code()
        time.sleep(60)  # Pausa por 60 segundos (1 minuto)
    except:
        continue
