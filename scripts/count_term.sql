create extension if not exists pg_trgm;

drop table if exists mti_count_term;

create table mti_count_term as
select
  cui,
  max(term) as term,
  count(cui) as count,
  count(cui) / (select sum(count) from mti_count_year)::numeric as prop
from mti_term
where cui != ''
group by cui
;

alter table mti_count_term add primary key (cui);

create index on mti_count_term (term);
create index on mti_count_term (count);
create index on mti_count_term (prop);

create index on mti_count_term using gin (term gin_trgm_ops);

analyze mti_count_term;
