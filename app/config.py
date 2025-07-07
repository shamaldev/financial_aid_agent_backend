from pydantic_settings import BaseSettings
from dotenv import load_dotenv
# import os


load_dotenv()

class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str
    autogen_use_docker: bool
    embedding_model: str
    deepseek_model: str
    storage_dir: str
    chroma_dir: str
    tool_map_path: str
    database_hostname: str
    database_password: str
    database_name: str
    database_username: str
    database_port: int
    sslmode: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    redis_url: str
    langchain_tracing_v2: str
    langchain_api_key: str
    langchain_project: str
    class Config:
        env_file = ".env"
    
# Load settings
settings = Settings()

