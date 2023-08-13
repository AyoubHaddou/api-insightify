import app.database.crud.crud_tenant as crud_tenant
from app.database.models.analysis import Analysis 
from app.database.models.entity import Entity 
from app.database.models.review import Review
from app.database.models.tenant import Tenant
from app.database.models.translation import Translation
from logging_config import logger

tenant_names = ['Decathlon', 'Leroy Merlin', 'Norauto']
tenant_url_webs = ['www.decathlon.fr', 'www.leroymerlin.fr', 'www.norauto.fr']
tenant_types = [ 'store', 'store', 'car_repair']

for tenant_name, tenant_url_web, tenant_type in zip(tenant_names, tenant_url_webs, tenant_types):
    logger.info('new TENANT in START', tenant_name)
    crud_tenant.post_tenant(tenant_name, tenant_type, tenant_url_web)