--------Dedicated--------

SELECT RIGHT (PRPMS.PREN, 6) "Employee ID"
	, PRPMS.PRCKNM "Employee Name"
	, PRPMS_1.PRCKNM "Supervisor"
	, PRPMS_1.PREML1 "Supervisor Email"
	, PRPMS.PRL02 "Strategic Business Unit"
	, PRPMS.PRL03 "Department"
	, PMEMPLP.EMDCG "Driver Control Group"
	, PRPMS.PRL04 "Infinium Location"
	, PMEMPLP.EMTE "QTOPS Terminal"

	FROM psa.dbo.SMFD35_XPSFILE_PMEMPLP       PMEMPLP(NOLOCK) --Driver Info
		LEFT JOIN psa.dbo.smfd35_hrdbfa_prpms PRPMS ON CONCAT(0, PMEMPLP.EMCM) = PRPMS.PRER --Employee Table
			AND PMEMPLP.EMPID = PRPMS.PREN
		LEFT JOIN psa.dbo.SMFD35_HRDBFA_PRPSP PRPSP (NOLOCK) --Supervisor Table
			ON PRPMS.PRER = PRPSP.SPER
			AND PRPMS.PREN = PRPSP.SPEN
		LEFT JOIN psa.dbo.SMFD35_HRDBFA_PRPMS PRPMS_1 (NOLOCK)--Employee Master joined on supervisor table
			ON PRPSP.SPSPER = PRPMS_1.PRER
			AND PRPSP.SPSPEN = PRPMS_1.PREN

WHERE
	-- Clean Data: (PRL02 in (‘DED’) AND EMDCG LIKE ‘D%’) AND PRL04 = EMTE
	--We need to identify any drivers where the PRL02(SBU) and EMDCG(drv control group) are not in sync or the locations(QTOPS) don’t match.
	--This should be three separate reports for the three driver types Variant, Dedicated and OCR. Only active, no independent contractors.

	(
		PRPMS.PRER IN ('051','001') --Companies US Xpress, US Xpress Enterprises,
		AND PRPMS.PRTEDH = 0 --Term date is blank (Not Terminated)
		AND PRPMS.PRSEC = 'DRV' --Drivers
		AND PMEMPLP.EMJBCD != 'OWN' --Non W2 Drivers (Not Contractors)
	)

	AND (
			(
				PRPMS.PRL02 IN('DED') --in SBU
				AND (PMEMPLP.EMDCG Not LIKE 'D%')--not in Control Group
			)

			OR (
				PRPMS.PRL02 NOT IN('DED') --Not in SBU
				AND (PMEMPLP.EMDCG LIKE 'D%') --not in Control Group
			)

			OR (
				(PRPMS.PRL02 IN('DED') OR PMEMPLP.EMDCG LIKE 'D%') --in SBU or Control Group
				AND PRPMS.PRL04 != EMTE --Infinium location not matching QTOPs location
			)
		)

ORDER BY PRPMS.PRCKNM ASC