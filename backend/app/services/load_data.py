import pandas as pd

def load_csv_data():
    covid_data_path = 'migrations/covid_data_corrected_final.csv'
    country_data_path = 'migrations/country_wise_latest_corrected.csv'
    
    covid_data = pd.read_csv(covid_data_path)
    country_data = pd.read_csv(country_data_path)
    
    return covid_data, country_data