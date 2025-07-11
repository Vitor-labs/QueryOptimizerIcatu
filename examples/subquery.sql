-- example_queries/subquery.sql
SELECT 
    e.employee_id,
    e.first_name,
    e.last_name,
    e.salary,
    e.department_id
FROM employees e
WHERE e.salary > (
    SELECT AVG(salary) 
    FROM employees 
    WHERE department_id = e.department_id
)
AND e.department_id IN (
    SELECT department_id 
    FROM departments 
    WHERE location_id IN (1700, 1800, 2400)
)
ORDER BY e.salary DESC;
