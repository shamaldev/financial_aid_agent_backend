calworks_static_patterns = {
    "Submission Date":              r"Submission Date\s*:\s*(\d{2}/\d{2}/\d{4})",
    "Case Number":                  r"CalWORKs Case Number\s*:\s*(\w+)",
    #"Begin Aid Date":               r"CalWORKs Beginning Date of Aid\s*:\s*(\d{2}/\d{2}/\d{4})",
    "Begin Aid Date":               r"CalWORKs Beginning Date of Aid\s*:\s*([\w/]+)",
    "Full Name":                    r"Full Name\s*:\s*([A-Za-z ,.'-]+)",
    "Phone":                        r"Phone Number\s*:\s*([^\n]+)",
    "Address":                      r"Address\s*:\s*([A-Za-z0-9 ,.'-]+ CA \d{5})",
    "Household Composition":        r"Household Composition\s*:\s*([0-9]+ adults,\s*[0-9]+ child(?:ren)?)",
    "Two-Parent Household":         r"Two-Parent Household\s*:\s*(Yes|No|N/A)",
    "Currently Receiving CalWORKs": r"Currently Receiving CalWORKs\s*:\s*(Yes|No|N/A)",
    "Former Client":                r"Former Client\s*:\s*(Yes|No|N/A)",
    "Last Received":                r"Last Received \(previous period\)\s*:\s*(.+)",
    "Reason Former Status":         r"Reason for Former Status\s*:\s*(.+)",
    "Sanction Status":              r"Sanction Status \(Pre-Oct 1, 2019\)\s*:\s*(Yes|No|N/A)",
    "Intend to Cure Sanction":      r"Intend to Cure Sanction \(if applicable\)\s*:\s*(Yes|No|N/A)"
}

parent_status_patterns = {
    "WTW Participant":             r"WTW Participant\s*:\s*(Yes|No|N/A)",
    "Reason Unavailable for Care": r"Reason Unavailable for Care\s*:\s*([^\n]+)",
    "Employment Status":           r"Employment Status\s*:\s*([^\n]+)"
}

parent_income_patterns = {
    "Primary Wages":               r"Primary Wages\s*:\s*\$?(\d+[\d,]*)",
    "Secondary Wages":             r"Secondary Wages\s*:\s*\$?(\d+[\d,]*)",
    "Disability/Unemployment":     r"Disability/Unemployment\s*:\s*\$?(\d+[\d,]*)",
    "Child Support Received":      r"Child Support Received\s*:\s*\$?(\d+[\d,]*)",
    "Child Support Paid":          r"Child Support Paid\s*:\s*\$?(\d+[\d,]*)",
    "CalWORKs Cash Aid":           r"CalWORKs Cash Aid\s*:\s*\$?(\d+[\d,]*)",
    "SSI/SSP":                     r"SSI/SSP\s*:\s*\$?(\d+[\d,]*)",
    "Self-Employment Expenses":    r"Self[\u2011-]Employment Expenses\s*:\s*\$?([A-Za-z0-9/, ]+)",
    "Adjusted Monthly Income":     r"Adjusted Monthly Income\s*:\s*\$?(\d+[\d,]*)"
}

child_patterns = {
    "Name":                        r"Name\s*:\s*([A-Za-z ]+)",
    "DOB":                         r"DOB\s*:\s*(\d{2}/\d{2}/\d{4})",
    "Age":                         r"Age\s*:\s*(\d+)",
    "Relationship":                r"Relationship\s*:\s*([A-Za-z ]+)",
    "Authorized for WTW":         r"Authorized for WTW\s*:\s*(Yes|No|N/A)",
    "Incapacity Details":         r"Incapacity Details\s*:\s*(Yes|No|N/A)"
}