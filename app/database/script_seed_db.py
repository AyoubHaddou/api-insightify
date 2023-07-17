from app.database.crud.crud_tenant import post_tenant, run_scrapping_trustpilot
from app.database.models.analysis import Analysis 
from app.database.models.entity import Entity 
from app.database.models.review import Review
from app.database.models.tenant import Tenant

names = ['Auchan', 'Decathlon', 'Leroy Merlin', 'Norauto']
types = ['store', 'store', 'store', 'car_repair']
url_webs = ['www.auchan.fr', 'www.decathlon.fr', 'www.leroymerlin.fr', 'www.norauto.fr']

for name, url_web, type in zip(names, url_webs, types):
    print('new TENANT in START', name)
    post_tenant(name, type, url_web)