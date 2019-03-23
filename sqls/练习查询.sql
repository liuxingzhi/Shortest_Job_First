insert into job
select *
from job_data_unclean;

insert into company
select *
from company_data_unclean;

select * from job;


select * from job as j
inner join company as c
on c.company_id = j.company_id
where lower(j.job_title) like "%manager%"
and j.location like BINARY "%IL%"
and c.company_name like "%%"
and c.industry like "%Internet%"
order by j.job_id, j.location, c.industry, c.company_id asc