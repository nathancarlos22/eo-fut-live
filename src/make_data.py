import sys
from make_data_imp import *
import datetime
import pandas as pd

from concurrent.futures import ThreadPoolExecutor
import threading
import pandas as pd

df = pd.read_csv('../data/raw/data_live_scores.csv')
date_strings = df['date'].unique()

date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in date_strings]
sorted_dates = sorted(date_objects)
sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

recent_date = sorted_date_strings[-1]
date_now = datetime.datetime.now().strftime('%Y-%m-%d')

# list of dates unilt today
list_of_dates = pd.date_range(start=recent_date, end=date_now).strftime('%Y-%m-%d').tolist()




# Inicializando a lista e o lock
thread_safe_list = []
lock = threading.Lock()

# Executando as tarefas em paralelo e coletando os DataFrames
with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(main_function, list_of_dates, [thread_safe_list]*len(list_of_dates), [lock]*len(list_of_dates), [df]*len(list_of_dates))

# Concatenando todos os DataFrames coletados
if thread_safe_list:  # Verifique se a lista não está vazia
    # final_df = pd.concat(thread_safe_list, ignore_index=True)
    final_df = pd.concat([df] + thread_safe_list, ignore_index=True)
    final_df.to_csv('data_live_scores.csv', index=False)
    
else:
    print("Sem dataframes para concatenar.")
