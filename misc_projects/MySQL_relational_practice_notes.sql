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

Create or replace view full_reviews as 
Select title, rating, concat(first_name,' ' ,last_name) as reviewer from series join reviews on series.id = reviews.series_id
join reviewers on reviewers.id = reviews.reviewer_id order by 1;

Select * from full_reviews;

Create or replace view full_reviews AS
SELECT * FROM series ORDER BY released_year desc;

ALTER VIEW full_reviews AS
SELECT * FROM series ORDER BY released_year;

Drop view full_reviews;

Select title, round(avg(rating),1) as avg_rating from full_reviews
group by title
having round(avg(rating),1)>8
and count(rating) > 4
order by 2 desc;

Select title, round(avg(rating),1) as avg_rating from full_reviews
group by title with rollup;

SELECT emp_no, department, salary, AVG(salary) OVER() FROM employees;
 
SELECT 
    emp_no, 
    department, 
    salary, 
    MIN(salary) OVER() as min_sal,
    MAX(salary) OVER() as max_sal
FROM employees;
        
SELECT MIN(salary), MAX(salary) FROM employees;

SELECT emp_no, department, salary, 
round(AVG(salary) OVER(PARTITION BY department)) AS dept_avg,
count(*) over(PARTITION BY department) AS dept_count,
round(AVG(salary) OVER()) AS company_avg,
count(*) over() AS company_count
FROM employees;

SELECT emp_no, department, salary,
SUM(salary) OVER(PARTITION BY department) as Total_dept_salary,
SUM(salary) OVER(PARTITION BY department order by salary desc) as Rolling_dept_salary
FROM employees;

SELECT emp_no, department, salary,
MIN(salary) OVER(PARTITION BY department order by salary desc) as min_dept_salary
FROM employees;

SELECT emp_no, department, salary,
Rank() OVER(PARTITION BY department order by salary desc),
Rank() OVER(order by salary desc)
FROM employees;

SELECT emp_no, department, salary,
Row_number() OVER(PARTITION BY department order by salary desc),
Row_number() OVER(order by salary desc),
Row_number() OVER()
FROM employees;

SELECT emp_no, department, salary,
Row_number() OVER(PARTITION BY department order by salary desc),
Rank() OVER(PARTITION BY department order by salary desc)
FROM employees;

SELECT 
    emp_no, 
    department, 
    salary,
    ROW_NUMBER() OVER(PARTITION BY department ORDER BY SALARY DESC) as dept_row_number,
    RANK() OVER(PARTITION BY department ORDER BY SALARY DESC) as dept_salary_rank,
    RANK() OVER(ORDER BY salary DESC) as overall_rank,
    DENSE_RANK() OVER(ORDER BY salary DESC) as overall_dense_rank,
    ROW_NUMBER() OVER(ORDER BY salary DESC) as overall_num
FROM employees ORDER BY overall_rank;

SELECT 
    emp_no, 
    department, 
    salary,
    FIRST_VALUE(emp_no) OVER(PARTITION BY department ORDER BY salary DESC) as highest_paid_dept,
    FIRST_VALUE(emp_no) OVER(ORDER BY salary DESC) as highest_paid_overall
FROM employees;
