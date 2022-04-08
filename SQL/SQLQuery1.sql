SELECT
PRPMS.PRER "Company",
	right (PRPMS.PREN, 6) "EE ID",
	PRPMS.PRCNM "Complete Name",
	PRPMS.PRL01 "Company",
	PRPMS.PRL02 "SBU",
	PRPMS.PRL03 "Dept",
	CONCAT(RTRIM(PRPMS.PRL01), '-', RTRIM(PRPMS.PRL02),'-', RTRIM(PRPMS.PRL03), '-', RTRIM(PRPMS.PRL04)) "Company-SBU-Dept-Loc",
	PRPMS.PRPOS "Position Number",
	PRPMS.PRTITL "Title",
	PRPMS.PRSEC "Security",
	PEPOG.OGPLVL "Org Level",
	PRPMS.PREML1 "Email",
	CASE
		WHEN PRPMS.PRDHAH = 0 THEN PRPMS.PRDOHE
		ELSE PRPMS.PRDHAE
	END AS "Most Recent DOH",
	PRPMS.PRTEDE "Term Date",
	PRPMS_1.PRCKNM "Supervisor",
	PRPSP.SPSPNM "First Supervisor name",
	right (PRPMS_1.PREN, 6) "First Supervisor ID",
	PRPMS_1.PRTITL "First Supervisor title",
	PRPMS_1.PREML1 "First Supervisor Email"

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
	PRPMS.PRER IN ('051','001', '065', '044') --Companies US Xpress, US Xpress Enterprises, Total Transportation, or Xpress Tech
	AND PRPMS.PRTEDH = 0  --Term date PRTDH is blank
	AND PRPMS.PRSEC <> 'DRV' --Not Drivers

ORDER BY 17