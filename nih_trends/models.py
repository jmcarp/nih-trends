import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

from nih_trends.meta import Base, engine

class Award(Base):
    __tablename__ = 'award'
    __table_args__ = (
        sa.Index(None, 'nih_spending_cats', postgresql_using='gin'),
        sa.Index(None, 'project_terms', postgresql_using='gin'),
    )

    application_id = sa.Column(sa.Integer, primary_key=True)
    activity = sa.Column(sa.Text, index=True)
    administering_ic = sa.Column(sa.Text, index=True)
    application_type = sa.Column(sa.Text)
    arra_funded = sa.Column(sa.Boolean)
    award_notice_date = sa.Column(sa.Date)
    budget_start = sa.Column(sa.Date)
    budget_end = sa.Column(sa.Date)
    ed_inst_type = sa.Column(sa.Text)
    full_project_num = sa.Column(sa.Text)
    fy = sa.Column(sa.Integer, index=True)
    ic_name = sa.Column(sa.Text, index=True)
    nih_spending_cats = sa.Column(psql.ARRAY(sa.Text))
    org_city = sa.Column(sa.Text)
    org_country = sa.Column(sa.Text)
    org_dept = sa.Column(sa.Text)
    org_district = sa.Column(sa.Text)
    org_duns = sa.Column(sa.Text)
    org_fips = sa.Column(sa.Text)
    org_name = sa.Column(sa.Text)
    org_state = sa.Column(sa.Text)
    org_zipcode = sa.Column(sa.Text)
    funding_ics = sa.Column(psql.ARRAY(sa.Text))
    project_start = sa.Column(sa.Date)
    project_end = sa.Column(sa.Date)
    project_terms = sa.Column(psql.ARRAY(sa.Text))
    project_title = sa.Column(sa.Text)
    support_year = sa.Column(sa.Integer)
    total_cost = sa.Column(sa.Numeric(30, 2))
    total_cost_sub_project = sa.Column(sa.Numeric(30, 2))

class Abstract(Base):
    __tablename__ = 'abstract'

    application_id = sa.Column(sa.Integer, primary_key=True)
    abstract_text = sa.Column(sa.Text)

Base.metadata.create_all(engine)
