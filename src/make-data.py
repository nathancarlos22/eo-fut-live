from make_data_imp import main_function
import datetime
import pandas as pd
import argparse
import concurrent.futures 

# def main():
#     # Criar o analisador de argumentos
#     parser = argparse.ArgumentParser(description='Exemplo de Argumento em Python.')

#     # Adicionar um argumento
#     # Neste exemplo, adicionaremos um argumento chamado 'numero', que será um inteiro
#     parser.add_argument('numero', type=int, help='Um número inteiro para processamento.')

#     # Analisar os argumentos
#     args = parser.parse_args()

#     # Usar o argumento
#     print(f"Buscando Datas no intervalo de {args.numero} em {args.numero} dias.")

#     # # Dates games until today

#     # df = pd.read_csv('data_live_scores.csv')
#     # df = df.drop_duplicates()
#     # date_strings = df['date'].unique()
#     date_strings = ['2022-05-21']

#     date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in date_strings]
#     sorted_dates = sorted(date_objects)
#     sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

#     recent_date = sorted_date_strings[-1]
#     date_now = datetime.datetime.now().strftime('%Y-%m-%d')

#     # list of dates unilt today
#     list_of_dates = pd.date_range(start=recent_date, end=date_now).strftime('%Y-%m-%d').tolist()

#     # min_date = min(date_objects)
#     # max_date = max(date_objects)

#     i=0
#     for data in list_of_dates:
#         i+=1
#         if i == args.numero:
#             main_function(data, args.numero)
#             i=0




def main():
    # date_strings = ['2022-05-21']
    date_strings = ['2023-03-24']

    date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in date_strings]
    sorted_dates = sorted(date_objects)
    sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

    recent_date = sorted_date_strings[-1]
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')

    # list of dates unilt today
    list_of_dates = pd.date_range(start=recent_date, end=date_now).strftime('%Y-%m-%d').tolist()
    # pegar os ultimos 10 dias
    # list_of_dates = list_of_dates[-10:]
    print(len(list_of_dates))

    

    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(main_function, list_of_dates)

if __name__ == "__main__":
    main()