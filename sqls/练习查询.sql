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
order by j.job_id, j.location, c.industry, c.company_id asc;

select c.company_id, c.logo_url
from company_data_unclean as c
inner join company_logo_downloaded as c2
on c.company_id = c2.company_id
where c2.downloaded = false
order by c.company_id
limit 12;

select count(*)
from company_data_unclean as c1
limit 10;
update company_logo_downloaded as c
set c.downloaded = true
where c.company_id = c1.company_id;

select c.company_id, c.logo_url
from company_data_unclean as c
order by c.company_id;

insert into company_logo_downloaded(company_id)
select company_id
from company_data_unclean;

select * from company_logo_downloaded;



select count(*) from job_data_unclean;