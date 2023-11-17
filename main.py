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
import betfairlightweight
import configparser
import h2o
# from h2o.automl import H2Oautoml
from dotenv import load_dotenv
import os
from datetime import datetime



warnings.filterwarnings('ignore')

# hora = datetime.now().hour


load_dotenv()

chat_id = os.getenv('CHAT_ID')
token = os.getenv('TOKEN')


def sendMenssageTelegram(message):
    url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    results = requests.get(url_base)
    print(results)
    print(message)


id_over05HTmodel = []
winht_model = 0
loseht_model = 0

# id_over05HTrandomforest = []
# winht_randomforest = 0
# loseht_randomforest = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

text = ' '

# intervalo_horas = 10
# intervalo_segundos = intervalo_horas * 60 * 60
# tempo_atual = time.time()
# tempo_termino = tempo_atual + intervalo_segundos
resultados = {}

minutoss = datetime.now().minute
flag = 0

model = keras.models.load_model('models/model_redeht.h5')
# model_Automl = keras.models.load_model('model_Automl.h5')
# Inicializar o cluster H2O
h2o.init()
model_Automl = loaded_model = h2o.load_model("C:/Users/Pichau/Desktop/eofut/models/model_automl")
# model_randomforest = pickle.load(
#     open('models/random_forestht.pkl', 'rb'))

id_over05HTmodel = []
winht_model = 0
loseht_model = 0

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

# tempo_termino = tempo_atual + intervalo_segundos

id_evento = ''

lucro = 0
valorEsperado = 0
state = ''
while True:

    # hora = datetime.now().hour
    print('🤖 Procurando jogos...\n')

    # tempo_atual = time.time()
    # if tempo_atual >= tempo_termino or flag == 0 or hora == 0 and minutoss == 0:
        # flag = 1


        # def makeBet(id_evento):

        # try:
        #     config = configparser.ConfigParser()
        #     config.read('credenciais.ini')

        #     app_key = config['api_credentials']['app_key']
        #     username = config['api_credentials']['username']
        #     password = config['api_credentials']['password']

        #     trading = betfairlightweight.APIClient(username, password, app_key=app_key, cert_files=("./betfair-certs/nc-odds.crt", "./betfair-certs/nc-odds.key"))
        #     trading.login()

        #     filtros_mercado = betfairlightweight.filters.market_filter()

        #     eventos_fut = trading.betting.list_events(filter=filtros_mercado)

        #     competitions = trading.betting.list_competitions(filter=filtros_mercado)

        #     planilha_eventos = pd.DataFrame({
        #         'NomeEvento': [evento.event.name for evento in eventos_fut],
        #         'IdEvento': [evento.event.id for evento in eventos_fut],
        #         'LocalEvento': [evento.event.venue for evento in eventos_fut],
        #         'CodPais': [evento.event.country_code for evento in eventos_fut],
        #         'Timezone': [evento.event.time_zone for evento in eventos_fut],
        #         'DataAbertura': [evento.event.open_date for evento in eventos_fut],
        #         'TotalMercados': [evento.market_count for evento in eventos_fut],
        #         'DataLocal': [evento.event.open_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None) for evento in eventos_fut],

        #     })

        #     planilha_eventos = planilha_eventos[planilha_eventos['NomeEvento'].str.contains(' v ')] # retirando mercados de eventos que não são partidas de futebol
        #     planilha_eventos['IdEvento'] = planilha_eventos['IdEvento'].astype(str)

        #     jogo = planilha_eventos[planilha_eventos['IdEvento'] == id_evento]

        #     filtros_mercado = betfairlightweight.filters.market_filter(event_ids=[id_evento])

        #     catalogos_mercado = trading.betting.list_market_catalogue(
        #         filter=filtros_mercado,
        #         max_results='100',
        #         sort='FIRST_TO_START',
        #         market_projection=['RUNNER_METADATA']
        #     )

        #     mercados = pd.DataFrame({
        #         'NomeMercado': [mercado.market_name for mercado in catalogos_mercado],
        #         'IdMercado': [mercado.market_id for mercado in catalogos_mercado],
        #         'TotalCorrespondido': [mercado.total_matched for mercado in catalogos_mercado],
        #         'Home': [mercado.runners[0].runner_name for mercado in catalogos_mercado],
        #         'HomeId': [mercado.runners[0].selection_id for mercado in catalogos_mercado],
        #         'Away': [mercado.runners[1].runner_name for mercado in catalogos_mercado],
        #         'AwayId': [mercado.runners[1].selection_id for mercado in catalogos_mercado],
        #         'Draw': [mercado.runners[2].runner_name if len(mercado.runners) > 2 else '' for mercado in catalogos_mercado],
        #         'DrawId': [mercado.runners[2].selection_id if len(mercado.runners) > 2 else 0 for mercado in catalogos_mercado],

        #     })

        #     filtro_mercado_id_odds = mercados[(mercados['NomeMercado'] == 'First Half Goals 0.5')]

        #     order_filter = betfairlightweight.filters.ex_best_offers_overrides(
        #         best_prices_depth=3,
        #     )

        #     price_filter = betfairlightweight.filters.price_projection(
        #         price_data=['EX_BEST_OFFERS'],
        #         ex_best_offers_overrides=order_filter,
        #     )

        #     market_id_list = filtro_mercado_id_odds['IdMercado'].to_list()

        #     market_books = trading.betting.list_market_book(
        #         market_ids=market_id_list,
        #         price_projection=price_filter,
        #     )

        #     odds = []
        #     casa, empate, fora, over25, under25 = [], [], [], [], []

        #     for market in market_books:
        #         runners = market.runners

        #         for i in range(0,3):
        #             try:
        #                 odds.append([runner_book.ex.available_to_back[i].price
        #                             if runner_book.ex.available_to_back
        #                             else 1.01
        #                             for runner_book in runners])
        #             except:
        #                 odds.append([1.01, 1.01, 1.01])

        #     if odds[0][1] > 1.01:
        #         for mercado in catalogos_mercado:
        #             if mercado.market_name == 'First Half Goals 0.5' and mercado.total_matched > 0:
        #                 selecao_gols_acima = mercado.runners[0].selection_id
        #                 odds_gols_acima = odds[0][1]
        #                 valor_aposta = 5.0
        #                 retorno_esperado = valor_aposta * odds_gols_acima

        #                 limit_order_filter = betfairlightweight.filters.limit_order(
        #                     size=valor_aposta,
        #                     price=odds_gols_acima,
        #                     persistence_type='PERSIST'
        #                 )

        #                 resposta = betfairlightweight.filters.place_instruction(
        #                     selection_id=mercado.runners[1].selection_id,
        #                     order_type="LIMIT",
        #                     side="BACK",
        #                     limit_order=limit_order_filter
        #                 )

        #                 # print(f"Aposta feita com sucesso! ID da aposta: {resposta['instructionReports'][0]['betId']}")
        #                 # print(f"Valor apostado: {valor_aposta:.2f} / Odds: {odds_gols_acima:.2f} / Retorno esperado: {retorno_esperado:.2f}")

        #                 order = trading.betting.place_orders (
        #                 market_id=mercado.market_id, # The market id we obtained from before
        #                 customer_strategy_ref='back_the_fav',
        #                 instructions=[resposta] # This must be a list
        #         )

        #         return order.__dict__['_data']['instructionReports'][0]['status'], retorno_esperado
        #         # return "SUCCESS", retorno_esperado
        # except Exception as e:
        #     traceback.print_exc()

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

        for game in dic_response['data']:
            awayTeam = game['awayTeam']['name']
            homeTeam = game['homeTeam']['name']
            status = game['status']
            minute = game['currentTime']['minute']
            awayTeamScore = game['scores']['homeTeamScore']
            homeTeamScore = game['scores']['awayTeamScore']
            league = game['league']['name']

            print(f'{homeTeam} x {awayTeam} - {minute} - {status} - {awayTeamScore} x {homeTeamScore} ({league})')

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

            # at_over_0_5 = game['probabilities']['AT_over_0_5']
            # at_over_1_5 = game['probabilities']['AT_over_1_5']
            # at_under_0_5 = game['probabilities']['AT_under_0_5']
            # at_under_1_5 = game['probabilities']['AT_under_1_5']
            # ht_over_0_5 = game['probabilities']['HT_over_0_5']
            # ht_over_1_5 = game['probabilities']['HT_over_1_5']
            # ht_under_0_5 = game['probabilities']['HT_under_0_5']
            # ht_under_1_5 = game['probabilities']['HT_under_1_5']
            # away = game['probabilities']['away']
            # btts = game['probabilities']['btts']
            # draw = game['probabilities']['draw']
            # home = game['probabilities']['home']
            # over_0_5 = game['probabilities']['over_0_5']
            # over_1_5 = game['probabilities']['over_1_5']
            # over_2_5 = game['probabilities']['over_2_5']
            # over_3_5 = game['probabilities']['over_3_5']
            # under_0_5 = game['probabilities']['under_0_5']
            # under_1_5 = game['probabilities']['under_1_5']
            # under_2_5 = game['probabilities']['under_2_5']
            # under_3_5 = game['probabilities']['under_3_5']

            attacks_home = game['stats']['attacks']['home']
            attacks_away = game['stats']['attacks']['away']

            # ballSafe_home = game['stats']['ballSafe']['home']
            # ballSafe_away = game['stats']['ballSafe']['away']

            corners_home = game['stats']['corners']['home']
            corners_away = game['stats']['corners']['away']

            # dangerousAttacks_home = game['stats']['dangerousAttacks']['home']
            # dangerousAttacks_away = game['stats']['dangerousAttacks']['away']

            fouls_home = game['stats']['fouls']['home']
            fouls_away = game['stats']['fouls']['away']

            # freeKick_home = game['stats']['freeKick']['home']
            # freeKick_away = game['stats']['freeKick']['away']

            # goalAttempts_home = game['stats']['goalAttempts']['home']
            # goalAttempts_away = game['stats']['goalAttempts']['away']

            # goalKick_home = game['stats']['goalKick']['home']
            # goalKick_away = game['stats']['goalKick']['away']

            goals_home = game['stats']['goals']['home']
            goals_away = game['stats']['goals']['away']

            # injuries_home = game['stats']['injuries']['home']
            # injuries_away = game['stats']['injuries']['away']

            offsides_home = game['stats']['offsides']['home']
            offsides_away = game['stats']['offsides']['away']

            # penalties_home = game['stats']['penalties']['home']
            # penalties_away = game['stats']['penalties']['away']

            possessiontime_home = game['stats']['possessiontime']['home']
            possessiontime_away = game['stats']['possessiontime']['away']

            redcards_home = game['stats']['redcards']['home']
            redcards_away = game['stats']['redcards']['away']

            # saves_home = game['stats']['saves']['home']
            # saves_away = game['stats']['saves']['away']

            # shotsBlocked_home = game['stats']['shotsBlocked']['home']
            # shotsBlocked_away = game['stats']['shotsBlocked']['away']

            # shotsInsidebox_home = game['stats']['shotsInsidebox']['home']
            # shotsInsidebox_away = game['stats']['shotsInsidebox']['away']

            shotsOffgoal_home = game['stats']['shotsOffgoal']['home']
            shotsOffgoal_away = game['stats']['shotsOffgoal']['away']

            shotsOngoal_home = game['stats']['shotsOngoal']['home']
            shotsOngoal_away = game['stats']['shotsOngoal']['away']

            shotsOutsidebox_home = game['stats']['shotsOutsidebox']['home']
            shotsOutsidebox_away = game['stats']['shotsOutsidebox']['away']

            # substitutions_home = game['stats']['substitutions']['home']
            # substitutions_away = game['stats']['substitutions']['away']

            tackles_home = game['stats']['tackles']['home']
            tackles_away = game['stats']['tackles']['away']

            # throwIn_home = game['stats']['throwIn']['home']
            # throwIn_away = game['stats']['throwIn']['away']

            yellowcards_home = game['stats']['yellowcards']['home']
            yellowcards_away = game['stats']['yellowcards']['away']

            # yellowredcards_home = game['stats']['yellowredcards']['home']
            # yellowredcards_away = game['stats']['yellowredcards']['away']

            # dangerousAttacks_home = game['stats']['dangerousAttacks']['home']
            # dangerousAttacks_away = game['stats']['dangerousAttacks']['away']

            # appm1_home = game['pressureStats']['appm1']['home']
            # appm1_away = game['pressureStats']['appm1']['away']

            # appm2_home = game['pressureStats']['appm2']['home']
            # appm2_away = game['pressureStats']['appm2']['away']

            # attack_momentum_home = game['pressureStats']['attack_momentum']['home']
            # attack_momentum_away = game['pressureStats']['attack_momentum']['away']

            # exg_home = game['pressureStats']['exg']['home']
            # exg_away = game['pressureStats']['exg']['away']

            # mh1_home = game['pressureStats']['mh1']['home']
            # mh1_away = game['pressureStats']['mh1']['away']

            # mh2_home = game['pressureStats']['mh2']['home']
            # mh2_away = game['pressureStats']['mh2']['away']

            # mh3_home = game['pressureStats']['mh3']['home']
            # mh3_away = game['pressureStats']['mh3']['away']

            novo_dado = {
                # 'id':iD,
                'minute': minute,
                # 'homeTeam': homeTeam,
                # 'awayTeam': awayTeam,
                'league': league,
                # 'at_over_0_5': at_over_0_5,
                # 'at_over_1_5': at_over_1_5,
                # 'at_under_0_5': at_under_0_5,
                # 'at_under_1_5': at_under_1_5,
                # 'ht_over_0_5': ht_over_0_5,
                # 'ht_over_1_5': ht_over_1_5,
                # 'ht_under_0_5': ht_under_0_5,
                # 'ht_under_1_5': ht_under_1_5,
                # 'away': away,
                # 'btts': btts,
                # 'draw': draw,
                # 'home': home,
                # 'over_0_5': over_0_5,
                # 'over_1_5': over_1_5,
                # 'over_2_5': over_2_5,
                # 'over_3_5': over_3_5,
                # 'under_0_5': under_0_5,
                # 'under_1_5': under_1_5,
                # 'under_2_5': under_2_5,
                # 'under_3_5': under_3_5,
                # 'attacks_home': attacks_home,
                # 'attacks_away': attacks_away,
                'corners_home': corners_home,
                'corners_away': corners_away,
                # 'dangerousAttacks_home': dangerousAttacks_home,
                # 'dangerousAttacks_away': dangerousAttacks_away,
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
                # 'attack_momentum_home': attack_momentum_home,
                # 'attack_momentum_away': attack_momentum_away,
                # 'exg_home': exg_home,
                # 'exg_away': exg_away,
                # 'appm1_home': appm1_home,
                # 'appm1_away': appm1_away,
                # 'mh1_home': mh1_home,
                # 'mh1_away': mh1_away,
                # 'mh2_home': mh2_home,
                # 'mh2_away': mh2_away,
                # 'mh3_home': mh3_home,
                # 'mh3_away': mh3_away,
                # 'result': '0'
            }

            Xht = pd.DataFrame(novo_dado, index=[0])

            # try:
            #     id_evento = game['betfairId']
            # except:
            #     continue

            if Xht.isna().sum().sum() > 0:
                continue

            # print(
            #     f'{homeTeam} x {awayTeam} - {minute} - {status} - {awayTeamScore} x {homeTeamScore}')
            

            # rede neural
            if iD in id_over05HTmodel:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_model += 1
                    id_over05HTmodel.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor

                    text = f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem over 0.5 ht

            ✅ Win {winht_model} - {loseht_model}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}
    '''
                    sendMenssageTelegram(text)

                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_model += 1
                    id_over05HTmodel.remove(iD)
                    lucro -= 5
                    text = f'''{len(id_over05HTmodel)} 👑 Modelo de aprendizagem over 0.5 ht

            🛑 Lose {winht_model} - {loseht_model}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}
    '''
                    sendMenssageTelegram(text)

            # random forest
    #         if iD in id_over05HTrandomforest:
    #             if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
    #                 winht_randomforest += 1
    #                 id_over05HTrandomforest.remove(iD)
    #                 valor = valorEsperado - 5
    #                 lucro += valor

    #                 text = f'''{len(id_over05HTrandomforest)} 👑 Modelo Random Forest over 0.5 ht

    #         ✅ Win {winht_randomforest} - {loseht_randomforest}
    #         💰 Lucro: {lucro:.2f}

    #         🚨 Jogo: {homeTeam} x {awayTeam}
    #         ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    #         🏆 Liga: {league}
    #         ⏱️ Minuto: {minute}
    # '''
    #                 sendMenssageTelegram(text)

    #             if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
    #                 loseht_randomforest += 1
    #                 id_over05HTrandomforest.remove(iD)
    #                 lucro -= 5
    #                 text = f'''{len(id_over05HTrandomforest)} 👑 Modelo Random Forest over 0.5 ht

    #         🛑 Lose {winht_randomforest} - {loseht_randomforest}
    #         💰 Lucro: {lucro:.2f}
            
    #         🚨 Jogo: {homeTeam} x {awayTeam}
    #         ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    #         🏆 Liga: {league}
    #         ⏱️ Minuto: {minute}
    # '''
    #                 sendMenssageTelegram(text)

            # Automl
            if iD in id_over05HTAutoml:
                if minute <= 45 and (awayTeamScore + homeTeamScore) > 0:
                    winht_Automl += 1
                    id_over05HTAutoml.remove(iD)
                    valor = valorEsperado - 5
                    lucro += valor

                    text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl over 0.5 ht

            ✅ Win {winht_Automl} - {loseht_Automl}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}
    '''
                    sendMenssageTelegram(text)
                
                if status == 'HT' and (awayTeamScore + homeTeamScore) == 0:
                    loseht_Automl += 1
                    id_over05HTAutoml.remove(iD)
                    lucro -= 5
                    text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl over 0.5 ht

            🛑 Lose {winht_Automl} - {loseht_Automl}
            💰 Lucro: {lucro:.2f}

            🚨 Jogo: {homeTeam} x {awayTeam}
            ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
            🏆 Liga: {league}
            ⏱️ Minuto: {minute}
    '''
                    sendMenssageTelegram(text)
            


            condicao5min = 0
            # condicao5min_randomforest = 0
            condicao5min_Automl = 0

            if minute >= 15 and minute < 35:
                try:
                    preprocessor = pickle.load(
                        open('models/preprocessor.pickle', 'rb'))

                    # Xht = preprocessor.transform(Xht).toarray()
                    Xht = preprocessor.transform(Xht)
                    Xht_h2o = h2o.H2OFrame(Xht)

                except Exception as e:
                    print(e)
                    continue

                if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                    print(
                        f'{homeTeam} x {awayTeam} rede: {model.predict(Xht)[0][0]}')
                    # print(f'{homeTeam} x {awayTeam} rede: {model.predict_proba(Xht)[0][1]}')
                    # print(
                    #     f'{homeTeam} x {awayTeam} randomforest: {model_randomforest.predict_proba(Xht)[0][1]}')

                    print(
                        f"{homeTeam} x {awayTeam} Automl: {h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']}")

                    if model.predict(Xht)[0][0] >= 0.75:

                        condicao5min = 1
                    # if model_randomforest.predict_proba(Xht)[0][1] >= 0.75:
                    #     condicao5min_randomforest = 1

                    if h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1'] >= 0.75:
                        condicao5min_Automl = 1

            if condicao5min == 1 and iD not in id_over05HTmodel:
                id_over05HTmodel.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTmodel)} 👑 Modelo Rede Neural over 0.5 ht

    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {model.predict(Xht)[0][0]}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    📈 Ataques: {attacks_home} - {attacks_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
'''
                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)

#             if condicao5min_randomforest == 1 and iD not in id_over05HTrandomforest:
#                 id_over05HTrandomforest.append(iD)
#                 # state, valorEsperado = makeBet(id_evento)
#                 state, valorEsperado = 'SUCCESS', 10

#                 text = f'''{len(id_over05HTrandomforest)} 👑 Modelo Random Forest over 0.5 ht
#     🚨 Jogo: {homeTeam} x {awayTeam}
#     💭 Previsão: {model_randomforest.predict_proba(Xht)[0][1]}
#     📈 Estado da aposta: {state}
#     💰 Valor esperado da aposta: {valorEsperado:.2f}
#     ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
#     🏆 Liga: {league}
#     ⏱️ Minuto: {minute}

#     📋 Estatísticas
#     🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
#     🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
#     ⛳ Escanteios: {corners_home} - {corners_away}
#     📈 Ataques: {attacks_home} - {attacks_away}
#     ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
#     🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
#     🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
# '''
#                 if '&' in text:
#                     text = text.replace('&', '')
#                 sendMenssageTelegram(text)

            if condicao5min_Automl == 1 and iD not in id_over05HTAutoml:
                id_over05HTAutoml.append(iD)
                # state, valorEsperado = makeBet(id_evento)
                state, valorEsperado = 'SUCCESS', 10

                text = f'''{len(id_over05HTAutoml)} 👑 Modelo Automl over 0.5 ht
    🚨 Jogo: {homeTeam} x {awayTeam}
    💭 Previsão: {h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']}
    📈 Estado da aposta: {state}
    💰 Valor esperado da aposta: {valorEsperado:.2f}
    ⚔️ Placar: {homeTeamScore} x {awayTeamScore}
    🏆 Liga: {league}
    ⏱️ Minuto: {minute}

    📋 Estatísticas
    🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
    🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
    ⛳ Escanteios: {corners_home} - {corners_away}
    📈 Ataques: {attacks_home} - {attacks_away}
    ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
    🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
    🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
'''
                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)

        time.sleep(60)
    except Exception as e:
        traceback.print_exc()
        print(e)
        continue
