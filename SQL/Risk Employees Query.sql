--Risk Employees--

SELECT DISTINCT
	right (PRPMS.PREN, 6) "EmployeeID",
	PRPMS.PRCKNM "Name",
	PRPMS.PRTITL "Title",
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
	PRPMS.PRL01 = '001' AND PRPMS.PRL02 = 'RSK' AND PRPMS.PRTEDH = '0'

ORDER BY PRPMS.PRCKNM ASC

