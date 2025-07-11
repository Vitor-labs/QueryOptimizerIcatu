-- example_queries/aggregation.sql
SELECT 
    d.department_name,
    COUNT(*) as employee_count,
    AVG(e.salary) as avg_salary,
    MIN(e.salary) as min_salary,
    MAX(e.salary) as max_salary,
    SUM(e.salary) as total_salary
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
WHERE e.status = 'ACTIVE'
    AND e.hire_date >= '2019-01-01'
GROUP BY d.department_id, d.department_name
HAVING COUNT(*) >= 5
ORDER BY avg_salary DESC;
