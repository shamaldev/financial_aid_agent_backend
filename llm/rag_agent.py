
from groq import Groq
import os 
from prompts.prompt import (
    split_policy_prompt,
    extract_metadata_prompt,
    generate_policy_logic_prompt
)
from dotenv import load_dotenv
import time

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

client = Groq(api_key=GROQ_API_KEY)


# @Madhu START
deepseek_llm = os.getenv("DEEPSEEK_MODEL")

def policy_splitter_agent(policy_text: str) -> dict:
    prompt = split_policy_prompt(policy_text)
    start = time.time()
    response = client.chat.completions.create(
        model= deepseek_llm,
        messages=[{"role": "user", "content": prompt}],
    )
    end = time.time()
    print(f"policy_splitter_agent Execution time: {end - start:.4f} seconds")    
    return response

def chunk_metadata_extracting_agent(policy_text: str):
    prompt = extract_metadata_prompt(policy_text)
    start = time.time()
    response = client.chat.completions.create(
        model= deepseek_llm,
        messages=[{"role": "user", "content": prompt}],
    )
    end = time.time()
    print(f"chunk_metadata_extracting_agent Execution time: {end - start:.4f} seconds")
    return response

def policy_logic_generating_agent(criteria_list: list[str], policy_text: str):
    start = time.time()

    prompt = generate_policy_logic_prompt(criteria_list, policy_text)
    response = client.chat.completions.create(
        model= deepseek_llm,
        messages=[{"role": "user", "content": prompt}],
    )
    end = time.time()
    print(f"policy_logic_generating_agent Execution time: {end - start:.4f} seconds")
    return response