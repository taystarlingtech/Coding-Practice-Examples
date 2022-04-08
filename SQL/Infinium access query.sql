SELECT 
PRPMS.PRER "Company"
	, right (PRPMS.PREN, 6) "EE ID"
	, PRPMS.PRCNM "Name"
	, PRPMS.PRL01 "Company"
	, PRPMS.PRL02 "SBU"
	, PRPMS.PRL03 "Dept"
	, CONCAT(RTRIM(PRPMS.PRL01), '-', RTRIM(PRPMS.PRL02),'-', RTRIM(PRPMS.PRL03), '-', RTRIM(PRPMS.PRL04)) "Company-SBU-Dept-Loc"
	, PRPMS.PRPOS "Position Number"
	, PRPMS.PRTITL "Title"
	, PRPMS.PRSEC "Security"
	, PEPOG.OGPLVL "Org Level"
	, PRPMS.PREML1 "Email"
	, CASE
		WHEN PRPMS.PRDHAH = 0 THEN PRPMS.PRDOHE ELSE PRPMS.PRDHAE
	END AS "Most Recent DOH"




	FROM psa.dbo.SMFD35_HRDBFA_PRPMS          PRPMS (nolock) --Employee Master
		LEFT JOIN psa.dbo.SMFD35_HRDBFA_PEPOG PEPOG --Position Manager
			ON PRPMS.PRER = pepog.oger
			and prpms.prpos = pepog.ogpos
		LEFT JOIN psa.dbo.SMFD35_HRDBFA_PRPSP PRPSP (nolock) --Supervisor Table
			ON PRPMS.PRER = PRPSP.SPER
			AND PRPMS.PREN = PRPSP.SPEN
		LEFT JOIN psa.dbo.SMFD35_HRDBFA_PRPMS PRPMS_1 (nolock)--Employee Master joined on supervisor table --details for supervisors
			ON PRPSP.SPSPER = PRPMS_1.PRER

			AND PRPSP.SPSPEN = PRPMS_1.PREN
	WHERE IN PRPMS.PRFNM ( 'ASHLEY', ')
	--WHERE PRPMS.PRFNM = 'Ashley' AND PRPMS.PRLNM = 'ATWELL'