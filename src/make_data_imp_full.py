from io import StringIO
import traceback
import datetime
from concurrent.futures import ThreadPoolExecutor
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

file_path = './data_live_scores_full.csv'

def main_function_full(date_str):

    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        options = webdriver.ChromeOptions()
        driver = webdriver.Remote(command_executor='http://localhost:4444', options=options)

        print(f'Verificando jogos da data: {date_str}')

        # Acessa o site
        driver.get(
            f'https://optaplayerstats.statsperform.com/en_GB/soccer?date={date_str}')
        driver.maximize_window()

        # Espera a página carregar
        WebDriverWait(driver, 30).until(lambda d: d.execute_script(
            'return document.readyState') == 'complete')
        
        close_icon = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
        )
        close_icon.click()
        # Obtém o conteúdo da página
        page_content = driver.page_source
        # Analisa o conteúdo com BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')

        # Encontrar todos os blocos de competição
        competitions = soup.find_all(
            'div', class_='livescore-container-fixtures-competition')
        dict_league_links = {}

        for comp in competitions:
            # Dentro de cada bloco de competição, obter o nome da liga
            league_name = comp.find(
                'span', class_='competitionName').get_text(strip=True)

            # Obter todos os links relacionados a essa liga
            links = comp.find_all('a', href=True)
            for link in links:
                if 'match' in link['href']:
                    if league_name not in dict_league_links:
                        dict_league_links[league_name] = []
                        dict_league_links[league_name].append(
                            'https://optaplayerstats.statsperform.com' + link['href'])
                    else:
                        dict_league_links[league_name].append(
                            'https://optaplayerstats.statsperform.com' + link['href'])
    except Exception as e:
        print(f'Erro na data: {date_str}')
        print(e)
        pass

    colunas_ordenadas =  ['date', 'minute', 'homeTeam', 'awayTeam', 'goalHome', 'goalAway',
                           'shotsHome', 'shotsAway', 'crossesHome', 'crossesAway','assistsHome', 'assistsAway', 
                           'blockedShotsHome', 'blockedShotsAway', 'league', 'corners_home',
                            'corners_away', 'redcards_home', 'redcards_away', 'shotsOffgoal_home',
                            'shotsOffgoal_away', 'shotsOngoal_home', 'shotsOngoal_away',
                            'yellowcards_home', 'yellowcards_away', 'passes_home', 'passes_away',
                            'fouls_c_home', 'fouls_c_away', 'fouls_won_home', 'fouls_won_away',
                            'offsides_home', 'offsides_away', 'tackles_home', 'tackles_away',
                            'result', 'match_id']
    
    for league in dict_league_links:
        print("Existem " + str(len(dict_league_links[league])) + " jogos para a liga " + league)
        for links in dict_league_links[league]:
            try:
                driver.get(links)
                driver.minimize_window()
                driver.maximize_window()
                

                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'button[data-period_idx="1"].Opta-Stdperiod'))
                )

                home_team = driver.find_element(
                    By.XPATH, '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[2]/a').text
                away_team = driver.find_element(
                    By.XPATH, '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[3]').text
                match_id = date_str + '-' + home_team + '-' + away_team

                print('Verificando se o jogo já existe no dataframe')

                if match_id in df['match_id'].unique():
                    print('Jogo já existe no dataframe')
                    continue
                
                print('Jogo não existe no dataframe')
                print('Iniciando a coleta de dados')
                print('-------------------')

                # Clica no botão "First half"
                # button.click()

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

                dragger = driver.find_element(
                        By.CSS_SELECTOR, '.Opta-Dragger.Opta-Dragger-end')

                dragger_location = dragger.location
                start_x = dragger_location['x']
                start_y = dragger_location['y']

                for value in range(0, start_x, 5):
                    all_dataframes = {}
                    # Localiza o elemento e altera seu valor de transform
                    dragger = driver.find_element(
                        By.CSS_SELECTOR, '.Opta-Dragger.Opta-Dragger-end')

                    # Obter a posição atual do dragger
                    dragger_location = dragger.location
                    start_x = dragger_location['x']
                    start_y = dragger_location['y']

                    # Calcular a nova posição X
                    new_x = start_x - 5  # Ajuste este valor conforme necessário
                    new_y = start_y  # Mantendo a posição Y constante

                    # Criar e executar o script para simular o movimento do mouse
                    script = f"""
                        var dragger = document.querySelector('#Opta_2 > div > div > div.Opta-timecontrols > div > div.Opta-Timestrip > svg > g.Opta-Dragger.Opta-Dragger-end');
                        var startX = {start_x};
                        var startY = {start_y};
                        var endX = {new_x};
                        var endY = {new_y};

                        // Criar e disparar o evento mousedown
                        var mouseDownEvent = new MouseEvent('mousedown', {{
                            clientX: startX,
                            clientY: startY,
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        dragger.dispatchEvent(mouseDownEvent);

                        // Criar e disparar o evento mousemove
                        var mouseMoveEvent = new MouseEvent('mousemove', {{
                            clientX: endX,
                            clientY: endY,
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        dragger.dispatchEvent(mouseMoveEvent);

                        // Criar e disparar o evento mouseup
                        var mouseUpEvent = new MouseEvent('mouseup', {{
                            clientX: endX,
                            clientY: endY,
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        dragger.dispatchEvent(mouseUpEvent);
                    """
                    driver.execute_script(script)
                    
                    
                    page_source = driver.page_source

                    dataframes = pd.read_html(StringIO(page_source))

                    all_dataframes[f'Team_1'] = dataframes

                    script = """
                    return document.querySelector('g.Opta-TimeBox.Opta-end text').textContent;
                    """
                    
                    if driver.execute_script(script) == '0:00':
                        break

                    minute.append(driver.execute_script(script))

                    team1_stats = all_dataframes['Team_1'][2]
                    team2_stats = all_dataframes['Team_1'][3]

                    date.append(date_str)
                    match_id_list.append(match_id)
                    homeTeam.append(home_team)
                    awayTeam.append(away_team)
                    liga.append(league)
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
                    print('-------------------')

                    print(f'{date_str} - {home_team} x {away_team} - {minute[-1]} minutos')
                    
                print('Finalizando o jogo')

                final_df = pd.DataFrame({
                    'date': date,
                    'minute': minute,
                    'match_id': match_id_list,
                    'homeTeam': homeTeam,
                    'awayTeam': awayTeam,
                    'goalHome': goalHome,
                    'goalAway': goalAway,
                    'shotsHome': shotsHome,
                    'shotsAway': shotsAway,
                    'crossesHome': crossesHome,
                    'crossesAway': crossesAway,
                    'assistsHome': assistsHome,
                    'assistsAway': assistsAway,
                    'blockedShotsHome': blockedShotsHome,
                    'blockedShotsAway': blockedShotsAway,
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
                    'fouls_won_home': fouls_won_home,
                    'fouls_won_away': fouls_won_away,
                    'offsides_home': offsides_home,
                    'offsides_away': offsides_away,
                    'tackles_home': tackles_home,
                    'tackles_away': tackles_away,

                })


                final_df['result'] = 0
                
                # reordenar as colunas do DataFrame
                final_df = final_df[colunas_ordenadas]
                
                # Abrir o arquivo em modo de anexação
                print('Salvando o dataframe')
                with open('data_live_scores_full.csv', 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    # Iterar sobre as linhas do DataFrame
                    for index, row in final_df.iterrows():
                        # Converter a linha em uma lista e escrevê-la no arquivo
                        writer.writerow(row.tolist())
                    
                
            # traceback
            except Exception as e:
                print(f'Erro no jogo: {home_team} x {away_team}')
                traceback.print_exc()

                print(e)
                continue
    print('Finalizando o driver')
    driver.quit()

