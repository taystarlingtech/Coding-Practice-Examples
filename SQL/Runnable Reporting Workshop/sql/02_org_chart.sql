-- 02_org_chart.sql
-- Same idea as Ops Org Chart Query.sql:
--   employee master LEFT JOIN employee master (as supervisor).
-- Differences from production:
--   * Readable column names instead of PREN / PRCKNM / PRPSP
--   * No NOLOCK (SQLite is a file; that hint is a SQL Server locking choice)
--   * job_family <> 'DRV' stands in for PRSEC <> 'DRV'

SELECT
    e.employee_id,
    e.name,
    e.dept_code AS dept,
    e.title,
    s.name AS reports_to
FROM employees AS e
LEFT JOIN employees AS s
    ON e.supervisor_id = s.employee_id
WHERE e.status = 'Active'
  AND e.job_family <> 'DRV'
ORDER BY e.name;
