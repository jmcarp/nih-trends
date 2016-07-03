#!/usr/bin/env python

import os
import glob
import logging

import sqlalchemy as sa
from flask_script import Server
from flask_script import Manager

from nih_trends.meta import engine
from nih_trends.load import load_records
from nih_trends.fetch import fetch_archives
from nih_trends.models import Award, Abstract
from nih_trends.schemas import AwardSchema, AbstractSchema
from nih_trends.mti import Submitter, populate_batch
from nih_trends.app import make_app
from nih_trends import config

here = os.path.dirname(__file__)
logger = logging.getLogger(__file__)

app = make_app()
manager = Manager(app)
logging.basicConfig(level=logging.INFO)

manager.add_command('runserver', Server(use_debugger=True, use_reloader=True))

def execute_script(path):
    logger.info('Executing script {}'.format(path))
    with open(path) as fp:
        cmd = '\n'.join(
            line for line in fp.readlines()
            if not line.strip().startswith('--')
        )
        engine.execute(sa.text(cmd))

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
def load_awards(pattern='*.zip'):
    for path in glob.glob(os.path.join(config.DOWNLOAD_PATH, 'awards', pattern)):
        load_records(path, Award, AwardSchema, 'application_id')

@manager.command
def load_abstracts(pattern='*.zip'):
    for path in glob.glob(os.path.join(config.DOWNLOAD_PATH, 'abstracts', pattern)):
        load_records(path, Abstract, AbstractSchema, 'application_id')

@manager.command
def mti_batch_populate():
    populate_batch()

@manager.command
def mti_batch_submit():
    Submitter.batch_submit()

@manager.command
def mti_batch_fetch():
    Submitter.batch_fetch()

SCRIPTS = [
    'count_year.sql',
    'count_term.sql',
    'count_term_year.sql',
    'variance.sql',
]

@manager.command
def build_aggregates():
    for script in SCRIPTS:
        execute_script(os.path.join('scripts', script))

if __name__ == '__main__':
    manager.run()
