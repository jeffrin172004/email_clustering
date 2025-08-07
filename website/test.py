from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .email_fetcher import fetch_emails
from .utils import log_message
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_fixed
import json
from datetime import datetime
import re

load_dotenv()

# ---------------------------
# Define output structure
# ---------------------------
class ResearchResponse(BaseModel):
    cluster: List[int]                     # Cluster labels
    email: List[List[Tuple[str, str]]]     # [(email_id, body)] per cluster
    summary: List[str]                     # Summary per cluster

# ---------------------------
# Setup LangChain components
# ---------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

system_prompt = """
You are an expert research assistant tasked with clustering emails based on semantic similarity.

Steps:
1. Review all provided emails.
2. Group them into clusters (0-based indexing) based on semantic similarity.
3. For each cluster, list the (email_id, body) pairs.
4. Create a concise summary (50-150 words) for each cluster.

Input:
- A list of emails in the format:
  Email ID: <id>
  Email Body: <body>

Return:
- cluster: List of cluster numbers corresponding to each email.
- email: List of lists, where each inner list contains (email_id, body) tuples for a cluster.
- summary: List of summaries (one per cluster).

Use this format: {format_instructions}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("user", "All Emails:\n{all_emails}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = []
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# ---------------------------
# Retry wrapper for AI calls
# ---------------------------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def invoke_agent(query):
    """Invoke the LangChain agent with retry logic."""
    return agent_executor.invoke(query)

# ---------------------------
# Preprocess emails
# ---------------------------
def preprocess_emails(emails: List[dict]) -> str:
    """Convert fetched emails into a single formatted string for LLM."""
    formatted_emails = []
    for email in emails:
        email_id = str(email.get('from', ''))
        #email_id = email.get('sender', '')
        body = email.get('body', '').replace('\r\n', ' ').strip()
        if not body:
            continue
        formatted_emails.append(f"Email ID: {email_id}\nEmail Body: {body}")
    return "\n\n".join(formatted_emails)

# ---------------------------
# Main processing function
# ---------------------------
def process_emails(from_date: str, max_emails: int = 50) -> dict:
    """
    Fetch, process, and cluster emails from Gmail in a single LLM call.
    
    Args:
        from_date: Start date in YYYY-MM-DD format.
        max_emails: Maximum emails to process.

    Returns:
        dict: Clustered emails in ResearchResponse format.
    """
    try:
        # Validate date format
        datetime.strptime(from_date, '%Y-%m-%d')

        # Fetch emails
        emails = fetch_emails(from_date)
        if not emails:
            return {'cluster': [], 'email': [], 'summary': []}

        # Limit emails
        emails = emails[:max_emails]

        # Preprocess into one big string
        all_emails_str = preprocess_emails(emails)
        log_message(all_emails_str)     ##just for testing
        if not all_emails_str:
            return {'cluster': [], 'email': [], 'summary': []}

        # Create query for LLM
        query = {"all_emails": all_emails_str}

        # Single call to LLM
        raw_response = invoke_agent(query)
        output_string = raw_response.get("output")

        # Parse and validate
        parsed_output = json.loads(output_string)
        validated_output = ResearchResponse(**parsed_output)

        final_result = {
            'cluster': validated_output.cluster,
            'email': validated_output.email,
            'summary': validated_output.summary
        }

        # Log only final processed output
        log_message(f"Processed Output: {json.dumps(final_result, indent=2)}", level="info")

        return final_result

    except Exception as e:
        log_message(f"Error processing emails: {str(e)}", level="error")
        raise
