Select * from customers
select * from orders

SELECT * FROM orders 
WHERE customer_id = (SELECT id FROM customers WHERE last_name = 'George');

Select b.*, a.* from customers a 
right join orders b
on a.id = b.customer_id;





