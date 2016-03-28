import os

EXPORTER_URL = 'http://exporter.nih.gov/ExPORTER_Catalog.aspx'
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql:///nih-trends')
DOWNLOAD_PATH = os.getenv('NIH_DOWNLOAD_PATH', './downloads')
