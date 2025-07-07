
import pdfplumber
from typing import Any, Tuple
from data_extraction.childCare import StageOneChildCare
from data_extraction.continuousEligibiltyChildren import continuousEligibiltyChildren
from data_extraction.earlyWomenCount import EarlyWomenCount
from data_extraction.elderlyCare import CareForElderly
from utils.log_utils.logger_instances import app_logger

# Mapping extractors
FUNCTIONS_MAP = {
    'CalWORKs Stage One Child Care Application Form': [StageOneChildCare(),'CalWORKs Stage One Child Care Eligibility'],
    'Continuous Eligibility for Children (CEC) Application Form': [continuousEligibiltyChildren(),'Continuous Eligibility for Children (CEC)'],
    'Every Woman Counts (EWC) Program Application Form': [EarlyWomenCount(),'Every Woman Counts (EWC) Program'],
    'Programs of All-Inclusive Care for the Elderly (PACE) Application Form': [CareForElderly(),'Programs of All-Inclusive Care for the Elderly (PACE)']
}

def extract_application_data(pdf_path: str) -> Tuple[Any, str]:
    try:
        app_logger.log('Started')

        #  1. Read all pages and accumulate text
        with pdfplumber.open(pdf_path) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
        full_text = "\n".join(pages_text)
        # 2. Pull out the first non-empty line
        #    splitlines() preserves order; filter out blank lines
        lines = [line for line in full_text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("PDF contained no extractable text.")
        first_line = lines[0].strip()
        print("<<<<<<<<<<<<<<:", first_line)
        # 3. Look up extractor by that first line
        extractor = FUNCTIONS_MAP.get(first_line)
        if not extractor:
            raise KeyError(f"No extractor found for first line “{first_line}”")
        # 4. Run your parser & return its output plus whatever metadata you had
        parsed = extractor[0].parse_form(full_text)
        metadata = extractor[1]
        app_logger.log('Sucess')
        return parsed, metadata
    
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 