Use mynewproject;

Select reverse(upper('Why does my cat looks at me with such hatred?')) from dual;

Select distinct concat(author_fname,' ', author_lname) athor_name from books;

Select * from books order by author_lname desc, released_year asc;
Select * from books limit 2,5;

Select * from books where title like '%stories%';
Select * from books where author_fname like '_a_';

Select * from books order by pages desc limit 1;

Select count(distinct released_year) from books;

SELECT COUNT(*) FROM books WHERE title LIKE '%the%';
Select author_lname, count(author_lname) from books GROUP BY author_lname order by 2 desc;

select title, pages from books where pages = (Select max(pages) from books);

SELECT author_fname, author_lname, COUNT(*) 
FROM books 
GROUP BY author_lname, author_fname;


SELECT 
        author_lname, 
        author_fname,
        COUNT(*) as books_written, 
        MAX(released_year) AS latest_release,
        MIN(released_year)  AS earliest_release,
        SUM(pages) AS Total_pages,
        round(AVG(pages),0) AS Avg_pages
FROM books GROUP BY author_lname, author_fname;

CREATE TABLE people (
        name VARCHAR(100),
    birthdate DATE,
    birthtime TIME,
    birthdt DATETIME
);
 
INSERT INTO people (name, birthdate, birthtime, birthdt)
VALUES ('Elton', '2000-12-25', '11:00:00', '2000-12-25 11:00:00');
 
INSERT INTO people (name, birthdate, birthtime, birthdt)
VALUES ('Lulu', '1985-04-11', '9:45:10', '1985-04-11 9:45:10');
 
INSERT INTO people (name, birthdate, birthtime, birthdt)
VALUES ('Juan', '2020-08-15', '23:59:00', '2020-08-15 23:59:00');

INSERT INTO people (name, birthdate, birthtime, birthdt)
VALUES ('Hazel', CURDATE(), CURTIME(), NOW());

Select day(birthdate) from people;

SELECT birthdate, DATE_FORMAT(birthdate, '%a %b %D') FROM people;
 
SELECT birthdt, DATE_FORMAT(birthdt, '%H:%i') FROM people;
 
SELECT birthdt, DATE_FORMAT(birthdt, 'BORN ON: %r') FROM people;

Select concat(round(datediff(curdate(), birthdate)/360)," years") from people;

CREATE TABLE captions (
  text VARCHAR(150),
  created_at TIMESTAMP default CURRENT_TIMESTAMP,
  updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

Insert captions(text) values("New_here")
Select * from captions
Update captions set text = "Old_now";

SELECT * FROM books WHERE title NOT LIKE '%e%';

SELECT * FROM books WHERE released_year > 2005;
 
SELECT * FROM books WHERE pages > 500;

Select * from books where released_year not between 2001 and 2004 order by released_year;

SELECT * FROM people WHERE birthtime BETWEEN CAST('10:00:00' AS TIME) AND CAST('16:00:00' AS TIME);

SELECT title, released_year FROM books WHERE released_year >= 2000 AND released_year % 2 = 1;


SELECT author_fname, author_lname,
 CASE
        WHEN COUNT(*) = 1 THEN '1 book'
        ELSE CONCAT(COUNT(*), ' books')
 END AS count
FROM books
WHERE author_lname IS NOT NULL
GROUP BY author_fname, author_lname;


CREATE TABLE palindromes (
  word VARCHAR(100) CHECK(REVERSE(word) = word)
);

CREATE TABLE palindromes (
  word VARCHAR(100),
  CONSTRAINT word_is_palindrome CHECK(REVERSE(word) = word)
);

CREATE TABLE companies (
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    CONSTRAINT name_address UNIQUE (name , address)
);
 
CREATE TABLE houses (
  purchase_price INT NOT NULL,
  sale_price INT NOT NULL,
  CONSTRAINT sprice_gt_pprice CHECK(sale_price >= purchase_price)
);

