-- 06_exception_report.sql
-- Terminated people who still have a supervisor on file.
-- Ops / HR often want this as a cleanup list after a termination.

SELECT
    e.employee_id,
    e.name AS terminated_employee,
    e.title,
    e.dept_code,
    s.name AS still_reports_to
FROM employees AS e
LEFT JOIN employees AS s
    ON e.supervisor_id = s.employee_id
WHERE e.status = 'Terminated'
ORDER BY e.name;
