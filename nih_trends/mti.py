from nih_trends.meta import session
from nih_trends.models import Award, Abstract

def write_abstracts(path, offset, limit):
    query = session.query(
        Abstract
    ).join(
        Award,
        Abstract.application_id == Award.application_id
    ).filter(
        Award.activity == 'R01',
        Award.application_type == 1,
    )
    rows = query[offset:offset + limit]
    with open(path, 'w') as fp:
        fp.writelines(
            '{}|{}\n'.format(row.application_id, row.abstract_text)
            for row in rows
        )
