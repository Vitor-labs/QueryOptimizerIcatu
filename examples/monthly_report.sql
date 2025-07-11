-- example_queries/monthly_report.sql
SELECT 
    d.department_name,
    DATE_TRUNC('month', e.hire_date) as hire_month,
    COUNT(*) as new_hires,
    AVG(e.salary) as avg_salary,
    MIN(e.salary) as min_salary,
    MAX(e.salary) as max_salary,
    SUM(e.salary) as total_salary_cost,
    LAG(COUNT(*), 1) OVER (
        PARTITION BY d.department_id 
        ORDER BY DATE_TRUNC('month', e.hire_date)
    ) as prev_month_hires,
    COUNT(*) - LAG(COUNT(*), 1) OVER (
        PARTITION BY d.department_id 
        ORDER BY DATE_TRUNC('month', e.hire_date)
    ) as hire_change
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
WHERE e.hire_date >= DATE('now', '-2 years')
GROUP BY d.department_id, d.department_name, DATE_TRUNC('month', e.hire_date)
ORDER BY d.department_name, hire_month DESC;
