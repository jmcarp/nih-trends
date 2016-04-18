import ujson as json
from flask import Blueprint
from marshmallow import fields
from webargs.flaskparser import use_kwargs
import sqlalchemy as sa

from nih_trends import models
from nih_trends import schemas
from nih_trends.meta import session

blueprint = Blueprint('api', __name__)

def paginate_query(query, page, per_page):
    per_page = max(per_page, 20)
    query = query.limit(per_page)
    query = query.offset((page - 1) * per_page)
    return query

def sort_query(query, key):
    if key:
        order = sa.desc if key.startswith('-') else sa.asc
        key = key.lstrip('-')
        query = query.order_by(order(key))
    return query

def jsonify(value):
    return json.dumps(value), 200, {'Content-Type': 'application/json'}

@blueprint.route('/awards/')
@use_kwargs({
    'year': fields.List(fields.Integer, missing=[]),
    'activity': fields.String(missing='R01'),
    'application_type': fields.Integer(missing=1),
    'term': fields.List(fields.String, missing=[]),
    'sort': fields.String(missing=None),
    'page': fields.Integer(missing=1),
    'per_page': fields.Integer(missing=20),
})
def awards(**kwargs):
    query = session.query(models.Award)
    if kwargs['year']:
        query = query.filter(models.Award.fy.in_(kwargs['year']))
    if kwargs['activity']:
        query = query.filter(models.Award.activity == kwargs['activity'])
    if kwargs['application_type']:
        query = query.filter(models.Award.application_type == kwargs['application_type'])
    if kwargs['term']:
        query = query.join(
            models.MtiTerm,
            models.Award.application_id == models.MtiTerm.application_id,
        ).filter(
            models.MtiTerm.term.in_(kwargs['term']),
        )
    query = paginate_query(query, kwargs['page'], kwargs['per_page'])
    query = sort_query(query, kwargs['sort'])
    return jsonify({
        'results': schemas.AwardSchema(many=True).dump(query).data,
    })

@blueprint.route('/terms/counts/year/')
@use_kwargs({
    'year': fields.List(fields.Integer, missing=[]),
    'term': fields.List(fields.String, missing=[]),
    'sort': fields.String(missing=None),
    'page': fields.Integer(missing=1),
    'per_page': fields.Integer(missing=20),
})
def term_counts_year(**kwargs):
    query = session.query(models.MtiCountYear)
    if kwargs['year']:
        query = query.filter(models.MtiCountYear.fy.in_(kwargs['year']))
    if kwargs['term']:
        query = query.filter(models.MtiCountYear.term.in_(kwargs['term']))
    query = paginate_query(query, kwargs['page'], kwargs['per_page'])
    query = sort_query(query, kwargs['sort'])
    return jsonify({
        'results': schemas.MtiCountSchema(many=True).dump(query).data,
    })

@blueprint.route('/terms/dispersion/')
@use_kwargs({
    'term': fields.List(fields.String, missing=[]),
    'sort': fields.String(missing=None),
    'page': fields.Integer(missing=1),
    'per_page': fields.Integer(missing=20),
})
def term_dispersion(**kwargs):
    query = session.query(models.MtiDispersion)
    if kwargs['term']:
        query = query.filter(models.MtiDispersion.term.in_(kwargs['term']))
    query = paginate_query(query, kwargs['page'], kwargs['per_page'])
    query = sort_query(query, kwargs['sort'])
    return jsonify({
        'results': schemas.MtiDispersionSchema(many=True).dump(query).data,
    })
