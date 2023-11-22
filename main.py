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
# import betfairlightweight
# import configparser



warnings.filterwarnings('ignore')

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

id_over05HTAutoml = []
winht_Automl = 0
loseht_Automl = 0

text = ' '
resultados = {}

minutoss = datetime.now().minute
flag = 0

model = keras.models.load_model('models/model_redeht.h5')

# Inicializar o cluster H2O
h2o.init()
model_Automl = loaded_model = h2o.load_model("./models/model_automl")

preprocessor = pickle.load(
                        open('models/preprocessor.pickle', 'rb'))

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

            attacks_home = game['stats']['attacks']['home']
            attacks_away = game['stats']['attacks']['away']

            corners_home = game['stats']['corners']['home']
            corners_away = game['stats']['corners']['away']

            # dangerousAttacks_home = game['stats']['dangerousAttacks']['home']
            # dangerousAttacks_away = game['stats']['dangerousAttacks']['away']

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

            shotsOutsidebox_home = game['stats']['shotsOutsidebox']['home']
            shotsOutsidebox_away = game['stats']['shotsOutsidebox']['away']

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

            }

            Xht = pd.DataFrame(novo_dado, index=[0])
            
            # Tratando ligas com nomes diferentes, varios grupos, etc..
            if 'Asia - AFC Champions League' in league:
                league = 'Asia - AFC Champions League'
                Xht['league'] = league

            # try:
            #     id_evento = game['betfairId']
            # except:
            #     continue

            if Xht.isna().sum().sum() > 0:
                continue

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

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
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
            
            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)

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

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
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

            📋 Estatísticas
            🦵 Chutes a gol: {shotsOngoal_home} - {shotsOngoal_away}
            🦵 Chutes fora: {shotsOffgoal_home} - {shotsOffgoal_away}
            ⛳ Escanteios: {corners_home} - {corners_away}
            📈 Ataques: {attacks_home} - {attacks_away}
            ⏰ Tempo de posse: {possessiontime_home} - {possessiontime_away}
            🟥 Cartões vermelhos: {redcards_home} - {redcards_away}
            🟨 Cartões amarelos: {yellowcards_home} - {yellowcards_away}
            🔴 Faltas: {fouls_home} - {fouls_away}
            🚩 Impedimentos: {offsides_home} - {offsides_away}
            🛑 Desarmes: {tackles_home} - {tackles_away}
    '''
                    sendMenssageTelegram(text)
            


            condicao5min = 0
            condicao5min_Automl = 0

            if minute >= 1 and minute < 45:
                try:
                    

                    Xht = preprocessor.transform(Xht)
                    Xht_h2o = h2o.H2OFrame(Xht)

                except Exception as e:
                    print(e)
                    continue

                if (awayTeamScore + homeTeamScore) == 0:  # 0 gols
                    print(
                        f'{homeTeam} x {awayTeam} rede: {model.predict(Xht)[0][0]}')

                    print(
                        f"{homeTeam} x {awayTeam} Automl: {h2o.as_list(loaded_model.predict(Xht_h2o)).loc[0, 'p1']}")

                    if model.predict(Xht)[0][0] >= 0.75:

                        condicao5min = 1

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
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''

                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)

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
    🔴 Faltas: {fouls_home} - {fouls_away}
    🚩 Impedimentos: {offsides_home} - {offsides_away}
    🛑 Desarmes: {tackles_home} - {tackles_away}
'''
                if '&' in text:
                    text = text.replace('&', '')
                sendMenssageTelegram(text)

        time.sleep(60)
    except Exception as e:
        traceback.print_exc()
        print(e)
        continue
