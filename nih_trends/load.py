import os
import csv
import zipfile
import tempfile
import itertools

from nih_trends.meta import session
from nih_trends.models import MtiTerm
from nih_trends.schemas import MtiTermSchema

def load_records(filename, model, schema_class, attr, chunk_size=500):
    schema = schema_class()
    for fp in iter_files(filename):
        reader = csv.DictReader(fp)
        while True:
            chunk = list(itertools.islice(reader, chunk_size))
            if not chunk:
                break
            instances = {
                getattr(instance, attr): instance for instance in
                session.query(model).filter(getattr(model, attr).in_(
                    int(row[attr.upper()]) for row in chunk)
                )
            }
            for row in chunk:
                instance = instances.get(int(row[attr.upper()]), model())
                result = schema.load(row, instance=instance)
                session.add(result.data)
            session.commit()

TERM_FIELDS = (
    'application_id', 'term', 'cui', 'score',
    'type', 'misc', 'location', 'path',
)

def load_terms(filename):
    schema = MtiTermSchema()
    with open(filename) as fp:
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
        session.commit()

def iter_files(filename):
    with tempfile.TemporaryDirectory() as tempdir:
        with open(filename, 'rb') as fp:
            zf = zipfile.ZipFile(fp)
            zf.extractall(path=tempdir)
            for info in zf.infolist():
                with open(os.path.join(tempdir, info.filename), encoding='latin-1') as fp:
                    yield fp
