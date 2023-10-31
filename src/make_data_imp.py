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

# def append_to_list(thread_safe_list, lock, df):
#     with lock:
#         thread_safe_list.append(df)


# def main_function(date_str, thread_safe_list, lock, df):
def main_function(date_str, df):
    dfs = []

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        time.sleep(1)


        print(f'Verificando jogos da data: {date_str}')

        # Acessa o site
        driver.get(
            f'https://optaplayerstats.statsperform.com/en_GB/soccer?date={date_str}')
        time.sleep(10)

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
        print(e)
        # main_function(date_str, thread_safe_list, lock, df)
        pass

    
    for league in dict_league_links:
        print("Existem " + str(len(dict_league_links[league])) + " jogos para a liga " + league)
        df_game = []
        for links in dict_league_links[league]:
            try:
                flag = 0

                driver.get(links)
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
                for value in range(30, end_value+1, 5):
                    # Localiza o elemento e altera seu valor de transform
                    dragger = driver.find_element(
                        By.CSS_SELECTOR, '.Opta-Dragger.Opta-Dragger-end')

                    driver.execute_script(
                        f"arguments[0].setAttribute('transform', 'translate({value}, 45)')", dragger)
                    actions.click_and_hold(dragger).move_by_offset(
                        4, 0).release().perform()

                    team_tabs_xpaths = [
                        '//*[@id="Opta_2"]/div/div/div[1]/div/ul/li[2]/a',
                        '/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/div/div/div[1]/div/ul/li[3]/a'
                    ]

                    all_dataframes = {}

                    for idx, team_tab_xpath in enumerate(team_tabs_xpaths):
                        # Clique na aba do time
                        driver.find_element(By.XPATH, team_tab_xpath).click()

                        time.sleep(1)  # Espere a página atualizar

                        # Capture o código fonte da página
                        page_source = driver.page_source

                        # Use o pandas para encontrar todos os dataframes no código fonte
                        dataframes = pd.read_html(page_source)

                        # Adicione os dataframes encontrados ao dicionário geral, usando o índice como chave
                        all_dataframes[f'Team_{idx + 1}'] = dataframes

                    script = """
                    return document.querySelector('g.Opta-TimeBox.Opta-end text').textContent;
                    """
                    minute = driver.execute_script(script)

                    # Pegar a linha 'Total' de cada time
                    team1_stats = all_dataframes['Team_1'][2]
                    team2_stats = all_dataframes['Team_2'][3]

                    # Estruturando o dataframe final
                    final_df = pd.DataFrame({
                        'date': [date_str],
                        'minute': [minute],
                        'match_id': [match_id],
                        'homeTeam': [home_team],
                        'awayTeam': [away_team],
                        'league': [league],
                        'corners_home': team1_stats['Crn'].iloc[-1],
                        'corners_away': team2_stats['Crn'].iloc[-1],
                        'redcards_home': team1_stats['RC'].iloc[-1],
                        'redcards_away': team2_stats['RC'].iloc[-1],
                        'shotsOffgoal_home': team1_stats['S'].iloc[-1] - team1_stats['SOnT'].iloc[-1],
                        'shotsOffgoal_away': team2_stats['S'].iloc[-1] - team2_stats['SOnT'].iloc[-1],
                        'shotsOngoal_home': team1_stats['SOnT'].iloc[-1],
                        'shotsOngoal_away': team2_stats['SOnT'].iloc[-1],
                        'yellowcards_home': team1_stats['YC'].iloc[-1],
                        'yellowcards_away': team2_stats['YC'].iloc[-1],
                        'passes_home': team1_stats['P'].iloc[-1],
                        'passes_away': team2_stats['P'].iloc[-1],
                        'fouls_c_home': team1_stats['FC'].iloc[-1],
                        'fouls_c_away': team2_stats['FC'].iloc[-1],
                        'fouls_won_home': team1_stats['FW'].iloc[-1],
                        'fouls_won_away': team2_stats['FW'].iloc[-1],
                        'offsides_home': team1_stats['O'].iloc[-1],
                        'offsides_away': team2_stats['O'].iloc[-1],
                        'tackles_home': team1_stats['Tk'].iloc[-1],
                        'tackles_away': team2_stats['Tk'].iloc[-1],

                        'result': 0
                    })

                    # Condição de parada: gol = 1 para qualquer um dos times
                    goal_condition_team1 = team1_stats['G'].iloc[-1]
                    goal_condition_team2 = team2_stats['G'].iloc[-1]

                    if goal_condition_team1 == 1 or goal_condition_team2 == 1:
                        flag = 1
                        print('Gol')
                        print('Juntando os dataframes')
                        dfs_combined = pd.concat(df_game, ignore_index=True)

                        # Adicione o valor 1 para os últimos 10 registros
                        
                        if len(dfs_combined) > 10:
                            dfs_combined.loc[dfs_combined.index[-10:],
                                             'result'] = 1
                        else:
                            dfs_combined['result'] = 1

                        dfs.append(dfs_combined)
                        break
                        # append_to_list(thread_safe_list, lock, dfs_combined)
                        # return dfs_combined

                    # dfs.append(final_df)
                    df_game.append(final_df)

                    dfs_combined = pd.concat(df_game, ignore_index=True)
                    # printando date minute homeTeam awayTeam
                    print(final_df[['date', 'minute', 'homeTeam', 'awayTeam']])
                    print('-------------------')
                if flag == 0:
                    print('Sem gol')
                    print('Juntando os dataframes')
                    dfs.append(dfs_combined)
                    break
                    # append_to_list(thread_safe_list, lock,
                                #    pd.concat(dfs, ignore_index=True))
                    # dfs_combined = pd.concat(dfs, ignore_index=True)
                    # return dfs_combined
                
            except Exception as e:
                print(e)
                continue
        
    return pd.concat(dfs, ignore_index=True)
    # append_to_list(thread_safe_list, lock, pd.concat(dfs, ignore_index=True))

