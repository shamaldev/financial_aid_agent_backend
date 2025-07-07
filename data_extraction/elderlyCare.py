# import pdfplumber
import re
from utils.extraction_utils.utils_elderlycare import pace_static_patterns,eligibility_patterns,spousal_patterns
from utils.log_utils.logger_instances import app_logger

class CareForElderly:
    def __init__(self):
        self.pace_static_patterns = pace_static_patterns
        self.eligibility_patterns = eligibility_patterns
        self.spousal_patterns = spousal_patterns

    def extract_text(self,doc_text):
        try:
            app_logger.log('Started')
            app_logger.log('Sucess')
            return doc_text.replace('●','').replace('☑','Yes').replace('⬜','No')
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 
        
    def normalize_phone(self,raw):
        try:
            app_logger.log('Started')
            digits = re.sub(r"\D", "", raw) 
            if len(digits)==10:
                app_logger.log('Sucess')
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            app_logger.log('Sucess')
            return raw
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def extract_static(self,text):
        try:
            app_logger.log('Started')
            out = {}
            for key, pat in self.pace_static_patterns.items():
                m = re.search(pat, text)
                out[key] = self.normalize_phone(m.group(1)) if key=="Phone Number" and m else (m.group(1).strip() if m else None)
            app_logger.log('Sucess')
            return out
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def extract_eligibility(self,text):
        try:
            app_logger.log('Started')
            out = {}
            for key, pat in self.eligibility_patterns.items():
                m = re.search(pat, text)
                if m:
                    # if two groups (detail + flag), join them
                    if len(m.groups())==2:
                        out[key] = f"{m.group(1).strip()} ({m.group(2)})"
                    else:
                        out[key] = m.group(1).strip()
                else:
                    out[key] = None
            app_logger.log('Sucess')
            return out
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def extract_spousal(self,text):
        try:
            app_logger.log('Started')
            out = {}
            for key, pat in self.spousal_patterns.items():
                m = re.search(pat, text)
                out[key] = m.group(1).strip() if m else None
            app_logger.log('Sucess')
            return out
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def parse_form(self,doc_text):
        try:
            app_logger.log('Started')
            text = self.extract_text(doc_text)
            data = {
                "Applicant": self.extract_static(text),
                "Eligibility": self.extract_eligibility(text),
                "Spousal Impoverishment": self.extract_spousal(text)
            }
            app_logger.log('Sucess')
            return data
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 