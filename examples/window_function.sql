-- example_queries/window_function.sql
SELECT 
    employee_id,
    first_name,
    last_name,
    department_id,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank,
    RANK() OVER (ORDER BY salary DESC) as overall_salary_rank,
    LAG(salary, 1) OVER (PARTITION BY department_id ORDER BY hire_date) as prev_hire_salary,
    AVG(salary) OVER (PARTITION BY department_id) as dept_avg_salary,
    salary - AVG(salary) OVER (PARTITION BY department_id) as salary_diff_from_avg
FROM employees
WHERE department_id IS NOT NULL
ORDER BY department_id, salary DESC;
