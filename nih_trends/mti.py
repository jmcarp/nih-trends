import os
import re
import csv
import logging
from urllib.parse import urljoin

from requests import HTTPError
from robobrowser import RoboBrowser

from nih_trends import config
from nih_trends.meta import session
from nih_trends.models import Award, Abstract, MtiTerm, MtiBatch, MtiBatchItem
from nih_trends.schemas import MtiTermSchema

logger = logging.getLogger(__name__)

def populate_batch(size=2500):
    while True:
        ids = get_batch_ids(size).all()
        if not ids:
            break
        batch = MtiBatch()
        batch.items = [
            MtiBatchItem(application_id=application_id)
            for application_id in ids
        ]
        session.add(batch)
        session.commit()
        write_batch(batch.id)

def get_batch_ids(size):
    return session.query(
        Award.application_id,
    ).outerjoin(
        MtiBatchItem,
        Award.application_id == MtiBatchItem.application_id,
    ).filter(
        Award.activity == 'R01',
        Award.application_type == 1,
        MtiBatchItem.application_id == None,  # noqa
    ).limit(
        size
    )

def write_batch(batch_id):
    logger.info('Writing MTI batch {:04}'.format(batch_id))
    rows = session.query(
        Abstract,
    ).join(
        MtiBatchItem,
        Abstract.application_id == MtiBatchItem.application_id,
    ).filter(
        MtiBatchItem.batch_id == batch_id
    )
    path = get_batch_file(batch_id, 'abstracts')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fp:
        fp.writelines(
            '{}|{}\n'.format(row.application_id, row.abstract_text)
            for row in rows
        )

TERM_FIELDS = (
    'application_id', 'term', 'cui', 'score',
    'type', 'misc', 'location', 'path',
)

def load_batch(batch_id):
    batch = session.query(MtiBatch).filter_by(id=batch_id).one()
    schema = MtiTermSchema()
    with open(get_batch_file(batch_id, 'terms')) as fp:
        reader = csv.DictReader(fp, delimiter='|', fieldnames=TERM_FIELDS)
        rows = list(reader)
        session.query(
            MtiTerm
        ).filter(
            MtiTerm.application_id.in_(
                int(row['application_id']) for row in rows
            )
        ).delete(
            synchronize_session='fetch'
        )
        for row in rows:
            result = schema.load(row, instance=MtiTerm())
            session.add(result.data)
    batch.done = True
    session.commit()

def get_batch_file(batch_id, category):
    return os.path.join(
        config.BATCH_PATH,
        category,
        'batch-{:04d}.txt'.format(batch_id)
    )

MTI_BASE_URL = 'http://ii.nlm.nih.gov'
MTI_BATCH_URL = 'http://ii.nlm.nih.gov/Batch/UTS_Required/mti.shtml'
MTI_CONFIRM_URL = 'http://ii.nlm.nih.gov/cgi-bin/II/Batch/UTS_Required/validate.pl?refDir='  # noqa
MTI_SCHEDULE_RE = re.compile(r'"(.*)"')
MTI_PATH_PREFIX = '/usr/local/apache/htdocs/II'
MAX_SUBMIT = 5

class Submitter:

    def __init__(self):
        self.browser = RoboBrowser(parser='html5lib')

    def login(self):
        self.browser.open(MTI_BATCH_URL)
        form = self.browser.get_form('fm1')
        form['username'] = config.MTI_USERNAME
        form['password'] = config.MTI_PASSWORD
        self.browser.submit_form(form)

    def submit(self, batch_id):
        logger.info('Submitting MTI batch {:04}'.format(batch_id))
        batch = session.query(MtiBatch).filter_by(id=batch_id).one()
        path = get_batch_file(batch_id, 'abstracts')
        self.browser.open(MTI_BATCH_URL)

        form = self.browser.get_form()
        form['Email_Address'] = config.MTI_EMAIL
        form['BatchNotes'] = config.MTI_EMAIL
        form['UpLoad_File'] = open(path)
        form['Filtering'] = ''
        form['SingLinePMID'] = 'Yes'
        form['Output'] = 'detail'
        self.browser.submit_form(form)

        # Confirm submit
        js = self.browser.find('script').text
        param = MTI_SCHEDULE_RE.search(js).groups()[0]
        self.browser.open(MTI_CONFIRM_URL + param)

        batch.submitted = True
        batch.path = param
        session.commit()

    def fetch(self, path, batch_id):
        session = self.browser.session
        path = '{}/text.out'.format(path.replace(MTI_PATH_PREFIX, ''))
        url = urljoin(MTI_BASE_URL, path)
        resp = session.get(url, stream=True)
        resp.raise_for_status()
        with open(get_batch_file(batch_id, 'terms'), 'w') as fp:
            for chunk in resp.iter_content(chunk_size=1024):
                fp.write(chunk)

    @classmethod
    def batch_submit(cls):
        rows = session.query(
            MtiBatch
        ).filter_by(
            submitted=False,
            done=False,
        ).limit(
            MAX_SUBMIT
        )
        if rows:
            submitter = cls()
            submitter.login()
            for batch in rows:
                submitter.submit(batch.id)

    @classmethod
    def batch_fetch(cls):
        submitter = cls()
        submitter.login()
        rows = session.query(
            MtiBatch
        ).filter(
            MtiBatch.submitted == True,  # nqa
            MtiBatch.done == False,  # noqa
            MtiBatch.path != None,  # noqa
        )
        for row in rows:
            try:
                submitter.fetch(row.path, row.id)
                load_batch(row.id)
            except HTTPError as exc:
                logger.exception(exc)
