# @MADHU
from llama_index.core.schema import TextNode
from utils.pdf_utils.text_utility import (
    get_doc, get_text, remove_metadat_lines, get_first_line,
    get_file_name, save_text_to_file, clean_whitespace_characters,
    extract_json_block, text_to_json
)
from utils.log_utils.logger_instances import app_logger


import re
import json

def extract_json_from_response(response):
    response_text = response.choices[0].message.content
    response_json_text = extract_json_block(response_text)
    response_json = text_to_json(response_json_text)
    return response_json

def remove_think_blocks(text: str) -> str:
    """
    Remove any content (including the <think> tags) between <think> and </think>.
    """
    try:
        app_logger.log('Started')
        # Use DOTALL so that `.*?` matches newlines as well
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        app_logger.log('Sucess')
        return cleaned.strip()
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 



class PolicyPreprocessor:
    def __init__(self, pdf_path, splitter_agent, metadata_agent, policy_logic_agent):
        self.pdf_path = pdf_path
        self.pages_data = []
        self.all_text = ""
        self.title = ""
        self.file_name = ""
        self.split_policy_dict = {}
        self.chunk_metadata = {}
        self.nodes = []
        self.splitter_agent = splitter_agent
        self.metadata_agent = metadata_agent
        self.policy_logic_agent = policy_logic_agent
        # self.page_matches = {}

    def get_pdf_data(self):
        try:
            app_logger.log('Started')

            doc = get_doc(self.pdf_path)

            for page_number, page in enumerate(doc, start=1):
                text = get_text(page)
                self.all_text += text
                self.pages_data.append({ "page_number": page_number, "text": text })

            self.all_text = remove_metadat_lines(self.all_text)
            
            self.title = get_first_line(self.all_text)

            self.file_name = get_file_name(self.pdf_path)

            output_path = f"{self.title}.txt"
            save_text_to_file(self.all_text, output_path)

            self.pages_data = clean_whitespace_characters(self.pages_data)
            app_logger.log('Sucess')
            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def split_policy(self):
        try:
            app_logger.log('Started')

            # call your policy_splitter_agent
            split_policy_response = self.splitter_agent(self.all_text)
            self.split_policy_dict = extract_json_from_response(split_policy_response)
            app_logger.log('Sucess')

            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def generate_metadata(self):
        try:
            app_logger.log('Started')

            for key, value in self.split_policy_dict.items():
                chunk_metadata_response = self.metadata_agent(f"{key} : {value}")
                chunk_metadata_dict = extract_json_from_response(chunk_metadata_response)
                self.chunk_metadata[key] = chunk_metadata_dict


            if self.title == 'CalWORKs Stage One Child Care Eligibility':
                criteria_sections = [
                    "Eligible Children",
                    "Eligible Parents",
                    "Two-Parent Households",
                    "Non-Assistance Unit Members",
                    "Eligible Former Clients",
                    "Inter-County Transfers"
                ]

                for k, v in self.chunk_metadata.items():
                    match_found = any(
                        re.search(rf"(^|\b)\d*\.?\s*{re.escape(section)}\b", k, re.IGNORECASE)
                        or k.strip().lower() == section.lower()
                        for section in criteria_sections
                    )
                    v['category'] = 'criteria' if match_found else 'info'
                    
            if self.title == 'Continuous Eligibility for Children (CEC)':
                criteria_sections = [
                    "CEC ELIGIBILITY REQUIREMENTS",
                    "PERIOD OF ELIGIBILITY",
                    "AID CODES",
                    "PROCESSING INSTRUCTIONS FOR ADVERSE CHANGES IN CIRCUMSTANCE",
                    "LOSS OF CONTACT",
                    "CEC VS. DEEMED INFANT ELIGIBILITY"
                ]

                for k, v in self.chunk_metadata.items():
                    match_found = any(
                        re.search(rf"(^|\b)\d*\.?\s*{re.escape(section)}\b", k, re.IGNORECASE)
                        or k.strip().upper() == section
                        for section in criteria_sections
                    )
                    v['category'] = 'criteria' if match_found else 'info'

            app_logger.log('Sucess')

            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    
    def add_metadata(self):
        try:
            app_logger.log('Started')

            for key, value in self.chunk_metadata.items():
                value['section_name'] = key
                value['title'] = self.title
                # value['page_number'] = self.page_matches[key]
                value['file_name'] = self.file_name

            app_logger.log('Sucess')

            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 

    
    def generate_policy_logic(self):
        try:
        
            app_logger.log('Started')
            all_criteria = []
            for key, value in self.chunk_metadata.items():

                if value['category'] == 'criteria':
                    all_criteria.append(key)

            
            policy_logic_response = self.policy_logic_agent(all_criteria, self.all_text)
            policy_logic_response_text = policy_logic_response.choices[0].message.content
            cleaned_policy_logic_response_text = remove_think_blocks(policy_logic_response_text)
            # print(policy_logic_response_text)

            self.split_policy_dict['policy_logic'] = cleaned_policy_logic_response_text
            self.chunk_metadata['policy_logic'] = {'summary' : 'Gives a high level over view of all the criterion', 'category' : 'final_logic', 'section_name': 'policy_logic', 'title' :self.title, 'file_name' : self.file_name}

            app_logger.log('Sucess')

            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def format_metadata(self):
        try:
            app_logger.log('Started')

            for key, value in self.chunk_metadata.items():
                for k, v in value.items():
                    if not isinstance(v, str):
                        value[k] = str(v)
            app_logger.log('Sucess')
            
            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def create_nodes(self):
        try:
            app_logger.log('Started')

            for key, value in self.split_policy_dict.items():
                node = TextNode(text=f"{key} : {value}", metadata=self.chunk_metadata[key])
                self.nodes.append(node)

            with open(f"{self.title}nodes.txt", "w", encoding="utf-8") as f:
                for key, value in self.split_policy_dict.items():
                    text = f"{key} : {value}"
                    metadata = self.chunk_metadata.get(key, {})
                    f.write(f"Text: {text}\n")
                    f.write(f"Metadata: {metadata}\n")
                    f.write("="*40 + "\n")

            data = []

            for key, value in self.split_policy_dict.items():
                entry = {
                    "text": f"{key} : {value}",
                    "metadata": self.chunk_metadata.get(key, {})
                }
                data.append(entry)

            with open(f"{self.title}nodes.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            app_logger.log('Sucess')

            return self
        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 


    def run(self):
        try:
            app_logger.log('ENTERED')
            app_logger.log('Started')

            self.get_pdf_data().split_policy().generate_metadata().add_metadata().generate_policy_logic().format_metadata()
            ## @TODO Get Human Feedback
            self.create_nodes()
                    
            app_logger.log('Sucess')
            app_logger.log('DONE')

            return self.nodes, self.title

        except Exception as e:
            app_logger.log('Failed', level='error')
            raise 





































    # def match_pages(self):
    #     # Precompile patterns once
    #     compiled_keys = {
    #         key: re.compile(rf'\b{re.escape(key)}\b')
    #         for key in self.split_policy_dict
    #     }

    #     self.page_matches = {key: [] for key in self.split_policy_dict}

    #     for page_data in self.pages_data:
    #         page_text = page_data["text"]
    #         for key, pattern in compiled_keys.items():
    #             if pattern.search(page_text):
    #                 self.page_matches[key].append(page_data["page_number"])

    #     # Replace lists with last item as int, or 0 if the list is empty
    #     for key, val in self.page_matches.items():
    #         if isinstance(val, list):
    #             if len(val) > 0:
    #                 self.page_matches[key] = val[-1]
    #             else:
    #                 self.page_matches[key] = 0
    #     return self