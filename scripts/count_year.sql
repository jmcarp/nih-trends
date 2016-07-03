drop table if exists mti_count_year;

create table mti_count_year as
select
  fy,
  count(*)
from award
join mti_batch_item using (application_id)
join mti_batch on mti_batch_item.batch_id = mti_batch.id
where mti_batch.done
group by fy
;

alter table mti_count_year add primary key (fy);

create index on mti_count_year (count);

 analyze mti_count_year;
