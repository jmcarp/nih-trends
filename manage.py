#!/usr/bin/env python

import os
import glob

from flask_script import Manager

from nih_trends.load import load_awards
from nih_trends.fetch import fetch_archives
from nih_trends.app import make_app
from nih_trends import config

app = make_app()
manager = Manager(app)

@manager.command
def fetch_awards(overwrite=False):
    fetch_archives(
        config.AWARDS_URL,
        os.path.join(config.DOWNLOAD_PATH, 'awards'),
        overwrite=overwrite,
    )

@manager.command
def fetch_abstracts(overwrite=False):
    fetch_archives(
        config.ABSTRACTS_URL,
        os.path.join(config.DOWNLOAD_PATH, 'abstracts'),
        overwrite=overwrite,
    )

@manager.command
def load(pattern='*.zip'):
    for path in glob.glob(os.path.join(config.DOWNLOAD_PATH, pattern)):
        load_awards(path)

if __name__ == '__main__':
    manager.run()
