import pandas as pd 
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

sentiment_model = pipeline(model="IAyoub/finetuning-bert-sentiment-reviews")
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

def pnn_dict(label):
    label_dict = {
        'LABEL_0': 'negative',
        'LABEL_1': 'neutral',
        'LABEL_2':'positive',
    }
    return label_dict[label]

def predict_single_row(text: str) -> str:
    pred = sentiment_model(text)[0]
    return pd.Series([pnn_dict(pred['label']), pred['score']])

def predict_multi_rows(texts_list: list) -> list[str]:
    return pd.Series([[pnn_dict(sentiment_model(i)[0]['label']) for i in texts_list], [sentiment_model(i)[0]['score'] for i in texts_list]])