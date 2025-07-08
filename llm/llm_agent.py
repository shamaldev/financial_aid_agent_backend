from dotenv import load_dotenv
import os
import json
from prompts.prompt import (
    application_analyzing_prompt,
    report_feedback_agent_prompt,
    revise_report_prompt,
    criteria_evaluation_prompt,
    final_report_prompt,
    report_formatter_prompt,
    feedback_classification_prompt,
    handle_query_prompt,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

import asyncio

from tools.llamaindex.agentic_rag import rag_tool
from utils.llm_parser import _clean_and_parse_json

load_dotenv()

class LLMAgents:
    def __init__(self, model=None, api_key=None):
        self.llm = ChatGroq(
            model_name=model or os.getenv("GROQ_MODEL"),
            groq_api_key=api_key or os.getenv("GROQ_API_KEY")
        )
        # Each is now a RunnableSequence using the pipe `|`
        self.generate_report_chain = (
            application_analyzing_prompt() | self.llm | StrOutputParser()
        )
        self.review_report_chain = (
            report_feedback_agent_prompt() | self.llm | StrOutputParser()
        )
        self.revise_report_chain = (
            revise_report_prompt() | self.llm | StrOutputParser()
        )
        self.criteria_chain = (
            criteria_evaluation_prompt() |
            self.llm |
            StrOutputParser()
        )
        self.final_report_chain = (
            final_report_prompt() |
            self.llm |
            StrOutputParser()
        )
        self.final_report_formater_chain = (
            report_formatter_prompt() | 
            self.llm | 
            StrOutputParser()
        )
        # New chains
        self.classify_feedback_chain = feedback_classification_prompt() | self.llm | StrOutputParser()
        self.handle_query_chain = handle_query_prompt() | self.llm | StrOutputParser()


    # classify feedback
    async def classify_feedback(self, feedback: str) -> str:
        response = self.classify_feedback_chain.invoke({"feedback": feedback})
        return response.strip().lower()

    # method to handle query feedback
    async def handle_query(self, state: dict) -> dict:
        response = self.handle_query_chain.invoke({
            "feedback": state["feedback"],
            "policy_context": state["policy_context"],
            "application": state["application"],
            "report": state["report"]
        })
        state["query_response"] = response
        state["status"] = "query_answered"
        return state
    

    async def generate_report(self, state: dict) -> dict:
        print("<<<<<<<<<< generate_report agent >>>>>>>>>>")
        response = self.generate_report_chain.invoke({
            "application_details": state["application"],
            "policy_context": state["policy_context"],
        }) 
        print("Report generated using generated report < 3:", response)

        return response

    async def review_report(self, state: dict) -> dict:
        print("<<<<<<<< Review Report >>>>>>>>>>")
        response = self.review_report_chain.invoke({
            "application_details": state["application"],
            "policy_context": state["policy_context"],
            "generated_report": state['criteria'],
        })
        print("Review report:", response)
        if response.strip().lower().startswith("feedback"):
            state["feedback"] = response
            state["status"] = "needs_revision"
        else:
            state["status"] = "approved_by_main"
        return state


    async def revise_report(self, state: dict) -> dict:
        print("<<<<<<<< Revise Report >>>>>>>>>>")
        revised = self.revise_report_chain.invoke({
            "application_details" : state['application'],
            "original_report": state['criteria'],
            "feedback": state["feedback"],
            "policy_context": state["policy_context"],
        })
        print("Original Report:", state['criteria'])

        print("Revised Report:", revised)
        state['criteria'] = revised
        state["status"] = "revised"
        # increment before routing back to review
        state["revision_count"] = state.get("revision_count", 0) + 1
        print(f"Revision count is now {state['revision_count']}")
        return state


    async def criteria_evaluation(self, section: str, application_data: str) -> dict:
        print("<<<<<<<< Criteria Evaluation >>>>>>>>>>")
        resp = self.criteria_chain.invoke({
            "section": section,
            "application_data": application_data
        })
        print("Before Parsing criteria results:", resp)
        return _clean_and_parse_json(resp)


    async def generate_final_report(self, state: dict) -> dict:
        print("<<<<<<<< generate_final_report >3 chunks >>>>>>>>>>")
        resp = self.final_report_chain.invoke({
            "criteria_results": json.dumps(state["criteria_results"], indent=2),
            "relation_rag" : state["relation_rag"]
        })
        return resp
    

    async def final_report_formatter(self, state: dict) -> dict:
        # Use evaluated_report if present; otherwise, fall back to report
        evaluated = state['criteria']
        response = self.final_report_formater_chain.invoke({
            "evaluated_report": json.dumps(evaluated, indent=2) if not isinstance(evaluated, str) else evaluated
        })
        state["report"] = response
        state["status"] = "report_formatted"

        print("Final Report:", response)
        return state
    
    async def prepare_report(self, state):
        print("<<<<<<<< Prepare Report Agent >>>>>>>>>>")
        policy_chunks = state["policy_context"]
        application = state["application"]
        doc_name = state["doc_name"]

        if len(policy_chunks) <= 3:
            # Small policy: Generate report directly
            final_report = await self.generate_report(state)
            state["policy_context"] = "\n".join(policy_chunks)  # If needed by downstream nodes
        else:
            # Large policy: Multi-agent evaluation
            eval_tasks = [
                self.criteria_evaluation(chunk, application)
                for chunk in policy_chunks if chunk and not chunk.strip().startswith("---")
            ]
            criteria_results = await asyncio.gather(*eval_tasks)

            relation_rag = rag_tool(
                    "Retrieve all the eligibility criteria sections from the policy",
                    categories="final_logic",
                    policy_name=doc_name
            )

            print('Relation results from Rag:', relation_rag)

            relation_rag_state = {"criteria_results": criteria_results,"relation_rag": relation_rag}

            report = await self.generate_final_report(relation_rag_state)

            final_report = {
                "criteria_evaluations" : criteria_results,
                "final_evaluation" : report
            }
            # final_report = await self.final_report_formatter(state)
        
        state['criteria'] = final_report
        state["status"] = "generated"
        return state