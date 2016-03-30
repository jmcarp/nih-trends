import os
import urllib

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date

def fetch_archives(url, base_path, overwrite=False):
    response = requests.get(url)
    html = BeautifulSoup(response.content)
    rows = html.find_all('tr', class_='row_bg')
    os.makedirs(base_path, exist_ok=True)
    for row in rows:
        columns = row.find_all('td')
        link_column, date_column = columns[-2:]
        link_href = link_column.find('a').attrs['href']
        download_url = urllib.parse.urljoin(url, link_href)
        last_updated = parse_date(date_column.text)
        path = get_path(base_path, download_url)
        mtime = get_mtime(path)
        if overwrite and mtime and mtime > last_updated.timestamp():
            continue
        fetch_file(download_url, path)

def get_path(base_path, url):
    _, path = os.path.split(url)
    return os.path.join(base_path, path)

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
