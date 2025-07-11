-- example_queries/unoptimized.sql
SELECT DISTINCT
    e1.employee_id,
    e1.first_name,
    e1.last_name,
    e1.salary,
    (SELECT department_name FROM departments WHERE department_id = e1.department_id) as dept_name,
    (SELECT COUNT(*) FROM employees e2 WHERE e2.department_id = e1.department_id) as dept_count,
    (SELECT AVG(salary) FROM employees e3 WHERE e3.department_id = e1.department_id) as dept_avg_salary
FROM employees e1
WHERE e1.employee_id IN (
    SELECT employee_id 
    FROM employees 
    WHERE salary > (
        SELECT AVG(salary) * 1.1 
        FROM employees
    )
)
AND EXISTS (
    SELECT 1 
    FROM departments d 
    WHERE d.department_id = e1.department_id 
    AND d.location_id IN (1700, 1800)
)
ORDER BY e1.salary DESC;
