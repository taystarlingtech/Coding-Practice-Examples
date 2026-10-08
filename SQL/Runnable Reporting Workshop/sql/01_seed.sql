-- Sample HR rows. Hierarchy:
--   Alex (COO)
--     Jordan (Ops Director) -> Casey, Morgan, Drew (terminated driver), Chris (terminated)
--     Sam (Tech Director)   -> Quinn, Avery, Jamie
--     Riley (HR Manager)    -> Taylor

INSERT INTO employees (employee_id, name, dept_code, title, job_family, status, hire_date, supervisor_id) VALUES
(1,  'Alex Rivera',   'EXE', 'Chief Operating Officer', 'OFC', 'Active',     '2014-03-01', NULL),
(2,  'Jordan Blake',  'OPS', 'Ops Director',            'OFC', 'Active',     '2016-07-12', 1),
(3,  'Sam Patel',     'TEC', 'Tech Director',           'TEC', 'Active',     '2017-01-09', 1),
(4,  'Riley Chen',    'HR',  'HR Manager',              'OFC', 'Active',     '2018-04-22', 1),
(5,  'Casey Nguyen',  'OPS', 'Dispatcher',              'OFC', 'Active',     '2019-11-04', 2),
(6,  'Morgan Lee',    'OPS', 'Dispatcher',              'OFC', 'Active',     '2020-02-17', 2),
(7,  'Quinn Adams',   'TEC', 'Systems Analyst',         'TEC', 'Active',     '2019-08-30', 3),
(8,  'Avery Brooks',  'TEC', 'Systems Analyst',         'TEC', 'Active',     '2021-05-03', 3),
(9,  'Jamie Ortiz',   'TEC', 'Help Desk Technician',    'TEC', 'Active',     '2022-09-19', 3),
(10, 'Taylor Shaw',   'HR',  'HR Coordinator',          'OFC', 'Active',     '2023-01-16', 4),
(11, 'Drew Kim',      'OPS', 'Driver',                  'DRV', 'Terminated', '2015-06-01', 2),
(12, 'Chris Vale',    'OPS', 'Dispatcher',              'OFC', 'Terminated', '2018-10-10', 2);
