# File: chatbot/llm.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from chatbot.utils import load_json
from chatbot.prompts.prompt import (
    check_policy_candidates,
    generate_bot_answer,
    generate_clarification_message,
    identify_intent_prompt,
)
from tools.llamaindex.agentic_rag import rag_tool
# from tools.llamaindex.llamaindex_config import init_embbed_model
import json

load_dotenv()
# init_embbed_model()
 
# Load environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
TOOL_MAP_PATH = os.getenv("TOOL_MAP_PATH")
 
class ChatbotAgents:
    def __init__(self, model: str = GROQ_MODEL, api_key: str = GROQ_API_KEY, json_file: str = TOOL_MAP_PATH):
        self.llm = ChatGroq(model_name=model, groq_api_key=api_key)
        # Load policy config
        self.file = load_json(json_file)
        print(self.file,'file')
        # Lowercase policy names for comparison
        self.policy_names = list(self.file.keys())
      
        self.policy_names_lower = [name.lower() for name in self.policy_names]

        print(self.policy_names,"policy_names")

    def chatbot_flow(self, query: str, history: list[str]) -> str:
        print(">>>>>>>>>>>>>>>>>>>>>> policy chat started")

        candidates = self.identify_policies(query)

        print(">>>>>>>>>>>>>>>>>>>>>> candidates identified")

        if not candidates:
            # No matches: ask user to choose from all policies
            return generate_clarification_message(all_policies=list(self.policy_names))
        if len(candidates) > 1:
            # Ambiguous: ask user to pick among candidates
            return generate_clarification_message(candidates=candidates)
        # Exactly one
        policy_name = candidates[0]
        
        # Step 2: Retrieve context via RAG
        context = rag_tool(
            query,
            categories=None,
            policy_name=policy_name,
            top_k = 5
        )
        print(">>>>>>>>>>>>>>>>>>>>>> rag tool called")


        prompt = generate_bot_answer()
        formatted = prompt.format_messages(
            history=history,
            question=query,
            policy_context=context
        )
        resp = self.llm.invoke(formatted).content.strip()
        print(">>>>>>>>>>>>>>>>>>>>>> llm response generated")
        print("<<<<<<<<<<<<<<<<<<<<<< policy chat ended")

        return resp

     

    def identify_policies(self, question: str) -> list[str]:
        """
        Use LLM to get a ranked list of candidate policies.
        Returns a list of policy names (exact keys) or empty if none match.
        """
        prompt = check_policy_candidates()
        formatted = prompt.format_messages(
            question=question,
            policy_details=self.file  # includes summaries
        )
        resp = self.llm.invoke(formatted).content.strip()
        # Expect comma-separated list or 'None'
        candidates = [p.strip() for p in resp.split(',') if p.strip().lower() != 'none']

        print(">>>>>>>>>>> identify_policies <<<<<<<<<<<<")
        print("candidates \n")
        print(candidates)
        print("policy_names \n")
        print(self.policy_names)

        # Normalize to exact key names
        normalized = []
        for p in candidates:
            for name in self.policy_names:
                if p.lower() == name.lower():
                    normalized.append(name)
                    break
        return normalized
     
    
    def identify_intent(self, user_question: str, history: list[str]) -> dict:
        chat_history_str = "\n".join(history)

        prompt = identify_intent_prompt()
        formatted = prompt.format_messages(chat_history=chat_history_str, query=user_question)
   
        resp = self.llm.invoke(formatted)
        try:
            intent_data = json.loads(resp.content)
        except json.JSONDecodeError:
            intent_data = {"intent": "error", "relevant_context": None}
        return intent_data

    def generate_answer(self, user_question: str, history: list[str]) -> str:
        intent_data = self.identify_intent(user_question, history)
        intent = intent_data.get("intent")
        relevant_context = intent_data.get("relevant_context")

        print("<<<<<<<<<<Intent Recognition started>>>>>>>>")
        print(intent_data)

        if intent == "new":
            response = self.chatbot_flow(user_question,history)
            return response
        elif intent == "follow":
            new_query = relevant_context + "\n" + user_question
            response = self.chatbot_flow(new_query,history)
            return response
        elif intent == "list_policies":
            header = "These are the available policies:\n"
            body_lines = []
            for policy_name, description in self.file.items():
                # wrap long descriptions if you like, but this is the basic idea:
                body_lines.append(f"- {policy_name}: {description}")
            return header + "\n".join(body_lines)
        
        

# if __name__ == '__main__':
#     agent = ChatbotAgents()  # Assuming this class is defined elsewhere
#     history = [
#         """User:Explain about EWC policy? 
#         Assistant: The Every Woman Counts (EWC) policy is a program offered by the California Department of Health Care Services (DHCS) that provides free breast and cervical cancer screening services to uninsured women. Here's an overview of the policy:

#         **Eligibility Criteria:**

#         To be eligible for the EWC program, women must meet the following criteria:

#         * Live in California
#         * Have no or limited health insurance, or have health insurance with a co-payment or deductible they cannot afford
#         * Not be eligible for Medi-Cal
#         * Have income up to 200% of the Federal Poverty Level (FPL)
#         * Be at least 40 years old for breast exams and mammograms
#         * Be at least 21 years old for Pap tests

#         **Services Covered:**

#         The EWC program covers the following services:

#         * Mammograms
#         * Clinical breast exams
#         * Pap tests
#         * Human Papillomavirus (HPV) tests (in combination with a Pap test)

#         **Referral Process:**

#         Women who are ineligible for Medi-Cal or Covered CA health plan and are in need of breast and cervical cancer screenings can be referred to the EWC program. Bureau Assistants (BAs) can provide in-person or mail the EWC flyer and brochure to eligible women. Women can also call an automated referral line at (800) 511-2300 or use an Online Provider Locator to find up to ten doctors or clinics in their area that provide these services.

#         **Additional Information:**

#         The EWC program assists eligible women with enrollment into the Breast and Cervical Cancer Treatment Program (BCCTP). For more information, refer to the Medi-Cal Handbook Section 10 – Limited Services (page 171).

#         The EWC program is available 24 hours a day, 7 days a week, and can be accessed through the DHCS website: http://www.dhcs.ca.gov/services/Cancer/ewc/Pages/default.aspx."""
#     ]
#     res = agent.generate_answer("Explain about the CEC policy?", history)
#     print(res)

 
   