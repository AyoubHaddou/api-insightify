from sentry_sdk import capture_message
import subprocess
import os 


def run_scrapping_trustpilot(tenant_id, url_web, month):
    
    print('Starting scrapping function for trustpilot')

    os.environ['TENANT_URL'] = url_web
    os.environ['TENANT_ID'] = str(tenant_id) 
    os.environ['TENANT_MONTH'] = month
    
    # Chemin vers le répertoire racine du projet Scrapy
    project_directory = 'app/collection/scraping/trustpilot/trustpilot'

    # Obtention de l'emplacement d'origine
    original_directory = os.getcwd()

    try:
        print('Starting web scraping...')
        # Changement vers le répertoire du projet Scrapy
        os.chdir(project_directory)
        
        # Construction de la commande à exécuter
        command = 'scrapy crawl trustpilotreviews'

        # Exécution de la commande avec les variables d'environnement
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Attend la fin de l'exécution du processus
    finally:
        # Retour à l'emplacement d'origine
        os.chdir(original_directory)
        capture_message("COLLECT BY SCRAPING DONE")
        print('web scraping completed')