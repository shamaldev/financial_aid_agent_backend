# @MADHU
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.tools import FunctionTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os
import json
from utils.pdf_utils.text_utility import alpha_numeric_string
from llm.rag_agent import policy_splitter_agent, chunk_metadata_extracting_agent, policy_logic_generating_agent
from tools.llamaindex.data_preprocessing import PolicyPreprocessor

from utils.log_utils.logger_instances import app_logger

CHROMA_DIR  = os.getenv("CHROMA_DIR", "./chroma_db")
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

def create_or_get_chroma_store(collection_name):
    try:
        app_logger.log("Started")

        os.makedirs(CHROMA_DIR, exist_ok=True)
        os.makedirs(STORAGE_DIR, exist_ok=True)

        chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        chroma_collection = chroma_client.get_or_create_collection(name=collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        app_logger.log("Sucess")
        
        return vector_store
    except Exception as e:
        app_logger.log("Failed", level='error')
        raise
    

def create_index(vector_store, nodes, collection_name):
    try:
        app_logger.log("Started")

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(nodes, storage_context=storage_context)
        index.set_index_id(collection_name)
        index.storage_context.persist(persist_dir=STORAGE_DIR)
        app_logger.log("Sucess")


    except Exception as e:
        app_logger.log("Failed", level='error')
        raise

def recreate_index(vector_store):
    try:
        app_logger.log("Started")

        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
        # # Load a specific index by its ID
        # index = load_index_from_storage(storage_context, index_id=collection_name)
        app_logger.log("Sucess")

        return index

    except Exception as e:
        app_logger.log("Failed", level='error')
        raise


def create_rag_function_tool(index, policy_name, tool_name, summary):
    try:

        app_logger.log("Started")

        def filtered_vector_query(query: str, categories: str = None,  policy_name:str = None, top_k = 8) -> str:

                # Construct metadata filters
                metadata_dicts = []
                if categories:
                    metadata_dicts.extend([{"key": "category", "value": categories}])
                if policy_name:
                    metadata_dicts.extend([{"key": "title", "value": policy_name}])

                # Determine filter condition
                if categories and policy_name:
                    print("FilterCondition.AND")
                    condition = FilterCondition.AND
                else:
                    condition = FilterCondition.OR
                    print("FilterCondition.OR")
                    

                # Apply filters to query engine
                query_engine = index.as_query_engine(
                    similarity_top_k=top_k,
                    filters=MetadataFilters.from_dicts(
                        metadata_dicts,
                        condition=condition # FilterCondition.AND
                    )
                )
                response = query_engine.query(query)
                return response
            
        filtered_vector_query.__doc__ = (
            f"""Use to answer questions over {policy_name}.
            Summary of content: {summary}

            Always leave categories as None UNLESS there is a specific category you want to search for.
            Args:
                query (str): The string query to be embedded.
                categories (str): Filter by set of categories. Leave as None to perform a vector search over all categories. Otherwise, filter by the specified categories.
                policy_name (str): Filter by policy name to perform vector search over it"""
        )   

        vector_query_tool = FunctionTool.from_defaults(
            name=tool_name,
            fn=filtered_vector_query
        )
        app_logger.log("Sucess")

        return vector_query_tool

    except Exception as e:
        app_logger.log("Failed", level='error')
        raise







def rebuild_tools(collection_name, policy_name, tool_name, summary):
    try:

        app_logger.log("Started")

        vector_store = create_or_get_chroma_store(collection_name)
        index = recreate_index(vector_store)
        tool = create_rag_function_tool(index, policy_name, tool_name, summary)

        app_logger.log("Sucess")

        return tool
    except Exception as e:
        app_logger.log("Failed", level='error')
        raise


def create_rag_index(nodes: str, collection_name: str):
    """Get vector query tools from a document."""
    try:

        app_logger.log("Started")

        # init_embbed_model()
        vector_store = create_or_get_chroma_store(collection_name)
        create_index(vector_store, nodes, collection_name)

    except Exception as e:
        app_logger.log("Failed", level='error')
        raise







def create_or_update_tool_map(policy_name, collection_name, tool_name, summary, file_path='tool_map.json'):
    try:
        app_logger.log("Started")

        # Create the new entry
        new_entry = {
            policy_name: {
                "collection_name": collection_name,
                "summary": summary,
                "tool_name": tool_name
            }
        }

        # Load existing data if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    tool_map = json.load(f)
                except json.JSONDecodeError:
                    tool_map = {}
        else:
            tool_map = {}

        # Update the map with the new entry
        tool_map.update(new_entry)

        # Save it back to the file
        with open(file_path, 'w') as f:
            json.dump(tool_map, f, indent=4)

        app_logger.log("Sucess")

    except Exception as e:
        app_logger.log("Failed", level='error')
        raise















def create_index_from_policy(pdf_path):
    try:

        app_logger.log("ENTERED")
        app_logger.log("Started")

        processor = PolicyPreprocessor(pdf_path, policy_splitter_agent, chunk_metadata_extracting_agent, policy_logic_generating_agent)
        nodes, policy_name = processor.run()

        collection_name = alpha_numeric_string(policy_name)
        TOOL_MAP_PATH  = os.getenv("TOOL_MAP_PATH", 'tool_map.json')
        tool_name =  f"{collection_name}_filter_query_tool"
        summary = nodes[0].metadata['summary']
        create_or_update_tool_map(policy_name, collection_name, tool_name, summary, TOOL_MAP_PATH)
        create_rag_index(nodes, collection_name)
        
        app_logger.log("Sucess")
        app_logger.log("EXITED")

    # return tool
    except Exception as e:
        app_logger.log("Failed", level='error')
        raise

def get_all_tools(existing_tools):
    try:
        app_logger.log("ENTERED")
        app_logger.log("Started")

        # Load whatever’s in your JSON map
        TOOL_MAP_PATH = os.getenv("TOOL_MAP_PATH", "tool_map.json")
        if os.path.exists(TOOL_MAP_PATH):
            with open(TOOL_MAP_PATH, "r") as f:
                tool_map = json.load(f)
        else:
            tool_map = {}

        # Initialize your list if it was None
        all_tools = existing_tools or []

        # Decide which entries are missing
        if all_tools:
            existing_names = [t.metadata.name for t in all_tools]
            # only keep those not already present
            required_map = {
                k: v
                for k, v in tool_map.items()
                if v.get("tool_name") not in existing_names
            }
        else:
            # first-ever load: add everything
            required_map = tool_map.copy()

        # nothing to add?
        if not required_map:
            app_logger.log("Sucess: (no new tools)")
        
            app_logger.log("EXITED")
        
            return all_tools

        # rebuild & append
        for policy_name, info in required_map.items():
            collection_name = info["collection_name"]
            tool_name = info["tool_name"]
            summary = info.get("summary")
            new_tool = rebuild_tools(collection_name, policy_name, tool_name, summary)
            all_tools.append(new_tool)

        print(f"!!!!!!!!!!! get_all_tools Sucess (added {len(required_map)} tools)")
        app_logger.log("EXITED")
        return all_tools
    
    except Exception as e:
        app_logger.log("Failed", level='error')
        raise