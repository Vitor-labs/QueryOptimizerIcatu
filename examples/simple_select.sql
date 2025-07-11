-- example_queries/simple_select.sql
SELECT 
    employee_id,
    first_name,
    last_name,
    salary,
    department_id
FROM employees
WHERE salary > 50000
    AND salary > 40000 -- added redundancy for testing purpose
    AND salary > 30000 -- added redundancy for testing purpose
    AND department_id IN (10, 20, 30)
ORDER BY salary DESC;
