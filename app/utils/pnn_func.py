import pandas as pd 
from transformers import pipeline
from sentry_sdk import capture_message
from logging_config import logger 
sentiment_model = pipeline(model="IAyoub/finetuning-bert-sentiment-reviews-2")

def pnn_dict(label):
    label_dict = {
        'LABEL_0': 'negative',
        'LABEL_1': 'neutral',
        'LABEL_2':'positive',
    }
    return label_dict[label]

def run_prediction_pnn(df):
    logger.info('Predictions PNN des avis en cours...')
    pred = predict_multi_rows(df.text_en.to_list())
    pred = pd.Series([v for v in pred.values()])
    df[['prediction_1', 'score_1']] = pred
    df['type_1'] = 'PNN'
    
    
    return df

def predict_single_row(text: str) -> str:
    pred = sentiment_model(text)[0]
    capture_message('SINGLE PREDICTION PNN')
    return {'prediction': pnn_dict(pred['label']), 
            'score': pred['score']}

def predict_multi_rows(texts_list: list) -> dict:
    result = {'prediction': [pnn_dict(sentiment_model(i)[0]['label']) for i in texts_list], 
            'score': [sentiment_model(i)[0]['score'] for i in texts_list]}
    capture_message('MULTI PREDICTION PNN')
    return result 
