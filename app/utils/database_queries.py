import pandas as pd
from app.database.connexion import db 
from app.database.models.analysis import Analysis 
from app.database.models.review import Review
from app.database.models.translation import Translation
from app.database.models.tenant import Tenant

def get_all_review_data_by_tenant_id(tenant_id, month=None):
    query = db.query(Review, Translation, Analysis, Tenant).\
        join(Tenant, Tenant.id == Review.tenant_id).\
        join(Translation, Translation.review_id == Review.id).\
        join(Analysis, Analysis.review_id == Review.id).\
        filter(Tenant.id == int(tenant_id))

    result = query.all()
    
    reviews_data = {}
    for review, translation, analysis, tenant in result:
        review_id = review.id
        if review_id not in reviews_data:
            reviews_data[review_id] = {
                'review_id': review.id,
                'tenant_id': review.tenant_id,
                'strapi_tenant_id': tenant.strapi_tenant_id,
                'entity_id': review.entity_id,
                'text': review.text,
                'rating': review.rating,
                'date': review.date,
                'source': review.source,
                'text_en': translation.text_en,
                'source_translation': translation.source_translation
            }
            
        if analysis.type == 'PNN':
            reviews_data[review_id]['type_1'] = analysis.type
            reviews_data[review_id]['prediction_1'] = analysis.prediction
            reviews_data[review_id]['score_1'] = analysis.score
        elif analysis.type == 'nested_1':
            reviews_data[review_id]['type_2'] = analysis.type
            reviews_data[review_id]['prediction_2'] = analysis.prediction
            reviews_data[review_id]['score_2'] = analysis.score
        elif analysis.type == 'nested_2':
            reviews_data[review_id]['type_3'] = analysis.type
            reviews_data[review_id]['prediction_3'] = analysis.prediction
            reviews_data[review_id]['score_3'] = analysis.score
        
    df = pd.DataFrame(reviews_data.values())

    if isinstance(month, str):
        year, month = map(int, month.split('-'))
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        mask = (df['date'].dt.year == year) & (df['date'].dt.month == month)
        df = df[mask]
    return df

