drop table if exists mti_count_year;

create table mti_count_year as
with terms as (
  select
    mti_term.cui,
    mti_term.term,
    award.fy
  from mti_term
  join award using (application_id)
), counts as (
  select
    fy,
    cui,
    max(term) as term,
    count(*) as count
  from terms
  group by
    cui,
    fy
)
select
  counts.*,
  counts.count / totals.count::numeric as prop
from counts
join mti_count_total totals using (fy)
;

alter table mti_count_year add primary key (fy, cui);

create index on mti_count_year (cui);
create index on mti_count_year (term);
create index on mti_count_year (count);
create index on mti_count_year (prop);
