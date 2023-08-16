import pandas as pd 
from datetime import datetime, date
from sentry_sdk import capture_message
import requests 
import os 
import json 
from app.utils.database_queries import get_all_review_data_by_tenant_id
from dotenv import load_dotenv
load_dotenv()

list_label_nested = {
    "positive": {
        'Delivery': ['Fast Delivery', 'Excellent Delivery', 'Accurate Delivery'],
        'Staff': ['Friendly Staff', 'Helpful Staff', 'Polite Staff'],
        'Product Quality': ['Good Quality', 'Beautiful Product', 'Well-made Product'],
    },
    "negative": {
        'Order Issue': ['Expensive', 'Delivery Problem', 'Unhelpful Staff', 'Stock Problem','Defective Product'],
        'Customer Service Issue': ['Unresponsive Support', 'Lack of Issue Resolution', 'Harassment', 'Defective Product'],
        'Politics Issue': ['Corporate Greed', 'Lack of Politeness', 'Harassment'],
    },
    'neutral': {
        'Satisfactory': ['No Particular Issue', 'Average Service', 'Satisfactory Experience'],
        'Acceptable': ['Nothing Remarkable', 'Okay Experience', 'Standard Service'],
    }
}

types_mapping = {
    'text_neutral': 'neutral',
    'text_negative': 'negative',
    'text_positive': 'positive',
}

def send_json_by_type(df, tenant_id, prediction_type, strapi_tenant_id):
    tenant_id = int(tenant_id)
    token = os.getenv("STRAPI_TOKEN")
    header = {'Authorization': f'Bearer {token}'}

    # Conversion des dates en objets datetime
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%Y-%m')

    # Liste des années et des mois
    dates_list = []

    df['date'] = pd.to_datetime(df['date'])
    date_min = df[df.tenant_id == tenant_id]['date'].min()
    date_min = date_min.strftime('%Y-%m')
    date_min = datetime.strptime(date_min, '%Y-%m')

    date_max = date.today()
    date_max = datetime(date_max.year, date_max.month, 1)

    while date_min <= date_max:
        dates_list.append(date_min.strftime('%Y-%m'))
        if date_min.month == 12:
            date_min = datetime(date_min.year + 1, 1, 1)
        else:
            date_min = datetime(date_min.year, date_min.month + 1, 1)

    # Send analysis 
    for month in dates_list:
        if prediction_type == 'PNN':
            result = prepare_pnn_data(df, tenant_id, strapi_tenant_id, month=month) 
            result = {'data': result}
            requests.post('https://strapi.insightify.tech/api/analyses', headers=header, json=result)
        elif prediction_type in ["text_neutral", "text_positive", "text_negative"]:
            result = prepare_advanced_analyse(df, month, tenant_id, types_mapping[prediction_type], strapi_tenant_id) 
            result = {'data': result}
            requests.post('https://strapi.insightify.tech/api/analyses', headers=header, json=result)
        else:
            raise ValueError(f"Unknown type {type}")
        
    # Send reviews
    cols = ['tenant_id', 'text_en','rating','prediction_2', 'prediction_3','source']
    cols_strapi = ['tenant', 'description','rating','category', 'subcategory','source']
    for prediction_1 in list_label_nested.keys():
        for prediction_2 in list_label_nested[prediction_1].keys():
            for prediction_3 in list_label_nested[prediction_1][prediction_2]:
                df_reviews = get_all_review_data_by_tenant_id(tenant_id)
                mask = (df_reviews.prediction_1 == prediction_1) & (df_reviews.prediction_2 == prediction_2) & (df_reviews.prediction_3 == prediction_3)
                df_reviews = df_reviews[mask][0:5]
                df_reviews = df_reviews[cols]
                df_reviews.columns = cols_strapi
                df_reviews['freemium'] = True
                result = df_reviews.to_dict(orient='records')
                if len(result) == 0 :
                    continue 
                for data in result:
                    result = {'data': data}
                    requests.post('https://strapi.insightify.tech/api/reviews', headers=header, json=result)
    
        
def send_all_analysis(df, strapi_tenant_id):
    types = ['PNN', 'text_negative', 'text_neutral', 'text_positive']
    for tenant_id in df.tenant_id.unique():
        for prediction_type in types:
            send_json_by_type(df, tenant_id, prediction_type, strapi_tenant_id)
            capture_message("REQUESTS STRAPI DONE")
            

def prepare_pnn_data(df, tenant_id, strapi_tenant_id, month='2023-06'):
    
    tenant_id = int(tenant_id)

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
        'tenant': int(strapi_tenant_id),
        'type': 'PNN',
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date,
        'entity': None
    }
    return result

def send_notification_to_strapi(notification_type, notification_description, user_id):
    token = os.getenv("STRAPI_TOKEN")
    header = {'Authorization': f'Bearer {token}'}
    data = {
        'type': notification_type,
        'description': notification_description,
        'read': False,
        'user': user_id
    }
    result = {'data': data}
    requests.post('https://strapi.insightify.tech/api/notifications', headers=header, json=result)
    

def prepare_advanced_analyse(df, strapi_tenant_id, month='2023-06', tenant_id=1, pnn_type='neutral'):
    
    tenant_id = int(tenant_id)
    
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
    analyse['tenant'] = int(strapi_tenant_id)
    analyse['type'] = f'text {pnn_type}'.upper()
    analyse['from'] = start_date.strftime('%Y-%m-%d')
    analyse['to'] = end_date
    analyse['entity'] = None 
    
    return analyse