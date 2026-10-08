-- 04_window_functions.sql
-- Window functions compute an aggregate WITHOUT collapsing rows.
-- COUNT(*) OVER (PARTITION BY dept_code) puts the dept headcount on
-- every employee row - useful for "you are 1 of N in Ops" reports.
--
-- ROW_NUMBER() ranks tenure inside each department. Interviewers ask
-- for this when they say "latest hire per dept" or "top N per group."

SELECT
    e.name,
    e.dept_code,
    e.title,
    e.hire_date,
    COUNT(*) OVER (PARTITION BY e.dept_code) AS dept_headcount,
    ROW_NUMBER() OVER (
        PARTITION BY e.dept_code
        ORDER BY e.hire_date
    ) AS tenure_rank_in_dept
FROM employees AS e
WHERE e.status = 'Active'
ORDER BY e.dept_code, tenure_rank_in_dept;
