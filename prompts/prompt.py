from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from langchain.prompts.chat import HumanMessagePromptTemplate



def application_analyzing_prompt():
    """
    when policy chunks are less thank 3,
    Recives application data, policy chunk and genrates eligibility verdict.
    """
    system = SystemMessage(
        content=(
            "You are an Expert Policy Criteria Evaluator."
            "Evaluate strictly based on the provided `Application Details` and `Policy Context`."
            "Review the policy context to identify main and sub eligibility criterion specified within the policy. For each sub criterion, cross-reference the corresponding application details to ensure alignment."
            "Do NOT introduce any external information or assumptions. "
            "Produce EXACTLY valid JSON with two keys: `criteria_evaluations` and `final_verdict`. "
            "All reasoning must refer only to the `Application Details` and `Policy Context`."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Application Details:**
        {application_details}

        **Policy Context:**
        {policy_context}
        ```

        ### Instructions (STRICT):
        1. **criteria_evaluations**: A JSON array where each object corresponds to one policy criterion. Each object must include:
           - **criterion**: the exact title of the criterion.
           - **analysis**:  A concise sentence explaining compliance, non-compliance or need of additional info, strictly based on the provided Application Details and Policy Context.
           - **verdict**: one of "Eligible", "Ineligible", "Further Review Needed"
        2. **final_evaluation**: must include: 
            - **final_verdict**: either `"Grant"` or `"Deny"`
            - **final_analysis**:  one-sentence justification summarizing the overall evaluation across all criteria.
        
        **OUTPUT**:
        ```json
        {{
          "criteria_evaluations": [
            {{ 
                "criterion": "...", 
                "analysis": "..." 
                "verdict": "...",
            }},
            ...
          ],
          "final_evaluation": 
            {{
                "final_verdict": "<Grant|Deny>",
                "final_analysis": "..."
            }}
        }}
        ```
        """
    )
    return ChatPromptTemplate.from_messages([system, human])


def report_feedback_agent_prompt():
    """
    Reviews the generated report.
    Provides any feedback if needed.
    """
    system = SystemMessage(
        content=(
            "You are an expert Policy Report Reviewer."
            "Validate the `Generated Report` against the `Policy Context` and `Application Details` to identify any errors, inconsistencies, or inaccurate conclusions."
            "Do NOT add any new text—only respond with one of two exact outputs."
        )
    )
    human = HumanMessagePromptTemplate.from_template(

        """
        **Application Details:**
        {application_details}

        **Policy Context:**
        {policy_context}

        **Generated Report:**
        {generated_report}

        ### Instructions:
        - If any criterion from the Policy Context is missing in the criteria_evaluations section of the Generated Report, or if any claim in the report lacks supporting evidence, respond exactly as follows:
          ```text
          feedback:
          <point wise, concise feedback to improve or correct the report>
          ```
        - If no issues are found, respond exactly with:
          ```text
          approved
          ```
        """
    )
        #       Missing criteria: <comma-separated list>
        #   Unsupported claims: <comma-separated list>
    return ChatPromptTemplate.from_messages([system, human])


def revise_report_prompt():
    system = SystemMessage(
        content=(
            "You are an Expert Policy Report Reviser."
            "Improve the `Original Report` to correct parts of the report or improve the report as per the `Feedback` provided. "
            "Do not include markdown code fences, application details or any additional commentary in the output."
            "Return the complete improved report in the original structure and format."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Application Details:**
        {application_details}

        **Original Report:**
        {original_report}

        **Policy Context:**
        {policy_context}

        **Feedback:**
        {feedback}
    
        **Output:**  
        Provide the revised report below, strictly following the original JSON structure and formatting
        """
    )
    return ChatPromptTemplate.from_messages([system, human])


####################################################################################################
def criteria_evaluation_prompt():
    """
    When criteira is more than 3,
    One policy criteria will be processed here,
    and will generate verdict for one criteria.
    """
    system = SystemMessage(
        content=(
            "You are an Expert Policy Criteria Evaluator."
            "Your task is to assess a single policy criterion using the provided `Policy Context` and `Application Data`. "
            "Review the `Policy Context` to identify eligibility criterion specified within the policy. For each criterion, cross-reference the corresponding `Application Data` to ensure alignment."
            "Do NOT add extra fields or external info."
            "Do NOT include any markdown, backticks, or extra fields—just the raw JSON."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Policy Context:**
        {section}

        **Application Data:**
        {application_data}

        ### Instructions (STRICT):
        1. **criterion**: the exact title of the criterion.
        2. **analysis**: A concise sentence that explains the verdict, based only on the `Policy Context` and `Application Data` provided. 
        3. **verdict**: one of "Eligible", "Ineligible", "Further Review Needed"

        **OUTPUT**:  
        ```json
        {{
            "criterion": "...",
            "analysis": "..."
            "verdict": "...",
        }}
        ```
        """
    )
    return ChatPromptTemplate.from_messages([system, human])



def final_report_prompt():
    system = SystemMessage(
        content=(
            "You are an Expert Eligibility Report Generator. "
            "Based solely on the provided **Criteria Evaluation** and **Overview and Relationships Between Criteria**, "
            "your task is to generate a concise eligibility decision. "
            "Do NOT introduce any external information or assumptions."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Criteria Evalutation:**
        {criteria_results}

        **Overview and Relationship between criteria's:**
        {relation_rag}

        ### Instructions (STRICT):
        1. **final_verdict**: either `"Grant"` or `"Deny"`
        2. **final_analysis**:  one-sentence justification summarizing the overall evaluation across all criteria.

        **Output:**  
        Produce only the report text, using these headings and bullet‐styles—no JSON, no markdown fences, no extra sections.
        {{
            "final_verdict": "<Grant|Deny>",
            "final_analysis": "..."
        }}
        """
    )
    return ChatPromptTemplate.from_messages([system, human])




##########################################################################


def report_formatter_prompt():
    system = SystemMessage(
        content=(
            "You are an Expert Report Formatter. "
            "Your task is to synthesize a clear and concise eligibility report following `Report Structure` using ONLY the information provided in `Evaluated Report`"
            "Do NOT introduce any external information or assumptions."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Evaluated Report :**
        {evaluated_report}

        ### Report Structure (follow exactly):

        ## Introduction  
        A concise paragraph (2–3 sentences) summarizing the applicant’s profile and the scope of this eligibility evaluation.

        ## Detailed Criteria Analysis  
        For each criterion in `refined_results`, include:
        - **Criterion:** [criterion title]  
          **Verdict:** [Eligible /Ineligible / Further Review Needed]  
          **Justification:** [two or three sentences, citing only the inputs]  
        
        ## Overall Recommendation  
        A final paragraph (1–2 sentences) stating either “Approve application,” “Deny application,” or “Request additional information,” with a brief policy-based rationale.

        **Output:**  
        Produce only the report text, using these headings and bullet‐styles—no JSON, no markdown fences, no extra sections.
        """
    )
    return ChatPromptTemplate.from_messages([system, human])



################################################################
def feedback_classification_prompt():
    system = SystemMessage(
        content=(
            "You are a Feedback Classifier. "
            "Your task is to analyze the given feedback and determine if it is a query for more information or a request to revise the report. "
            "Use the following guidelines: "
            "Classify as 'query' if the feedback asks a question about the policy, application, or report (e.g., 'What does this mean?' or 'Can you clarify this?'). "
            "Classify as 'revision' if the feedback suggests changes, corrections, or improvements to the report (e.g., 'This section is unclear, please revise','Add more details here' and 'This criteria/report evaluation seems wrong or mistaken assumption)."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Feedback:**
        {feedback}

        Classify the above feedback as either 'query' or 'revision'.

        **Output:**
        Respond with only 'query' or 'revision'.
        """
    )
    return ChatPromptTemplate.from_messages([system, human])


def handle_query_prompt():
    system = SystemMessage(
        content=(
            "You are a Query Handler. "
            "Your task is to provide an informative response to the given feedback using only the available context from the policy, application data, and current report. "
            "Do not introduce external information or assumptions."
        )
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        **Feedback:**
        {feedback}

        **Policy Context:**
        {policy_context}

        **Application Data:**
        {application}

        **Current Report:**
        {report}

        Provide a concise and informative response to the query.

        **Output:**
        Produce only the response text—no extra sections or formatting beyond plain text.
        """
    )
    return ChatPromptTemplate.from_messages([system, human])






###########################################################################

# @MADHU
def split_policy_prompt(policy_text: str):
    prompt = f"""
    You are a Policy Segmentation Assistant specialized in identifying and classifying policy documents.
    Below is a policy text. Your task is to split it into distinct parts based on the table of content and return it as a JSON.

    Policy:
    {policy_text}

    ### Requirements:
    1. Identify each section by its heading.
    2. Extract the full content under each heading.
    3. Preserve the original wording and order.
    4. Make sure the words are correct.
    5. Return JSON only and dont return anything else.
    6. Make JSON structure is correct.
    """
    return prompt

# @MADHU
def extract_metadata_prompt(policy_text: str):
    prompt = f"""
    You are a expert at analyzing documents and generating metadata for the document.
    Given a policy context and its heading, extract the following information:

    1. Summary – Provide a concise summary (under 50 token) of the policy context.
    2. category – Strictly classify the policy context as one of the following:
    'info' – If the passage provides general information about a benefit or service's eligibility. ex: 'BACKGROUND', 'PROCESSING INSTRUCTIONS' .
    'criteria' – If the passage lists specific rules, conditions, or qualifications needed to be eligible.
    'example' – If the passage provides an example or scenario illustrating eligibility determination.

    Return in JSON format.

    ### Policy:
    {policy_text}
    """
    return prompt


# @MADHU
def generate_policy_logic_prompt(criterion_list:list[str], policy:str) -> str:
    prompt = f"""
    You are a Policy Relationship Extractor.
    
    Your task:
    1. Read the entire policy text I provide.
    2. Identify each separate section or criterion (e.g. “Criterion 1: Income”, “Section B: Residency”, etc.).
    3. Determine how they relate to one another logically—i.e. which criteria are:
        • INDEPENDENT (stand alone criteria is not affected or affects other criteria)
        • DEPENDENT (depends on other critiera, if X then Y or only one of a group needs to be met)
    4. Produce a very concise summary (no more than 150 words) that:
        • Lists each criterion/section by name.
        • States its role (INDEPENDENT/DEPENDENT).
        • Describes its relationship in plain-English bullet points.
    
    Sample Output format:

    **Bulleted list**  
    - **<Criterion 1> (INDEPENDENT):** Must be met.  
    - **Criterion 2 (DEPENDENT):** dependent on Criterion 3;  At least one must be met.  
    - **Criterion 2 (DEPENDENT):** dependent on Criterion 2;  At least one must be met.  
    - **Criterion 4 (DEPENDENT):** only if Criterion 5 is met or Criterion 6 is not met; Only required if Criterion 6 is not met or Criterion 5 is met. 

    Note: replace <Criterion N> with criterion name

    #### List of criterion names:
    {criterion_list}

    #### Policy text:
    {policy}
    """

    return prompt

