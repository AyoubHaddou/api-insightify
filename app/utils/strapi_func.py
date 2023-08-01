import pandas as pd 
from datetime import datetime, date
import requests 
import json 
import os 
from dotenv import load_dotenv
load_dotenv()

list_label_nested = {
    "positive": {
        'Delivery': ['Fast Delivery', 'Excellent', 'Correct', 'Corresponding'],
        'Staff': ['Human', 'Good', 'Correct'],
        'Corresponding': ['Good Quality', 'Beautiful', 'Corresponding', 'Not Bad'],
    },
    "negative": {
        'Order Issue': ['Not corresponding', 'Expensive', 'Delivery Issue', 'Staff Problem', 'Stock Problem'],
        'Customer Service Issue': ['Staff Issue', 'Defective Product', 'Stock Problem',],
        'Politics Issue': ['Mask', 'Internal Policies', 'Foreign Policies'],
    },
    'neutral': {
        'Good': ['RAS', 'OK', 'Average Service', 'Service Good', 'Foreign Policies', 'Internal Policies'],
        'Not Bad': ['RAS', 'OK', 'Average Service', 'Service Good', 'Foreign Policies', 'Internal Policies'],
    }
}

types = {
    'text_neutral': 'neutral',
    'text_negative': 'negative',
    'text_positive': 'positive',
}

def prepare_pnn_data(df, month='2023-06', tenant_id=1):

    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%Y-%m')

    start_date = datetime.strptime(month, '%Y-%m')
    end_date = (start_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    mask = (df['date'] >= month) & (df['date'] <= end_date) & (df.tenant_id == tenant_id)
    
    df = df[mask]
    
    df[['positive', 'negative', 'neutral']] = 0
    df.loc[df['prediction_1'] == 'positive', 'positive'] += 1
    df.loc[df['prediction_1'] == 'negative', 'negative'] += 1
    df.loc[df['prediction_1'] == 'neutral', 'neutral'] += 1

    df = df.groupby('date', as_index=False).agg({'negative': 'sum', 'positive': 'sum', 'neutral': 'sum'})

    data_dict = df[['negative', 'positive', 'neutral']].astype(int).to_dict(orient='records')

    result = {
        'data': json.dumps([data_dict[0]]) if len(data_dict) > 0 else json.dumps([{'positive': 0, 'negative': 0, 'neutral': 0}]),
        'tenant': int(tenant_id),
        'type': 'PNN',
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date,
        'entity': None
    }
    return result


def prepare_advanced_analyse(df, month='2023-06', tenant_id=1, pnn_type='neutral'):
    
    start_date = datetime.strptime(month, '%Y-%m')
    end_date = (start_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    mask = (df['date'] >= month) & (df['date'] <= end_date) & (df['prediction_1'] == pnn_type) & (df.tenant_id == tenant_id)
    
    df = df[mask]
    
    analyse = {}

    for key in list_label_nested[pnn_type].keys(): 
        
            df_prep = (df[(df.prediction_2 == key)]
                    .groupby(['prediction_3'], as_index=False)
                    .count()
                    [['prediction_3','review_id']])
            
            analyse_key = [{row['prediction_3']: row['review_id']} for row in df_prep.to_dict(orient='records')]
            total_reviews = df_prep['review_id'].sum()
            analyse_key.append({'total': int(total_reviews)})
            
            for key_nested in list_label_nested[pnn_type][key]:
                if key_nested not in [i for d in analyse_key for i in d.keys()]:
                    analyse_key.append({key_nested: 0})
                    
            analyse_key = {i: next(iter(d.values())) for d in analyse_key for i in d}
            analyse[key] = analyse_key
            
    analyse = {'data': json.dumps([analyse])}
    analyse['tenant'] = int(tenant_id)
    analyse['type'] = f'text {pnn_type}'.upper()
    analyse['from'] = start_date.strftime('%Y-%m-%d')
    analyse['to'] = end_date
    analyse['entity'] = None 
    
    return analyse

def send_json_by_type(df, tenant_id=1, type='PNN'):

    token = os.getenv("STRAPI_TOKEN")
    header = {'Authorization': f'Bearer {token}'}

    # Conversion des dates en objets datetime
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%Y-%m')

    # Liste des années et des mois - 
    # Plus tard : faire la fonction qui prend date_max au lieu de min et date today au lieu de max. Pour Avoir la mise à jours des tables.
    dates_list = []

    # Obtention de la date minimale 
    date_min = df[df.tenant_id == tenant_id]['date'].min()
    date_min = datetime.strptime(date_min, '%Y-%m')

    # Obtention de la date maximal 
    date_max = date.today()
    date_max = datetime(date_max.year, date_max.month, 1)

    # Boucle pour ajouter chaque année et mois dans la liste
    while date_min <= date_max:
        dates_list.append(date_min.strftime('%Y-%m'))
        if date_min.month == 12:
            date_min = datetime(date_min.year + 1, 1, 1)
        else:
            date_min = datetime(date_min.year, date_min.month + 1, 1)

    for month in dates_list:
        if type == 'PNN':
            result = prepare_pnn_data(df, month, tenant_id)
            result = {'data': result}
            requests.post('https://strapi.insightify.tech/api/analyses', headers=header,json=result)
            print(result)
        elif type in ["text_neutral", "text_positive", "text_negative"]:
            result = prepare_advanced_analyse(df, month, tenant_id, types[type])
            result = {'data': result}
            requests.post('https://strapi.insightify.tech/api/analyses', headers=header,json=result)
            print(result)
        else:
            raise(f"Unknown type {type}")
        
        
def send_all_analysis(df):
    types = ['PNN', 'text_negative', 'text_neutral', 'text_positive']
    for id in df.tenant_id.unique():
        for type in types:
            send_json_by_type(df, id, type)