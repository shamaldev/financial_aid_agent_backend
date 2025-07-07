pace_static_patterns = {
    "Submission Date":            r"Submission Date\s*:\s*(\d{2}/\d{2}/\d{4})",
    "Applicant Name":             r"Applicant Name\s*:\s*([A-Za-z ,.'-]+)",
    "Date of Birth":              r"Date of Birth\s*:\s*(\d{2}/\d{2}/\d{4})",
    "Age":                        r"Age\s*:\s*(\d+)", 
    "Address":                    r"Address\s*:\s*([A-Za-z0-9 ,.'-]+ CA \d{5})",
    "Phone Number":               r"Phone Number\s*:\s*(\(\d{3}\)\s*\d{3}[-–—‐]\d{4})",
    "Medi-Cal Case Number":       r"Medi-Cal Case Number\s*:\s*(\d+)",
    "Medicare Number":            r"Medicare Number\s*:\s*([\w-]+)"
}
 
eligibility_patterns = {
    "Age (55+)":                  r"Age \(55\+\)\s*:\s*(Yes|No)",
    "Lives in PACE Service Area": r"Lives in PACE Service Area\s*:\s*(.+?)\s*(Yes|No|⬜|☑)",
    "Nursing Home Level of Care": r"Eligible for Nursing Home Level of Care\s*:\s*(Yes|No)",
    "Community Living":           r"Able to Live Safely in Community\s*:\s*(Yes|No)",
    "MAGI Aid Code":              r"Medi-Cal Aid Code \(MAGI\)\s*:\s*(.+?)\s*(Yes|No|⬜|☑)",
    "Dual Eligible":              r"Dual Eligible \(Medicare & Medi-Cal\)\s*:\s*(Yes|No)"
}

spousal_patterns = {
    "Spouse Name":      r"Spouse Name\s*:\s*(N/A|[A-Za-z ]+)",
    "Spouse Residence": r"Spouse Community Residence\s*:\s*(N/A|[A-Za-z0-9 ,.'-]+)",
    "MFBU Status":                r"MFBU Status\s*:\s*(.+)",
    "Resource Transfer":          r"Resource Transfer\s*:\s*(.+)"
}
