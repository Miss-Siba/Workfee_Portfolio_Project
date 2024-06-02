-- MySQL Test server for the project.
CREATE DATABASE IF NOT EXISTS workfee_db;
CREATE USER IF NOT EXISTS 'workfee_dev'@'localhost' IDENTIFIED BY 'workfee_dev_pwd';
GRANT ALL PRIVILEGES ON workfee_dev_db . * TO 'workfee_dev'@'localhost';
GRANT SELECT ON performance_schema . * TO 'workfee_dev'@'localhost';
