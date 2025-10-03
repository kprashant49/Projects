Select * from customers
select * from orders

SELECT * FROM orders 
WHERE customer_id = (SELECT id FROM customers WHERE last_name = 'George');

Select b.*, a.* from customers a 
right join orders b
on a.id = b.customer_id;

SELECT * FROM orders
JOIN customers ON customers.id = orders.customer_id;

SELECT first_name, last_name, sum(amount) as total FROM orders
JOIN customers ON customers.id = orders.customer_id
group by first_name, last_name
order by total desc;

Select first_name, last_name, ifnull(sum(amount),0) as money_spent from customers a 
left join orders b
on a.id = b.customer_id
group by first_name, last_name;

select first_name, title, grade from students join papers on students.id = papers.student_id order by grade desc;

select first_name, ifnull(title,'MISSING') as title, ifnull(grade, 0) as grade from students left join papers on students.id = papers.student_id;

select first_name, round(ifnull(avg(grade),0),2) as average,
case when round(ifnull(avg(grade),0),2) >= 75 then "Pass"
else "Fail"
end as result
from students left join papers on students.id = papers.student_id group by first_name order by average desc;
