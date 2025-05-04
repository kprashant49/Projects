Select employee.name as name from(Select (Select id from employee where e.managerId = id) as mid, count((Select id from employee where e.managerId = id)) as cnt from employee e
group by mid having cnt >= 5) as inline_query,employee where inline_query.mid = employee.id;


Select mname as name from(Select (Select name from employee where e.managerId = id) as mname, count((Select name from employee where e.managerId = id)) as cnt from employee e
group by mname having cnt >= 5) as inline_query;



(Select max(count) as max from (select count(managerId) as count from employee group by managerId) as maximum);

Select * from employee




