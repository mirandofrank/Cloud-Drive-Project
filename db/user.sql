CREATE DATABASE PERSON;
USE PERSON;

CREATE TABLE User_info (
	id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(50) NOT NULL,
    fname VARCHAR(30) NOT NULL,
    lname VARCHAR(30) NOT NULL,
    PRIMARY KEY(id)
);

desc User_info;
select * from User_info;


set SQL_SAFE_UPDATES = 0;
delete from User_info where username = "project454";
set SQL_SAFE_UPDATES = 1;
drop schema PERSON

