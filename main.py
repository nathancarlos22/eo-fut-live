import os
import time
import warnings
import traceback
import requests
import unicodedata
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from rapidfuzz import fuzz
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

warnings.filterwarnings('ignore')


def normalize_text_unicode(text):
    """
    Normalize the input text by removing accents and converting to lowercase.
    """
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text.lower()


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


def calculate_efficiency_attack(df):
    df['shotAccuracy_home'] = df['shotsOngoal_home'] / (df['shots_home'] + 0.01)
    df['shotAccuracy_away'] = df['shotsOngoal_away'] / (df['shots_away'] + 0.01)


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


def load_data():
    """
    Load and preprocess the dataset.
    """
    dataframe = pd.read_csv('src/data_live_engineer_filtered.csv', encoding='utf-8')
    dataframe['league'] = dataframe['league'].apply(normalize_text_unicode)
    dataframe['homeTeam'] = dataframe['homeTeam'].apply(normalize_text_unicode)
    dataframe['awayTeam'] = dataframe['awayTeam'].apply(normalize_text_unicode)
    return dataframe


def load_environment():
    """
    Load environment variables.
    """
    load_dotenv()
    chat_id = os.getenv('CHAT_ID')
    token = os.getenv('TOKEN')
    return chat_id, token


def find_matching_league(league_name, league_list):
    """
    Find the most similar league name from the list.
    """
    league_name = normalize_text_unicode(league_name)
    if league_name in league_list:
        return league_name
    else:
        # Find the league with the highest similarity score
        similar_league = max(league_list, key=lambda x: fuzz.ratio(x, league_name))
        return similar_league


def main():
    # Load data and environment variables
    dataframe = load_data()
    chat_id, token = load_environment()

    # Initialize variables
    id_jogos_mensagem = {"id_over05HTRandomForest": []}
    id_over05HTRandomForest = set()
    winht_RandomForest = 0
    loseht_RandomForest = 0

    # Create a session
    session = requests.Session()

    while True:
        print('🤖 Procurando jogos...\n')
        try:
            # Fetch live data
            url = "https://playscores.sportsat.app/gateway/api/v1/fixtures-svc/v2/fixtures/livescores?include=league,stats,pressureStats&take=3000"
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Origin': 'https://www.playscores.com',
                'Referer': 'https://www.playscores.com/',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
            response = session.get(url, headers=headers)
            response.raise_for_status()
            dic_response = response.json()
            numero_jogos = len(dic_response.get('data', []))
            print(f'🤖 {numero_jogos} jogos ao vivo\n')

            for game in dic_response.get('data', []):
                try:
                    # Extract game data
                    if game['stats'] is None:
                        continue

                    fixture_id = game['stats']['fixtureId']
                    status = game['status']

                    # Skip if game is not live
                    if status != 'LIVE':
                        continue

                    # Extract teams and league information
                    home_team = normalize_text_unicode(game['homeTeam']['name'])
                    away_team = normalize_text_unicode(game['awayTeam']['name'])
                    league_name = f"{game['league']['countryName']} - {game['league']['name']}"
                    league_name = normalize_text_unicode(league_name)

                    # Match league name
                    league_list = dataframe['league'].unique()
                    league = find_matching_league(league_name, league_list)
                    dataframe_league = dataframe[dataframe['league'] == league]
                    if dataframe_league.empty:
                        print(f"No data for league: {league}")
                        continue

                    # Extract match statistics
                    minute = game['currentTime'].get('minute', 0) or 0
                    second = game['currentTime'].get('second', 0) or 0
                    minute = float(f"{minute}.{second}")

                    stats = game['stats']
                    novo_dado = {
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'goal_home': stats['goals']['home'],
                        'goal_away': stats['goals']['away'],
                        'minute': minute,
                        'league': league,
                        'corners_home': stats['corners']['home'],
                        'corners_away': stats['corners']['away'],
                        'possessiontime_home': stats['possessiontime']['home'],
                        'possessiontime_away': stats['possessiontime']['away'],
                        'redcards_home': stats['redcards']['home'],
                        'redcards_away': stats['redcards']['away'],
                        'shotsOngoal_home': stats['shotsOngoal']['home'],
                        'shotsOngoal_away': stats['shotsOngoal']['away'],
                        'shotsOffgoal_home': stats['shotsOffgoal']['home'],
                        'shotsOffgoal_away': stats['shotsOffgoal']['away'],
                        'yellowcards_home': stats['yellowcards']['home'],
                        'yellowcards_away': stats['yellowcards']['away'],
                        'fouls_home': stats['fouls']['home'],
                        'fouls_away': stats['fouls']['away'],
                        'offsides_home': stats['offsides']['home'],
                        'offsides_away': stats['offsides']['away'],
                        'tackles_home': stats['tackles']['home'],
                        'tackles_away': stats['tackles']['away'],
                        'blockedShots_home': stats['shotsBlocked']['home'],
                        'blockedShots_away': stats['shotsBlocked']['away'],
                    }

                    Xht = pd.DataFrame(novo_dado, index=[0])
                    Xht['shots_home'] = Xht['shotsOngoal_home'] + Xht['shotsOffgoal_home']
                    Xht['shots_away'] = Xht['shotsOngoal_away'] + Xht['shotsOffgoal_away']

                    if minute > 1 and minute < 45:
                        # Calculate additional features
                        calculate_efficiency_attack(Xht)
                        calculate_defense_performance(Xht)
                        calculate_passing_performance(Xht)
                        calculate_cards(Xht)

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

                        # Prepare data for prediction
                        X = dataframe_league.drop(['result', 'league', 'match_result', 'match_id', 'homeTeam', 'awayTeam'], axis=1)

                        y = dataframe_league['result']

                        # Oversampling to handle imbalance
                        smote = SMOTE(random_state=42)
                        X_resampled, y_resampled = smote.fit_resample(X, y)

                        # Normalize features
                        scaler = StandardScaler()
                        X_resampled = scaler.fit_transform(X_resampled)
                        Xht_model = scaler.transform(Xht[X.columns])

                        # Train the model
                        model = RandomForestClassifier(random_state=42)
                        model.fit(X_resampled, y_resampled)

                        # Make prediction
                        prediction = model.predict(Xht_model)[0]
                        print(f'{home_team} x {away_team} - {minute} - {game["status"]} - {stats["goals"]["home"] } x {stats["goals"]["away"]} ({league})')

                        # Conditions for sending messages
                        total_goals = stats['goals']['home'] + stats['goals']['away']
                        if total_goals == 0 and prediction >= 0.52 and fixture_id not in id_over05HTRandomForest:
                            id_over05HTRandomForest.add(fixture_id)
                            message = f'''
👑 Modelo RandomForest 

💭 Previsão: {prediction}
🚨 Jogo: {home_team} x {away_team}
⚔️ Placar: {stats['goals']['home']} x {stats['goals']['away']}
🏆 Liga: {league}
⏱️ Minuto: {minute}
'''
                            message_id = send_message_telegram(token, chat_id, message)
                            id_jogos_mensagem["id_over05HTRandomForest"].append({
                                "id": fixture_id,
                                "message_id": message_id
                            })

                        # Update messages
                        for jogo in id_jogos_mensagem["id_over05HTRandomForest"]:
                            if jogo['id'] == fixture_id:
                                if total_goals > 0:
                                    winht_RandomForest += 1
                                    message = f'''
👑 Modelo RandomForest

✅ Win {winht_RandomForest} - {loseht_RandomForest}
🚨 Jogo: {home_team} x {away_team}
⚔️ Placar: {stats['goals']['home']} x {stats['goals']['away']}
🏆 Liga: {league}
⏱️ Minuto: {minute}
'''
                                    send_message_telegram(token, chat_id, message)
                                    id_over05HTRandomForest.remove(fixture_id)
                                    id_jogos_mensagem["id_over05HTRandomForest"].remove(jogo)
                                elif minute > 45 and total_goals == 0:
                                    loseht_RandomForest += 1
                                    message = f'''
👑 Modelo RandomForest

🛑 Lose {winht_RandomForest} - {loseht_RandomForest}
🚨 Jogo: {home_team} x {away_team}
⚔️ Placar: {stats['goals']['home']} x {stats['goals']['away']}
🏆 Liga: {league}
⏱️ Minuto: {minute}
'''
                                    send_message_telegram(token, chat_id, message)
                                    id_over05HTRandomForest.remove(fixture_id)
                                    id_jogos_mensagem["id_over05HTRandomForest"].remove(jogo)
                    else:
                        continue
                except Exception as e:
                    print(f"Error processing game: {e}")
                    traceback.print_exc()
                    continue
            time.sleep(60)
        except Exception as e:
            print(f"Error fetching live data: {e}")
            traceback.print_exc()
            time.sleep(60)
            continue


if __name__ == "__main__":
    main()
