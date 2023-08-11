from transformers import pipeline

translator = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

def translate_fr_to_en(df):

    print('Traduction des avis en cours...')

    traduction = translator(df.text.to_list())
    df['text_en'] = [i['translation_text'] for i in traduction]
    
    df['source_translation'] = 'Helsinki-NLP/opus-mt-fr-en'    

    return df
