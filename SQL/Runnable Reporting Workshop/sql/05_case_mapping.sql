-- 05_case_and_open_list.sql
-- CASE is the SQL version of the role-mapping logic in Report Builder
-- Query v2. Here we turn dept_code into a display name.
--
-- The second result-style query lists "gaps": active supervisors who
-- still have a terminated direct report in their tree. That is the
-- same *kind* of question as EEO Open Location List.sql - a filtered
-- exception report, not a full dump.

SELECT
    e.employee_id,
    e.name,
    e.dept_code,
    CASE e.dept_code
        WHEN 'EXE' THEN 'Executive'
        WHEN 'OPS' THEN 'Operations'
        WHEN 'TEC' THEN 'Technology'
        WHEN 'HR'  THEN 'Human Resources'
        ELSE 'Unmapped'
    END AS dept_name,
    e.title,
    e.status
FROM employees AS e
ORDER BY e.dept_code, e.name;
