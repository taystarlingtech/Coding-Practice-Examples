-- 03_headcount_cte.sql
-- CTEs (WITH ...) show up constantly in interviews and in Report Builder
-- SQL. This one is the "count actives by department, then keep depts
-- with at least 2 people" pattern - a filter on an aggregate.

WITH active_by_dept AS (
    SELECT
        dept_code,
        COUNT(*) AS active_count
    FROM employees
    WHERE status = 'Active'
    GROUP BY dept_code
)
SELECT
    dept_code,
    active_count
FROM active_by_dept
WHERE active_count >= 2
ORDER BY active_count DESC, dept_code;
