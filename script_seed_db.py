import app.database.crud.crud_tenant as crud_tenant
from app.database.models.analysis import Analysis 
from app.database.models.entity import Entity 
from app.database.models.review import Review
from app.database.models.tenant import Tenant
from app.database.models.translation import Translation

names = ['Decathlon', 'Leroy Merlin', 'Norauto']
url_webs = ['www.decathlon.fr', 'www.leroymerlin.fr', 'www.norauto.fr']
types = [ 'store', 'store', 'car_repair']

for name, url_web, type in zip(names, url_webs, types):
    print('new TENANT in START', name)
    crud_tenant.post_tenant(name, type, url_web)
    
    
    
# from app.utils.data_processing import process_monthly_tenant_reviews

# tenant_id = 4
# month = '2023-08'
# tenant = crud_tenant.get_tenant_by_id(tenant_id)
# process_monthly_tenant_reviews(tenant, month)