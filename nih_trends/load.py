import os
import csv
import zipfile
import tempfile
import itertools

from nih_trends.meta import session
from nih_trends.models import Award
from nih_trends.schemas import AwardSchema

def load_awards(filename, chunk_size=500):
    schema = AwardSchema()
    for fp in iter_files(filename):
        reader = csv.DictReader(fp)
        while True:
            chunk = list(itertools.islice(reader, chunk_size))
            if not chunk:
                break
            instances = {
                instance.application_id: instance for instance in
                session.query(Award).filter(Award.application_id.in_(
                    int(row['APPLICATION_ID']) for row in chunk)
                )
            }
            for row in chunk:
                instance = instances.get(int(row['APPLICATION_ID']), Award())
                result = schema.load(row, instance=instance)
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
