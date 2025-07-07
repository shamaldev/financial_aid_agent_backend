# import pdfplumber
import re
from utils.extraction_utils.utils_childcare import calworks_static_patterns,parent_status_patterns,parent_income_patterns,child_patterns
from utils.log_utils.logger_instances import app_logger
            
class StageOneChildCare:
    def __init__(self):
        self.calworks_static_patterns = calworks_static_patterns
        self.parent_status_patterns = parent_status_patterns
        self.parent_income_patterns = parent_income_patterns
        self.child_patterns = child_patterns

    def extract_recert(self,text):
        try:
            app_logger.log('Started')
            lines = re.findall(r"^[^\S\r\n]*[●\*]\s*(☑|X)?\s*(.+)$", text, flags=re.MULTILINE)
            selected = []
            other = None
            for mark, label in lines:
                if 'Addition of a child' in label or 'Change of child care provider' in label or 'Child turns age 13' in label:
                    if mark.strip() in ('☑', 'X'):
                        selected.append(label.strip())
                elif label.startswith('Other:'):
                    val = label.split(':', 1)[1].strip()
                    other = val
                    if mark.strip() in ('☑', 'X') and val:
                        selected.append(val)
            if selected:
                app_logger.log('Sucess')
                return '; '.join(selected)
            app_logger.log('Sucess')
            return other or 'N/A'
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def extract_text(self,pdf_text):
        # with pdfplumber.open(pdf_path) as pdf:
        #     text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        try:
            app_logger.log('Started')
            app_logger.log('Sucess')
            return pdf_text.replace('●', '').replace('■', '').replace('□', '')
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
            data = {'Applicant': {}, 'Household': {}, 'CalWORKs Status': {}}
            for key, pat in self.calworks_static_patterns.items():
                m = re.search(pat, text)
                if m:
                    val = m.group(1).strip()
                    if key == 'Phone':
                        val = self.normalize_phone(val)
                    if key in ['Submission Date', 'Case Number', 'Begin Aid Date', 'Full Name', 'Phone', 'Address']:
                        data['Applicant'][key] = val
                    elif key in ['Household Composition', 'Two-Parent Household']:
                        data['Household'][key] = val
                    else:
                        data['CalWORKs Status'][key] = val
            app_logger.log('Sucess')
            return data
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    def extract_parents(self,text):
        try:
            app_logger.log('Started')
            entries = re.split(r"Parent (\d+):", text)[1:]
            parents = {}
            for idx in range(0, len(entries), 2):
                num, block = entries[idx], entries[idx+1]
                # Initialize parent dictionary if not already present
                if num not in parents:
                    parents[num] = {'Status': {}, 'Income': {}}
                p = parents[num]

                # Extract status fields
                for key, pat in self.parent_status_patterns.items():
                    m = re.search(pat, block)
                    if m:
                        p['Status'][key] = m.group(1).strip()

                # Extract income fields
                for key, pat in self.parent_income_patterns.items():
                    m = re.search(pat, block)
                    if m:
                        p['Income'][key] = m.group(1).strip()

            # Convert numeric keys to 'Parent X' format
            app_logger.log('Sucess')
            return {f'Parent {num}': p for num, p in parents.items()}
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 
    
    def extract_children(self,text):
        try:
            app_logger.log('Started')
            entries = re.split(r"Child (\d+):", text)[1:]
            children = {}
            for idx in range(0, len(entries), 2):
                num, block = entries[idx], entries[idx+1]
                c = {}
                for key, pat in self.child_patterns.items():
                    m = re.search(pat, block)
                    if m:
                        c[key] = m.group(1).strip()
                children[f'Child {num}'] = c
            app_logger.log('Sucess')
            return children
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def parse_form(self,doc_text):
        try:
            app_logger.log('Started')
            app_logger.log('Strated')
                
            print('Entered into child care extraction function')
            text = self.extract_text(doc_text)
            data = self.extract_static(text)
            data['Parents'] = self.extract_parents(text)
            data['Children'] = self.extract_children(text)
            data['Recertification Trigger'] = self.extract_recert(text)
            app_logger.log('Sucess')

            app_logger.log('Sucess')
            return data
        
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 
