cec_config = {
    "form_type": "CEC",
    "fields": {
        "Submission Date":             {"pattern": r"Submission Date\s*:\s*(\d{2}/\d{2}/\d{4})"},
        "Head of Household Name":      {"pattern": r"Head of Household Name\s*:\s*([A-Za-z ,]+)"},
        "Address":                     {"pattern": r"Address\s*:\s*([A-Za-z0-9,\s]+CA\s*\d{5})"},
        "Phone Number":                {"pattern": r"Phone Number\s*:\s*(\(\d{3}\)\s*\d{3}-\d{4})"},
        "Email":                       {"pattern": r"Email\s*:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"},
        # Allow any hyphen-like character between Medi and Cal
        "Medi-Cal Case Number":        {"pattern": r"Medi[\-\u2010\u2011\u2012\u2013\u2014]Cal Case Number\s*:\s*([A-Za-z0-9]+)"},
        # Capture the entire "2 (2 adults, 2 children)"
        "Total Household Members":     {"pattern": r"Total Household Members\s*:\s*(\d+\s*\(.+?\))"},
        "Adults":                      {"pattern": r"Adults?\s*:\s*(.+)"},
        "Children":                    {"pattern": r"[\u2022●*\-]?\s*Child(?:ren)?\s*:\s*(.+)"},
        "Children Coverage":           {"pattern": r"Children Coverage\s*:\s*(.+)"},
        "Determination Date":          {"pattern": r"Determination Date\s*:\s*(\d{2}/\d{2}/\d{4})"},
        "Annual Redetermination Date": {"pattern": r"Annual Redetermination Date\s*:\s*(\d{2}/\d{2}/\d{4})"},
        "Adverse Reported On":         {"pattern": r"Reported On\s*:\s*(\d{2}/\d{2}/\d{4})"},
        "Adverse Change":              {"pattern": r"Change\s*:\s*(.+?)(?=\n|$)"},
        "Under age 19":                {"pattern": r"Under age 19\s*:\s*(Yes|No)"},
        "Not receiving minor consent services": {
            "pattern": r"Not receiving minor consent services\s*:\s*(Yes|No)"
        },
        # More permissive around hyphens and spacing
        "Eligible for no-SOC Medi-Cal prior to change": {
            "pattern": r"Eligible for no.*?Medi[-\u2010\u2011]Cal prior to change\s*:\s*(Yes|No)"
        },
        # Allow an optional "(Aid Code ...)" before the Yes/No
        "CEC Granted": {
            "pattern": r"CEC Granted\s*:\s*(?:\([^)]*\)\s*)?(Yes|No)"
        },
        "CEC Period":                  {"pattern": r"Begin\s*:\s*(\d{2}/\d{2}/\d{4})\s*End\s*:\s*(\d{2}/\d{2}/\d{4})"}
    }
}

# Section grouping remains the same
sections = {
    "Applicant Identification": [
        "Submission Date", "Head of Household Name", "Address",
        "Phone Number", "Email", "Medi-Cal Case Number"
    ],
    "Household Composition": [
        "Total Household Members", "Adults", "Children"
    ],
    "Current Medi-Cal Coverage": [
        "Children Coverage", "Determination Date", "Annual Redetermination Date"
    ],
    "Adverse Change Report": [
        "Adverse Reported On", "Adverse Change"
    ],
    "Eligibility Determination": [
        "Under age 19",
        "Not receiving minor consent services",
        "Eligible for no-SOC Medi-Cal prior to change",
        "CEC Granted"
    ],
    "CEC Period": [
        "CEC Period"
    ]
}