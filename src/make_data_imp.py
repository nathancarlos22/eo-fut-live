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
import re

file_path = './data_live_scores.csv'

def main_function(date_str):

    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        # service = Service(ChromeDriverManager().install())
        # driver = webdriver.Chrome(service=service)
        options = webdriver.ChromeOptions()
        driver = webdriver.Remote(command_executor='http://localhost:4444', options=options)
        # time.sleep(1)


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

    colunas_ordenadas =  ['date', 'minute', 'homeTeam', 'awayTeam', 'league', 'corners_home',
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
                
                # Espera a página carregar
                WebDriverWait(driver, 30).until(lambda d: d.execute_script(
                    'return document.readyState') == 'complete')
                button = WebDriverWait(driver, 30).until(
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
                button.click()

                # Recupera o valor do 'transform' após o clique
                dragger = driver.find_element(
                    By.CSS_SELECTOR, '.Opta-Dragger.Opta-Dragger-end')

                transform_value = dragger.get_attribute('transform')

                # Usa regex para extrair o valor numérico de 'translate'
                match = re.search(r'translate\((\d+),', transform_value)
                # Se não encontrar, usa um valor padrão
                end_value = int(match.group(1)) if match else 35

                # Use ActionChains para simular o arrasto
                actions = ActionChains(driver)

                # Exemplo: movendo o dragger 5 pixels à direita
                # Aqui estamos variando de 30 a 35
                # team_tab_xpath1 = '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[2]/a'
                # team_tab_xpath2 = '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[3]/a'
                # driver.find_element(By.XPATH, team_tab_xpath1).click()

                date = []
                minute = []
                match_id_list = []
                homeTeam = []
                awayTeam = []
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
                result = []
                
                for value in range(30, end_value+1, 5):
                    all_dataframes = {}
                    # Localiza o elemento e altera seu valor de transform
                    dragger = driver.find_element(
                        By.CSS_SELECTOR, '.Opta-Dragger.Opta-Dragger-end')

                    driver.execute_script(
                        f"arguments[0].setAttribute('transform', 'translate({value}, 45)')", dragger)
                    actions.click_and_hold(dragger).move_by_offset(
                        4, 0).release().perform()

                    page_source = driver.page_source

                    dataframes = pd.read_html(page_source)

                    all_dataframes[f'Team_1'] = dataframes

                    script = """
                    return document.querySelector('g.Opta-TimeBox.Opta-end text').textContent;
                    """
                    minuto = driver.execute_script(script)

                    
                    numero_extraido = re.findall('(\d+)\+', minuto)
                    numero_int = int(numero_extraido[0]) if numero_extraido else 0

                    # Convertendo para inteiro

                    # se houver algum erro na extração do minuto, altera o dragger para obter o valor correto
                    while numero_int > 45:
                        driver.execute_script(
                        f"arguments[0].setAttribute('transform', 'translate({value}, 45)')", dragger)
                        actions.click_and_hold(dragger).move_by_offset(
                        4, 0).release().perform()

                        page_source = driver.page_source

                        dataframes = pd.read_html(page_source)

                        all_dataframes[f'Team_1'] = dataframes

                        script = """
                        return document.querySelector('g.Opta-TimeBox.Opta-end text').textContent;
                        """
                        minuto = driver.execute_script(script)
                        numero_extraido = re.findall('(\d+)\+', minuto)
                        numero_int = int(numero_extraido[0]) if numero_extraido else 0
                        
                    
                    minute.append(minuto)

                    team1_stats = all_dataframes['Team_1'][2]
                    team2_stats = all_dataframes['Team_1'][3]

                    date.append(date_str)
                    match_id_list.append(match_id)
                    homeTeam.append(home_team)
                    liga.append(league)

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

                    awayTeam.append(away_team)
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

                    result.append(0)

                    goal_condition_team1 = team1_stats['G'].iloc[-1]
                    goal_condition_team2 = team2_stats['G'].iloc[-1]

                    if goal_condition_team1 == 1 or goal_condition_team2 == 1:
                        print('Gol')
                        # Adicione o valor 1 para os últimos 10 registros
                        if len(result) > 10:
                            result[-10:] = [1] * 10
                        else:
                            result = [1] * len(result)

                        break
                    print('-------------------')
                    print(f'{date_str} - {home_team} x {away_team} - {minute[-1]} minutos')
                    
                print('Finalizando o jogo')

                final_df = pd.DataFrame({
                    'date': date,
                    'minute': minute,
                    'match_id': match_id_list,
                    'homeTeam': homeTeam,
                    'awayTeam': awayTeam,
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

                    'result': result
                })
                
                # reordenar as colunas do DataFrame
                final_df = final_df[colunas_ordenadas]
                # Abrir o arquivo em modo de anexação
                print('Salvando o dataframe')
                with open('data_live_scores.csv', 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    # Iterar sobre as linhas do DataFrame
                    for index, row in final_df.iterrows():
                        # Converter a linha em uma lista e escrevê-la no arquivo
                        writer.writerow(row.tolist())
                    
                
                
            except Exception as e:
                print(f'Erro na data: {date_str}')
                print(e)
                continue
    print('Finalizando o driver')
    driver.quit()

