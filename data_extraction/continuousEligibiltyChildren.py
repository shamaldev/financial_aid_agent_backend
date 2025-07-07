# import pdfplumber
import re
from utils.extraction_utils.utils_cec import cec_config,sections
from pathlib import Path
from utils.log_utils.logger_instances import app_logger


class continuousEligibiltyChildren:
    def __init__(self):
        self.cec_config = cec_config
        self.sections = sections

    def extract_fields(self, text: str, config: dict) -> dict:
        try:
            app_logger.log('Started')
            flat = {}
            for name, meta in config["fields"].items():
                m = re.search(meta["pattern"], text, re.IGNORECASE)
                if m:
                    # If there are multiple capture groups (e.g. CEC Period), join them with " | "
                    flat[name] = " | ".join(g.strip() for g in m.groups())
                else:
                    flat[name] = None
            app_logger.log('Sucess')
            return flat
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def structure_record(self, flat: dict, sections: dict) -> dict:
        try:
            app_logger.log('Started')
            record = {}
            for sec, keys in sections.items():
                record[sec] = {}
                for k in keys:
                    val = flat.get(k)
                    # Split Adults/Children into lists
                    if k in ("Adults", "Children") and val:
                        record[sec][k] = [item.strip() for item in val.split(",")]
                    # Break out CEC Period into Begin/End
                    elif k == "CEC Period" and val:
                        b, e = [s.strip() for s in val.split(" | ")]
                        record[sec]["Begin"] = b
                        record[sec]["End"] = e
                    else:
                        record[sec][k] = val
            app_logger.log('Sucess')
            return record
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def parse_form(self, doc_text) -> dict:
        try:
            app_logger.log('Started')
            flat = self.extract_fields(doc_text, cec_config)
            app_logger.log('Sucess')
            return self.structure_record(flat, sections)
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

