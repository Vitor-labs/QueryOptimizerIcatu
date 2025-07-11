-- example_queries/basic_join.sql
SELECT 
    e.first_name,
    e.last_name,
    d.department_name,
    e.salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.hire_date >= '2020-01-01'
ORDER BY e.salary DESC;
