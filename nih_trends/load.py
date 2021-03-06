import os
import csv
import zipfile
import tempfile
import itertools

from nih_trends.meta import session

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

def iter_files(filename):
    with tempfile.TemporaryDirectory() as tempdir:
        with open(filename, 'rb') as fp:
            zf = zipfile.ZipFile(fp)
            zf.extractall(path=tempdir)
            for info in zf.infolist():
                with open(os.path.join(tempdir, info.filename), encoding='latin-1') as fp:
                    yield fp
