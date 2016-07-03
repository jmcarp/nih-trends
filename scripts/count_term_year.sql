drop table if exists mti_count_term_year;

create table mti_count_term_year as
with counts as (
  select
    award.fy,
    mti_term.cui,
    max(mti_term.term) as term,
    count(*) as count
  from mti_term
  join award using (application_id)
  where mti_term.cui != ''
  group by
    cui,
    award.fy
)
select
  counts.*,
  counts.count / totals.count::numeric as prop
from counts
join mti_count_year totals using (fy)
;

alter table mti_count_term_year add primary key (fy, cui);

create index on mti_count_term_year (cui);
create index on mti_count_term_year (term);
create index on mti_count_term_year (count);
create index on mti_count_term_year (prop);

analyze mti_count_term_year;
