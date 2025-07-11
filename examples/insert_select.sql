-- example_queries/insert_select.sql
INSERT INTO employee_audit (
    employee_id, 
    action_type, 
    action_date, 
    old_salary, 
    new_salary, 
    performed_by
)
SELECT 
    e.employee_id,
    'SALARY_INCREASE',
    CURRENT_TIMESTAMP,
    e.salary,
    e.salary * 1.03,
    'SYSTEM'
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
WHERE e.hire_date < DATE('now', '-2 years')
    AND e.last_promotion_date < DATE('now', '-1 year')
    AND d.budget_utilization < 0.85;
