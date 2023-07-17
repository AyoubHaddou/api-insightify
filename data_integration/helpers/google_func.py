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

def generate_entreprises_by_name(coord, keyword='Decathlon', type='store'):

    num_limit = 50

    names = []
    ratings = []
    types = []
    place_ids = []
    addresses = []

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": coord,
        "radius": 50000,
        "type": type,
        "keyword": keyword,
        "key": os.getenv("API_KEY_GOOGLE")
    }

    while True:
        time.sleep(3)
        response = requests.get(url, params=params)
        data = response.json()
        results = data["results"]

        if response.status_code == 200:
            for result in results:
                name = result.get("name", "")
                rating = result.get("rating", "")
                type = result.get("types", [])
                place_id = result.get("place_id", "")
                address = result.get("vicinity", "")

                names.append(name)
                ratings.append(rating)
                types.append(type)
                place_ids.append(place_id)
                addresses.append(address)

        if "next_page_token" not in data or len(names) >= num_limit:
            print(len(names), "found in", coord)
            break

        next_page_token = data["next_page_token"]
        params["pagetoken"] = next_page_token
    

    return pd.DataFrame({'name': names, 'rating': ratings, 'place_id': place_ids, 'type': types, 'address': addresses})


def generate_reviews(place_id):

    ratings = []
    comments = []
    dates = []
    api_key = os.getenv("API_KEY_GOOGLE")
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews&key={api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if "reviews" in data["result"]:
            reviews = data["result"]["reviews"]
            for review in reviews:
                rating = review.get("rating", "")
                comment = review.get("text", "")
                date = datetime.datetime.fromtimestamp(review.get("time", ""))

                ratings.append(rating)
                comments.append(comment)
                dates.append(date)
                
    return pd.Series([ratings, comments, dates])

# Le generate reviews si jamais j'ai un compte pro google 
# def generate_reviews(place_id):
#     num_limit = 200 # per place_id 

#     ratings = []
#     comments = []
#     dates = []
#     count = 0 
#     api_key = os.getenv("API_KEY_GOOGLE")
#     url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews&key={api_key}"

#     current_date = datetime.datetime.now()

#     while True:
#         time.sleep(3)
#         response = requests.get(url)
#         data = response.json()
#         count += 1
#         if response.status_code == 200:
#             if "reviews" in data["result"]:
#                 reviews = data["result"]["reviews"]
#                 for review in reviews:
#                     rating = review.get("rating", "")
#                     comment = review.get("text", "")
#                     date = datetime.datetime.fromtimestamp(review.get("time", ""))
                    
#                     # Vérifie si le commentaire a moins d'un an
#                     if (current_date - date).days <= 365:
#                         ratings.append(rating)
#                         comments.append(comment)
#                         dates.append(date)

#             # Vérifiez si une autre page de résultats est disponible
#             if "next_page_token" not in data or len(ratings) >= num_limit:
#                 return pd.Series([ratings, comments, dates])

#             # Récupérez le token de la page suivante
#             next_page_token = data["next_page_token"]

#             # Ajoutez le token à l'URL pour obtenir la page suivante
#             url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews&key={api_key}&pagetoken={next_page_token}"