from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
 
 
def check_policy_candidates():
    system = SystemMessage(
        content=(
            "You are a policy-aware assistant. "
            "Given the user's current question and the description of available policies, return the best matches. "
            "Be robust to synonyms (e.g., 'program' vs 'policy'), plural forms, and word order. "
            "If exactly one policy clearly matches, return its exact name. "
            "If multiple policies match equally well, return all matching names separated by commas. "
            "If no policy matches, reply 'Unknown'."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
            ---
            User Question:
            {question}

            Available Policies (name and summary):
            {policy_details}
            ---
            Output (one line, **exactly** one of the following):
            • A single policy name if one clear match
            • Multiple names separated by commas if ambiguous
            • Or 'Unknown' if none match

            **Do not** include any list markers, hyphens, or bullets—just the policy name(s).
        """
    )
    return ChatPromptTemplate.from_messages([system, human])
 
def generate_clarification_message(candidates: list[str] = None, all_policies: list[str] = None) -> str:
    if candidates:
        return (
            "I found multiple possible policies: "
            f"{', '.join(candidates)}. "
            "Could you please specify which one you’d like?"
        )
    return (
        "I couldn’t find a matching policy. "
        "Here are all available policies: "
        f"{', '.join(all_policies)}. "
        "Please let me know which one you need."
    )
 
def generate_bot_answer():
    system = SystemMessage(
        content=(
            "You are a helpful policy assistant. Answer the user's question using only the context of the selected policy. "
            "Ignore unrelated history. Provide a concise, structured, and detailed response."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        ---
        Selected Policy Context:
        {policy_context}

        User Question:
        {question}

        Conversation History (for clarity if needed):
        {history}
        ---
        Generate a clear and detailed response focusing on the policy context.
        """
    )
    return ChatPromptTemplate.from_messages([system, human])



def identify_intent_prompt():
    system = SystemMessage(
        content=(
            """
            You are an expert at interpreting user questions within a policy-assistant context.
            Given a prior Chat history and a new user query, determine if the new user query is a follow-up, a brand-new question, or a request to list all policies.
            Respond with a JSON object containing two fields:
            - "intent": "new" if it's a brand-new question, "follow" if it's a follow-up, or "list_policies" if it's a request to list all policies.
            - "relevant_context": if it's a follow-up, provide all the relevant context from the chat history as a string; otherwise, set to null.
            """
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """Chat history:
            {chat_history}
            
           New user query: 
           {query} 

           Respond only with the JSON object and no additional text.
        
        """
    )
    return ChatPromptTemplate.from_messages([system, human])