from transformers import pipeline
from logging_config import logger

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

def translate_fr_to_en(df):

    logger.info('STEP : Review translation starting')

    traduction = translator(df.text.to_list())
    df['text_en'] = [i['translation_text'] for i in traduction]
    
    df['source_translation'] = 'Helsinki-NLP/opus-mt-fr-en'  
    
    df['text_en'] = df['text_en'].str.strip().str[0:511]  

    return df
