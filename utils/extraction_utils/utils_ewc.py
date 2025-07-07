# Config-driven field definitions
ewc_config = {
    "form_type": "EWC",
    "fields": {
        "Submission Date":            {"method": "regex", "pattern": r"Submission Date\s*:\s*(\d{2}/\d{2}/\d{4})"},
        "Full Name":                  {"method": "regex", "pattern": r"Full Name\s*:\s*([A-Za-z ]+)"},
        "Date of Birth":              {"method": "regex", "pattern": r"Date of Birth\s*:\s*(\d{2}/\d{2}/\d{4})"},
        "Age":                        {"method": "regex", "pattern": r"Age\s*:\s*(\d+)"},
        "Address":                    {"method": "regex", "pattern": r"Address\s*:\s*([A-Za-z0-9, ]+ CA \d{5})"},
        "Phone Number":               {"method": "regex", "pattern": r"Phone Number\s*:\s*(\(\d{3}\) \d{3}-\d{4})"},
        "Email":                      {"method": "regex", "pattern": r"Email\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"},
        "California Resident":        {"method": "regex", "pattern": r"California Resident\s*:\s*(\w+)"},
        "Health Insurance Status":    {"method": "regex", "pattern": r"Health Insurance Status\s*:\s*(.+)"},
        "Monthly Household Income":   {"method": "regex", "pattern": r"Monthly Household Income\s*:\s*\$([0-9,]+)"},
        "Household Size":             {"method": "regex", "pattern": r"Household Size\s*:\s*(\d+)"},
        "Income as % of FPL":         {"method": "regex", "pattern": r"Income as \% of FPL\s*:\s*(\d+\%)"},
        "Clinical Breast Exam & Mammogram": {
            "method": "regex",
            "pattern": r"Clinical Breast Exam & Mammogram \(Age 40\+\)\s*:\s*(\w+)"
        },
        "Pap Test":                   {"method": "regex", "pattern": r"Pap Test \(Age 21\+\)\s*:\s*(\w+)"},
        "HPV Test":                   {"method": "regex", "pattern": r"HPV Test \(with Pap\)\s*:\s*(\w+)"},
        "Referred by":                {"method": "regex", "pattern": r"Referred by\s*:\s*([A-Za-z ]+)"},
        "Referral Method":            {"method": "regex", "pattern": r"Referral Method\s*:\s*(.+?)(?=\r?\n|$)"}
    }
}

sections = {
    "Applicant Info": [
        "Submission Date", "Full Name", "Date of Birth", "Age", "Address",
        "Phone Number", "Email", "California Resident"
    ],
    "Income & Household": [
        "Monthly Household Income", "Household Size", "Income as % of FPL"
    ],
    "Health Insurance": [
        "Health Insurance Status"
    ],
    "Screening Services": [
        "Clinical Breast Exam & Mammogram", "Pap Test", "HPV Test"
    ],
    "Referral": [
        "Referred by", "Referral Method"
    ]
}