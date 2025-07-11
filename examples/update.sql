-- example_queries/update.sql
UPDATE employees 
SET salary = salary * 1.05,
    last_updated = CURRENT_TIMESTAMP
WHERE department_id IN (
    SELECT department_id 
    FROM departments 
    WHERE location_id IN (1700, 1800)
)
AND performance_rating >= 4
AND last_salary_review < DATE('now', '-1 year');
