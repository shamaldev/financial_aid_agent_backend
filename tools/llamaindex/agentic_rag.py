# @MADHU
from llama_index.core.objects import ObjectIndex
from llama_index.core import VectorStoreIndex
import re
from typing_extensions import Annotated, Union, List

from utils.log_utils.logger_instances import app_logger
from tools.llamaindex.rag_tool_creator import get_all_tools

_all_tools = None
_obj_retriever = None

def _initialize_retriever():
    """
    Initialize or refresh the tool list and object retriever.
    """
    try:
        app_logger.log('Strated')
        global _all_tools, _obj_retriever
        # Fetch the latest set of tools
        new_tools = get_all_tools(_all_tools)
        # If first initialization or tools have changed
        if _all_tools is None or set(new_tools) != set(_all_tools):
            _all_tools = new_tools
            # Build a new index and retriever
            obj_index = ObjectIndex.from_objects(_all_tools, index_cls=VectorStoreIndex)
            _obj_retriever = obj_index.as_retriever(similarity_top_k=3)
            app_logger.log('Sucess')
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 

def clean_retrieved_node_text(text: str) -> list[str]:
    try:
        app_logger.log('Strated')
        # 1) Strip out the LLM boilerplate
        step1 = re.sub(
            r'Given the context information and not prior knowledge, answer the query\.\s*'
            r'Query: .*?\s*Answer:\s*|Context information is below\.\s*',
            '',
            text,
            flags=re.DOTALL
        )

        # 2) Replace only metadata lines (starting with summary:, category:, title:, file_name:, or section:)
        #    with a separator line of "==========" so we can split on it later.
        step2 = re.sub(
            r'^[ \t]*(?:summary|category|title|file_name|section_name):.*\n?',
            '==========\n',
            step1,
            flags=re.IGNORECASE | re.MULTILINE
        )

        # 3) Remove any standalone "Empty Response" lines
        step3 = re.sub(
            r'^Empty Response\s*\n?',
            '',
            step2,
            flags=re.MULTILINE
        )

        # 4) Trim leading/trailing whitespace
        cleaned = step3.strip()

        # 5) Split into blocks wherever "==========" appears
        blocks = [
            block.strip()
            for block in cleaned.split('==========')
            if block.strip()
        ]
        app_logger.log('Sucess')

        return blocks
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 



all_tools = []
def rag_tool(user_query: Annotated[str, "user query."], 
            categories: Annotated[List[Union[str, None]], "category of the query. should be 'info', 'criteria', 'example' or [None] as value "], 
            policy_name: Annotated[List[Union[str, None]], "Name of the policy whose context is required or None if no specific policy is required"],
            top_k: Annotated[int, "top k context."], 
            )-> Annotated[List[Union[str, None]], "Context relevant to user query"]:
    try:
        app_logger.log('Strated')
        app_logger.log("retriving tools Strated")
        _initialize_retriever()
        retrieved_tools = _obj_retriever.retrieve(user_query)
        app_logger.log(" retriving tools Done")

        app_logger.log("retriving Nodes Strated")
        all_cleaned_text = []
        cleaned_texts = []

        all_retrieved_nodes =[]
        # Iterate through each retrieved tool
        for tool in retrieved_tools:
            retrieved_node = tool.call(user_query, categories=categories, policy_name=policy_name) # ["criteria", None] 
            all_retrieved_nodes.append(retrieved_node)

        for node in all_retrieved_nodes:
            retrieved_text = node.content
            cleaned_texts = clean_retrieved_node_text(retrieved_text)
            all_cleaned_text.extend(cleaned_texts)
        all_cleaned_text = list(filter(lambda x: x != "", all_cleaned_text))

        app_logger.log("retriving Nodes Done")
        app_logger.log("Sucess")

        return all_cleaned_text
    
    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 