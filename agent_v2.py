import logging
from langgraph.graph import StateGraph, END
from llm.llm_agent import LLMAgents
from utils.log_utils.logger_instances import app_logger

# from prompts.prompt import policy_context
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 
class LangGraphWorkflow:
    def __init__(self, agents: LLMAgents):
        self.agents = agents
        self.graph = self._build_graph()

    # Function to classify feedback
    async def classify_feedback_node(self, state):
        feedback = state["feedback"]
        classification = await self.agents.classify_feedback(feedback)
        state["feedback_type"] = classification
        if classification == "query":
            state["status"] = "query"
        elif classification == "revision":
            state["status"] = "needs_revision"
        else:
            raise ValueError(f"Invalid classification: {classification}")
        return state

    def _router_start(self, state):
        app_logger.log(f"Routing from Start, is_feedback_revision={state.get('is_feedback_revision')}")

        # If there’s feedback (and we haven’t yet classified it), send it to the classifier
        if state.get("feedback") and not state.get("feedback_type"):
            return "ClassifyFeedback"
        # If it’s a revision‐by‐feedback, go straight to ReviseReport
        if state.get("is_feedback_revision", False):
            return "ReviseReport"
        # Otherwise, this is a fresh upload
        return "PrepareReport"

    def _router(self, state):
        app_logger.log(f"Router checking state: status={state.get('status')}, revision_count={state.get('revision_count', 0)}/{state.get('max_revisions', 3)}")
        if state.get("is_feedback_revision", False):
            app_logger.log("Feedback revision complete, ending flow")
            return END
        if state.get("revision_count", 0) >= state.get("max_revisions", 3):
            if state.get("status") != 'report_formatted':
                app_logger.log(f"Maximum revisions reached ({state.get('max_revisions')})")
                return "FormatReport"
            elif state.get("status") == 'report_formatted':
                return END

        status = state["status"]
        if status == "generated":
            app_logger.log("Status=generated, routing to ReviewReport")
            return "ReviewReport"
        elif status == "needs_revision":
            app_logger.log("Status=needs_revision, routing to ReviseReport")
            return "ReviseReport"
        elif status == "revised":
            app_logger.log("Status=revised, routing to ReviewReport")
            return "ReviewReport"
        elif status == "approved_by_main":
            app_logger.log("Status=approved_by_main, formatting report")
            return "FormatReport"
        elif status == "report_formatted":
            app_logger.log("Status=report_formatted, ending flow")
            return END

    def _build_graph(self):
        builder = StateGraph(dict)
        builder.add_node("Start", lambda state: state) 
        builder.add_node("PrepareReport", self.agents.prepare_report)
        builder.add_node("ReviewReport", self.agents.review_report)
        builder.add_node("ReviseReport", self.agents.revise_report)
        builder.add_node("FormatReport", self.agents.final_report_formatter)
        
        builder.add_node("ClassifyFeedback", self.classify_feedback_node)
        builder.add_node("HandleQuery", self.agents.handle_query)

        builder.set_entry_point("Start")
    
        # Conditional edges from ClassifyFeedback
        builder.add_conditional_edges("Start", self._router_start)
        builder.add_conditional_edges("ClassifyFeedback", lambda state: state["status"], {
            "query": "HandleQuery",
            "needs_revision": "ReviseReport"
        })
        builder.add_edge("HandleQuery", END)  # Query handling ends the flow

        builder.add_conditional_edges("PrepareReport", self._router)
        builder.add_conditional_edges("ReviewReport", self._router)
        builder.add_conditional_edges("ReviseReport", self._router)
        builder.add_conditional_edges("FormatReport", self._router)

        return builder.compile()
    
    def _logged(self, fn, name):
        async def wrapper(state):
            app_logger.log(f"--- Entering agent: {name} ---")
            result = await fn(state)
            app_logger.log(f"--- Exiting agent: {name} with status={result.get('status')} revision_count={result.get('revision_count')} ---")
            return result
        return wrapper

    async def invoke(self, state):
        app_logger.log(f"Starting workflow invoke with initial state: {state}")
        result = await self.graph.ainvoke(state)
        app_logger.log(f"Workflow completed with final state: {result}")
        return result



    
