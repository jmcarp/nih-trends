import os
import glob
import logging

import sqlalchemy as sa

import nih_trends
from nih_trends.meta import engine
from nih_trends.load import load_records
from nih_trends.fetch import fetch_archives
from nih_trends.models import Award, Abstract
from nih_trends.schemas import AwardSchema, AbstractSchema
from nih_trends.mti import Submitter, populate_batch
from nih_trends import config

here = os.path.dirname(nih_trends.__file__)
logger = logging.getLogger(__file__)

logging.basicConfig(level=logging.INFO)

def execute_script(path):
    logger.info('Executing script {}'.format(path))
    with open(path) as fp:
        cmd = '\n'.join(
            line for line in fp.readlines()
            if not line.strip().startswith('--')
        )
        engine.execute(sa.text(cmd))

SCRIPTS = [
    'count_year.sql',
    'count_term.sql',
    'count_term_year.sql',
    'variance.sql',
]

def add_commands(app):

    @app.cli.command()
    def fetch_awards(overwrite=False):
        fetch_archives(
            config.AWARDS_URL,
            os.path.join(config.DOWNLOAD_PATH, 'awards'),
            overwrite=overwrite,
        )

    @app.cli.command()
    def fetch_abstracts(overwrite=False):
        fetch_archives(
            config.ABSTRACTS_URL,
            os.path.join(config.DOWNLOAD_PATH, 'abstracts'),
            overwrite=overwrite,
        )

    @app.cli.command()
    def load_awards(pattern='*.zip'):
        for path in glob.glob(os.path.join(config.DOWNLOAD_PATH, 'awards', pattern)):
            load_records(path, Award, AwardSchema, 'application_id')

    @app.cli.command()
    def load_abstracts(pattern='*.zip'):
        for path in glob.glob(os.path.join(config.DOWNLOAD_PATH, 'abstracts', pattern)):
            load_records(path, Abstract, AbstractSchema, 'application_id')

    @app.cli.command()
    def mti_batch_populate():
        populate_batch()

    @app.cli.command()
    def mti_batch_submit():
        Submitter.batch_submit()

    @app.cli.command()
    def mti_batch_fetch():
        Submitter.batch_fetch()

    @app.cli.command()
    def build_aggregates():
        for script in SCRIPTS:
            execute_script(os.path.join('scripts', script))
