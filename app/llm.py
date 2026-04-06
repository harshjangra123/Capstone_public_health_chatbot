# Initializes the LLM (Groq model).

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

system_prompt = """You are a helpful assistant.

STRICT TOOL USAGE RULES:
- search_web requires: {{"query": "your question"}}
- search_dataset requires: {{"query": "your question"}}

NEVER generate:
- cursor
- id

Always use correct format.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)