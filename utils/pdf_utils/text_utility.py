import fitz
import os
import re
import json
from utils.log_utils.logger_instances import app_logger


def get_doc(pdf_path):
    try:
        app_logger.log('Started')
        # Open the PDF
        doc = fitz.open(pdf_path) 
        app_logger.log('Sucess')
        return doc
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def get_text(page):
    try:
        app_logger.log('Started')
        text = page.get_text()
        app_logger.log('Sucess')
        return text
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def remove_metadat_lines(input_string):
    try:
        app_logger.log('Started')
        # Remove lines that start with optional spaces and "Downloaded On:"
        pattern = r"(?m)^\s*Downloaded On:.*(?:\r?\n)?"
        app_logger.log('Sucess')
        return re.sub(pattern, "", input_string)
    # pattern = r"^\s*Downloaded On:.*$"
    # return re.sub(pattern, "", input_string, flags=re.MULTILINE)
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def get_first_line(text):
    try:
        app_logger.log('Started')
        first_line = text.partition('\n')[0]
        app_logger.log('Sucess')
        return first_line
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def get_file_name(pdf_path):
    try:
        app_logger.log('Started')
        file_name = os.path.basename(pdf_path)
        app_logger.log('Sucess')
        return file_name
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def save_text_to_file(text, file_path):
    try:
        app_logger.log('Started')
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def clean_whitespace_characters(pages_dict):
    try:
        app_logger.log('Started')
        for page_data in pages_dict:
            # Replace all whitespace characters (including \n, \r, \t) with a single space
            page_data["text"] = re.sub(r'\s+', ' ', page_data["text"]).strip()
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def extract_json_block(text):
    app_logger.log('Started')
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        app_logger.log('Sucess')
        return match.group(1)
    else:
        app_logger.log('Failed', level='error')
        raise ValueError("No valid ```json ... ``` block found.")


def text_to_json(json_text):
    try:
        app_logger.log('Started')
        res_dict = json.loads(json_text)
    except json.JSONDecodeError as e:
        app_logger.log('Failed', level='error')
        return None
    
    app_logger.log('Sucess')
    return res_dict


def alpha_numeric_string(s):
    try:
        app_logger.log('Started')
        # Replace spaces with underscores
        s = s.replace(' ', '_')
        
        # Keep only characters from [a-zA-Z0-9._-]
        s = re.sub(r'[^a-zA-Z0-9._-]', '', s)
        
        # Remove leading characters not in [a-zA-Z0-9]
        s = re.sub(r'^[^a-zA-Z0-9]+', '', s)
        
        # Remove trailing characters not in [a-zA-Z0-9]
        s = re.sub(r'[^a-zA-Z0-9]+$', '', s)
        
        app_logger.log('Sucess')
        return s

    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 




