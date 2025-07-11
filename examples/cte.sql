-- example_queries/cte.sql
WITH department_stats AS (
    SELECT 
        department_id,
        COUNT(*) as emp_count,
        AVG(salary) as avg_salary,
        MAX(salary) as max_salary
    FROM employees
    WHERE status = 'ACTIVE'
    GROUP BY department_id
),
high_performing_depts AS (
    SELECT department_id
    FROM department_stats
    WHERE avg_salary > 60000 AND emp_count >= 10
)
SELECT 
    e.employee_id,
    e.first_name,
    e.last_name,
    e.salary,
    d.department_name,
    ds.avg_salary as dept_avg_salary,
    CASE 
        WHEN e.salary > ds.avg_salary * 1.2 THEN 'High Performer'
        WHEN e.salary > ds.avg_salary THEN 'Above Average'
        ELSE 'Below Average'
    END as performance_category
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
INNER JOIN department_stats ds ON e.department_id = ds.department_id
INNER JOIN high_performing_depts hpd ON e.department_id = hpd.department_id
WHERE e.hire_date >= '2020-01-01'
ORDER BY e.department_id, e.salary DESC;
