# @MADHU
import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings as llamasettings
from utils.log_utils.logger_instances import app_logger


def init_embbed_model():
    try:
        app_logger.log('Started')
        EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
        llamasettings.llm = None
        llamasettings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
        app_logger.log('Sucess')

    except Exception as e:
        app_logger.log('Failed', level='error')
        raise 