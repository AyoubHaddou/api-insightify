import logging

def get_logger():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger()

    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    return logger

logger = get_logger()




# # Si on veut le rotatingFileHandler pour tout enregistrer sur des fichiers. 
# import logging
# import sys
# import os
# from logging.handlers import RotatingFileHandler

# def get_logger():
#     # Chemin vers le dossier de logs
#     log_folder = 'app/logs'

#     # Configuration de la journalisation avec rotation des fichiers
#     log_file = os.path.join(log_folder, 'app.log')
#     max_log_size = 5 * 1024 * 1024  # 5 Mo

#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
#     # Créer un gestionnaire pour la rotation des fichiers de log
#     file_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=5)
#     file_handler.setLevel(logging.INFO)
#     file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

#     # Ajouter les gestionnaires au logger root
#     logger = logging.getLogger()
#     logger.addHandler(file_handler)

#     # Définir le niveau de journalisation pour le logger "transformers" à WARNING
#     logging.getLogger("transformers").setLevel(logging.WARNING)
    
#     return logger