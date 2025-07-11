-- example_queries/multiple_joins.sql
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name as full_name,
    d.department_name,
    l.city,
    l.state_province,
    c.country_name,
    r.region_name,
    e.salary,
    j.job_title
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
INNER JOIN locations l ON d.location_id = l.location_id
INNER JOIN countries c ON l.country_id = c.country_id
INNER JOIN regions r ON c.region_id = r.region_id
INNER JOIN jobs j ON e.job_id = j.job_id
WHERE e.salary BETWEEN 40000 AND 100000
    AND r.region_name IN ('Europe', 'Americas')
    AND e.hire_date >= '2018-01-01'
ORDER BY r.region_name, c.country_name, l.city, e.salary DESC;
