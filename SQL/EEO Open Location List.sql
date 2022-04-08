SELECT 
    ELER AS 'ER',
	ELLOCATION AS 'Location Code',
	(select CDDESC FROM PSA.dbo.SMFD35_HRDBFA_PRPCD PRPCD (nolock)
	WHERE CDTYPE = 'LOC'
	AND CDER = ELER
	AND ELLOCATION = CDFIVE) AS 'LOCATION DESCRIPTION',
	ELADDRESS As 'Address',
	ELADD2 As 'Address2',
	ELCITY As City,
	ELSTATE As 'State',
	ELZIP As 'Zip Code',
	ELCOUNTY As County,
	ELACTIVITY As 'Establishment Activity',
	SUBSTRING( ELFUT3, 1, 10 ) AS 'Start Date',
	SUBSTRING( ELFUT3, 11, 10 ) AS 'Stop Date',
	SUBSTRING( ELFUT3, 21, 1 ) AS 'Driver Training Allowed',
	SUBSTRING( ELFUT3, 22, 3 ) AS 'Location Type',
	SUBSTRING( ELFUT3, 25, 1 ) AS 'Driver Orientation',
	SUBSTRING( ELFUT3, 26, 3 ) AS 'Driver PST REQ',
	SUBSTRING( ELFUT3, 29, 4 ) AS 'Simulated Phone Number',
	ELTL1 As 'Future Use Phone Number',
	ELUDLP UNIT,
	ELFUT2 As NAICS,
	ELSIC As SIC,
	ELUNT As UnitCode
	
FROM 
       PSA.dbo.SMFD35_HRDBFA_PEPEL PEPEL (nolock)
WHERE ELER IN ('001', '051','044', '065')
AND SUBSTRING( ELFUT3, 11, 10 ) = '' --Stop Date is blank
	
	   
ORDER BY 
       2
