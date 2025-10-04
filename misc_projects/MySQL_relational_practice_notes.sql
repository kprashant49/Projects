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

Select title, round(avg(rating),2) as avg_rating from series join reviews on series.id = reviews.series_id
group by title order by 2;

Select first_name, last_name, rating from reviewers join reviews on reviewers.id = reviews.reviewer_id;

Select title from series left join reviews on series.id = reviews.series_id where rating is null;

Select genre, round(avg(rating),2) as avg_rating from series join reviews on series.id = reviews.series_id
group by genre order by 1;

Select first_name, last_name, count(rating) as count, ifnull(min(rating),0) as min, ifnull(max(rating),0) as max, ifnull(avg(rating),0) as avg,
case when count(rating) = 0 then "Inactive" else "Active" end as Status from reviewers left join reviews on reviewers.id = reviews.reviewer_id
group by first_name, last_name;

Select first_name, last_name, count(rating) as count, ifnull(min(rating),0) as min, ifnull(max(rating),0) as max, ifnull(avg(rating),0) as avg,
if (count(rating) = 0, "Inactive","Active") as Status from reviewers left join reviews on reviewers.id = reviews.reviewer_id
group by first_name, last_name;

Select title, rating, concat(first_name,' ' ,last_name) as reviewer from series join reviews on series.id = reviews.series_id
join reviewers on reviewers.id = reviews.reviewer_id order by 1;

Create view full_reviews as 
Select title, rating, concat(first_name,' ' ,last_name) as reviewer from series join reviews on series.id = reviews.series_id
join reviewers on reviewers.id = reviews.reviewer_id order by 1;

Select * from full_reviews