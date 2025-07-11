-- example_queries/complex_analytics.sql
SELECT 
    e.department_id,
    EXTRACT(YEAR FROM e.hire_date) as hire_year,
    EXTRACT(QUARTER FROM e.hire_date) as hire_quarter,
    COUNT(*) as hires_count,
    AVG(e.salary) as avg_starting_salary,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.salary) as median_salary,
    SUM(COUNT(*)) OVER (
        PARTITION BY e.department_id 
        ORDER BY EXTRACT(YEAR FROM e.hire_date), EXTRACT(QUARTER FROM e.hire_date)
        ROWS UNBOUNDED PRECEDING
    ) as cumulative_hires
FROM employees e
WHERE e.hire_date >= '2015-01-01'
    AND e.department_id IS NOT NULL
GROUP BY 
    e.department_id, 
    EXTRACT(YEAR FROM e.hire_date), 
    EXTRACT(QUARTER FROM e.hire_date)
HAVING COUNT(*) >= 2
ORDER BY 
    e.department_id, 
    hire_year, 
    hire_quarter;
