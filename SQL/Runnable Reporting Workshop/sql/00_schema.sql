-- Runnable Reporting Workshop
-- SQLite schema that stands in for the Infinium employee / supervisor tables
-- used in Ops Org Chart Query.sql - without needing SSMS or production access.
--
-- Why a tiny schema instead of the real PRPMS/PRPSP names:
--   Reviewers cannot connect to psa.dbo. This file they CAN run.
--   The join pattern is the same: employee row + another employee row
--   for the supervisor (a self-join).

DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    employee_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    dept_code     TEXT    NOT NULL,  -- like PRL03
    title         TEXT    NOT NULL,  -- like PRTITL
    job_family    TEXT    NOT NULL,  -- like PRSEC (DRV, OFC, TEC, ...)
    status        TEXT    NOT NULL,  -- Active / Terminated  (PRTEDH analog)
    hire_date     TEXT    NOT NULL,  -- ISO date so it sorts
    supervisor_id INTEGER NULL REFERENCES employees(employee_id)
);
