drop table if exists mti_dispersion;

create table mti_dispersion as
select
  cui,
  max(term) as term,
  stddev(prop) as stddev,
  avg(prop) as avg,
  stddev(prop) / avg(prop) as disp
from mti_count_term_year
group by cui
;

alter table mti_dispersion add primary key (cui);

create index on mti_dispersion(term);
create index on mti_dispersion(avg);
create index on mti_dispersion(stddev);
create index on mti_dispersion(disp);

analyze mti_dispersion;
