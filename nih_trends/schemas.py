from marshmallow import fields, pre_load
from marshmallow_sqlalchemy import ModelSchema

from nih_trends.meta import session
from nih_trends.models import Award, Abstract

class Boolean(fields.Boolean):
    truthy = fields.Boolean.truthy | {'Y'}
    falsy = fields.Boolean.falsy | {'N'}

class AwardSchema(ModelSchema):
    class Meta:
        model = Award
        sqla_session = session
        strict = True

    arra_funded = Boolean(missing=None)

    delimited_keys = ('funding_ics', 'project_terms', 'nih_spending_cats')
    transforms = {
        'support_year': {
            'WC': None,
        },
    }

    @pre_load
    def clean_data(self, data):
        # Lower-case keys
        data = {key.lower(): value for key, value in data.items()}

        # Split delimited fields
        for key in self.delimited_keys:
            data[key] = split_delimited(data[key])

        # Null empty fields
        for key in self.fields:
            data[key] = data[key] if data[key] != '' else None

        # Apply transforms
        for key, mapping in self.transforms.items():
            for old, new in mapping.items():
                if data.get(key) == old:
                    data[key] = new

        return data

class AbstractSchema(ModelSchema):
    class Meta:
        model = Abstract
        sqla_session = session
        strict = True

    @pre_load
    def clean_data(self, data):
        return {key.lower(): value for key, value in data.items()}

def split_delimited(value, delimiter=';'):
    values = value.lower().split(delimiter)
    values = [value.strip() for value in values]
    values = [value for value in values if value]
    return values
