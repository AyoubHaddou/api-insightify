import time
import requests
import pandas as pd
import datetime
import os 

lille_coord = "50.6292,3.0573"
paris_coord = "48.868989, 2.351839"
marseille_coord = "43.301057, 5.393005"
lyon_coord = "45.758063, 4.841824"
reims_coord = "49.254654, 4.026955"
nantes_coord = "47.173916, -1.564743"
rennes_coord = "48.117761, -1.685869"
bordeaux_coord = "44.831214, -0.578428"
all_coord = [lille_coord, paris_coord, marseille_coord, lyon_coord, reims_coord,nantes_coord, rennes_coord, bordeaux_coord]

def generate_entreprises_by_name(search_coord, search_name, search_type):

    num_limit = 80

    tenant_names = []
    tenant_ratings = []
    tenant_types = []
    tenant_place_ids = []
    tenant_addresses = []

    request_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": search_coord,
        "radius": 50000,
        "type": search_type,
        "keyword": search_name,
        "key": os.getenv("API_KEY_GOOGLE")
    }

    while True:
        time.sleep(3)
        response = requests.get(request_url, params=params)
        data = response.json()
        results = data["results"]

        if response.status_code == 200:
            for result in results:
                tenant_name = result.get("name", "")
                tenant_rating = result.get("rating", "")
                tenant_type = result.get("types", [])
                place_id = result.get("place_id", "")
                address = result.get("vicinity", "")

                tenant_names.append(tenant_name)
                tenant_ratings.append(tenant_rating)
                tenant_types.append(tenant_type)
                tenant_place_ids.append(place_id)
                tenant_addresses.append(address)

        if "next_page_token" not in data or len(tenant_place_ids) >= num_limit:
            print(len(tenant_place_ids), "found in", search_coord)
            break

        next_page_token = data["next_page_token"]
        params["pagetoken"] = next_page_token
    
    return pd.DataFrame({'name': tenant_names, 'rating': tenant_ratings, 'place_id': tenant_place_ids, 'type': tenant_types, 'address': tenant_addresses})


def generate_reviews(place_id, entity_id, month=None):
    review_ratings = []
    review_texts = []
    review_dates = []

    api_key = os.getenv("API_KEY_GOOGLE")
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews&key={api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if "reviews" in data["result"]:
            reviews = data["result"]["reviews"]
            for review in reviews:
                review_rating = review.get("rating", "")
                review_comment = review.get("text", "")
                review_date = datetime.datetime.fromtimestamp(review.get("time", ""))
                
                if month is None or review_date.strftime("%Y-%m") == month:
                    review_ratings.append(review_rating)
                    review_texts.append(review_comment)
                    review_dates.append(review_date)
                    
    return pd.Series([entity_id, review_ratings, review_texts, review_dates])