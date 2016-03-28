import os
import urllib

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date

from nih_trends import config

def fetch_awards(overwrite=False):
    response = requests.get(config.EXPORTER_URL)
    html = BeautifulSoup(response.content)
    rows = html.find_all('tr', class_='row_bg')
    os.makedirs(config.DOWNLOAD_PATH, exist_ok=True)
    for row in rows:
        columns = row.find_all('td')
        link_column, date_column = columns[-2:]
        download_url = urllib.parse.urljoin(
            config.EXPORTER_URL,
            link_column.find('a').attrs['href'],
        )
        last_updated = parse_date(date_column.text)
        path = get_path(download_url)
        mtime = get_mtime(path)
        if overwrite and mtime and mtime > last_updated.timestamp():
            continue
        fetch_file(download_url, path)

def get_path(url):
    _, path = os.path.split(url)
    return os.path.join(config.DOWNLOAD_PATH, path)

def fetch_file(url, path):
    response = requests.get(url, stream=True)
    with open(path, 'wb') as fp:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                fp.write(chunk)

def get_mtime(path):
    try:
        return os.stat(path).st_mtime
    except FileNotFoundError:
        return None
