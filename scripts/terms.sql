drop table if exists mti_term_distinct;

create table mti_term_distinct as
select distinct on (cui)
  cui,
  term,
  to_tsvector(term) as term_text
from mti_term
order by
  cui,
  term
;

alter table mti_term_distinct add primary key cui;

create index on mti_term_distinct using gin (term_text);
