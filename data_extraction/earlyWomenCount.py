# import pdfplumber
import re
from utils.extraction_utils.utils_ewc import ewc_config,sections
from utils.log_utils.logger_instances import app_logger

class EarlyWomenCount:
    def __init__(self):
        self.ewc_config = ewc_config
        self.sections = sections
 
    def extract_fields(self,text, config):
        try:
            app_logger.log('Started')
            flat = {}
            for field, meta in config["fields"].items():
                if meta["method"] == "regex":
                    m = re.search(meta["pattern"], text, re.IGNORECASE)
                    flat[field] = m.group(1).strip() if m else None
            app_logger.log('Sucess')
            return flat
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 
        
    def structure_record(self,flat, sections):
        try:
            app_logger.log('Started')
            record = {}
            for sec, keys in sections.items():
                record[sec] = {k: flat.get(k) for k in keys}
            app_logger.log('Sucess')
            return record
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def parse_form(self,doc_text):
        try:
            app_logger.log('Started')

            flat = self.extract_fields(doc_text, self.ewc_config)

            # Fallback: extract Age from the "(Age XX)" in the DOB line if not found above
            if not flat.get("Age"):
                m = re.search(r"Date of Birth\s*:\s*\d{2}/\d{2}/\d{4}\s*\(Age\s*(\d+)\)", doc_text)
                flat["Age"] = m.group(1) if m else None

            app_logger.log('Sucess')
            return self.structure_record(flat, sections)
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 