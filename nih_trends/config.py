import os

AWARDS_URL = 'http://exporter.nih.gov/ExPORTER_Catalog.aspx'
ABSTRACTS_URL = 'http://exporter.nih.gov/ExPORTER_Catalog.aspx?sid=0&index=1'
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql:///nih-trends')
DOWNLOAD_PATH = os.getenv('NIH_DOWNLOAD_PATH', './downloads')
BATCH_PATH = os.getenv('NIH_BATCH_PATH', './batch')

MTI_USERNAME = os.getenv('MTI_USERNAME')
MTI_PASSWORD = os.getenv('MTI_PASSWORD')
MTI_EMAIL = os.getenv('MTI_EMAIL')

CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
