from make_data_imp import main_function
from make_data_imp_full import main_function_full
import datetime
import concurrent.futures 
import pandas as pd

def main():
    date_strings = ['2024-26-02']

    date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in date_strings]
    sorted_dates = sorted(date_objects)
    sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

    recent_date = sorted_date_strings[-1]
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')

    # list of dates unilt today
    list_of_dates = pd.date_range(start=recent_date, end=date_now).strftime('%Y-%m-%d').tolist()
    # list_of_dates = ['2020-10-14']
    # pegar os ultimos 10 dias
    # list_of_dates = list_of_dates[-10:]
    print(len(list_of_dates))

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        # executor.map(main_function, list_of_dates)
        executor.map(main_function_full, list_of_dates)

if __name__ == "__main__":
    main()