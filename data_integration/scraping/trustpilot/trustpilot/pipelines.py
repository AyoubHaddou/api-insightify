from datetime import datetime, timedelta
import pandas as pd
import re
from dotenv import load_dotenv
import os 
from sqlalchemy import create_engine
load_dotenv()

PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')
PGHOST = os.getenv('PGHOST')
PGPORT = os.getenv('PGPORT')
PGDATABASE = os.getenv('PGDATABASE')


SQLALCHEMY_DATABASE_URL = f'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

class TrustpilotPipeline:
    def __init__(self):
        self.data = {
            'review_rating': [],
            'title': [],
            'comment': [],
            'date': []
        }

    def process_item(self, item, spider):
        review_rating = item['review_rating']
        titles = item['title']
        comments = item['comment']
        dates = item['date']

        for i in range(max(len(review_rating), len(titles), len(comments), len(dates))):
            # Vérifier si la date est présente et non vide
            if i < len(dates) and dates[i]:
                # Convertir la date en objet datetime
                date_str = dates[i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                new_date_str = date_obj.strftime("%Y-%m-%d")
            
                # Extraire la note à partir du nom du fichier SVG
                rating_svg = review_rating[i] if i < len(review_rating) else ''
                rating_match = re.search(r'stars-(\d)\.svg', rating_svg)
                rating = rating_match.group(1) if rating_match else ''
                self.data['review_rating'].append(rating)
                self.data['title'].append(titles[i] if i < len(titles) else '')
                self.data['comment'].append(comments[i] if i < len(comments) else '')
                self.data['date'].append(new_date_str)
        return item

    def close_spider(self, spider):
        df = pd.DataFrame(self.data)
        df.title = df.title.astype(str)
        df.comment = df.comment.astype(str)
        df['text'] = df.title + ' - ' + df.comment 
        print('----------------------------------------------------------------')
        print(os.getenv('TENANT_ID'))
        print(PGDATABASE)
        df['tenant_id'] = int(os.getenv('TENANT_ID'))
        df['source'] = 'trustpilot'
        df = df[(df.text.isna() == False) & (df.text.values != '') & (df.text.str.len() < 512)]
        df = df.rename(columns={'review_rating': 'rating'})
        # df[['tenant_id', 'text', 'rating', 'date', 'source']].to_sql('review', engine, index=False, if_exists='append') 
        df[['tenant_id', 'text', 'rating', 'date', 'source']].to_csv(f'TEST_1.csv', index=False) 