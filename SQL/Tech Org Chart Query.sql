-------- Tech Org Chart--------
SELECT DISTINCT
	right (PRPMS.PREN, 6) "EmployeeID",
	PRPMS.PRCKNM "Name",
	PRPMS.PRTITL "Title",
	PRPMS.PRL03 "Dept",
	PRPMS_1.PRCKNM "Reports_to"
FROM
	psa.dbo.SMFD35_HRDBFA_PRPMS PRPMS (nolock) --Employee Master
	LEFT JOIN psa.dbo.SMFD35_HRDBFA_PEPOG PEPOG --Position Manager
	ON PRPMS.PRER = pepog.oger and prpms.prpos = pepog.ogpos 
	LEFT JOIN psa.dbo.SMFD35_HRDBFA_PRPSP PRPSP (nolock) --Supervisor Table
	ON PRPMS.PRER = PRPSP.SPER
	AND PRPMS.PREN = PRPSP.SPEN
	LEFT JOIN psa.dbo.SMFD35_HRDBFA_PRPMS PRPMS_1 (nolock)--Employee Master joined on supervisor table --details for supervisors
	ON PRPSP.SPSPER = PRPMS_1.PRER
	AND PRPSP.SPSPEN = PRPMS_1.PREN

WHERE
	PRPMS.PRER IN ('044') -- Xpress Tech
	AND PRPMS.PRTEDH = '0' --not terminated
	AND PRPMS.PRL03 = 'ADM' 
	AND PRPMS.PRSEC <> 'DRV' --Not Drivers
	--and PRPMS.PRLNM = 'Anthony'
	-- and PRPMS.PRCKNM like 'Anthony%'

order by PRPMS.PRCKNM asc