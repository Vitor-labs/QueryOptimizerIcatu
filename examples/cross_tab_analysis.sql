-- example_queries/cross_tab_analysis.sql
SELECT 
    job_title,
    SUM(CASE WHEN department_name = 'Sales' THEN 1 ELSE 0 END) as sales_count,
    SUM(CASE WHEN department_name = 'Marketing' THEN 1 ELSE 0 END) as marketing_count,
    SUM(CASE WHEN department_name = 'IT' THEN 1 ELSE 0 END) as it_count,
    SUM(CASE WHEN department_name = 'Finance' THEN 1 ELSE 0 END) as finance_count,
    SUM(CASE WHEN department_name = 'HR' THEN 1 ELSE 0 END) as hr_count,
    COUNT(*) as total_count,
    AVG(salary) as avg_salary_by_job
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
INNER JOIN jobs j ON e.job_id = j.job_id
WHERE e.status = 'ACTIVE'
GROUP BY j.job_id, job_title
HAVING COUNT(*) >= 5
ORDER BY total_count DESC, avg_salary_by_job DESC;
