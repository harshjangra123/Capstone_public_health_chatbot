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

You have access to external tools that can help you answer certain questions.

- Use tools when necessary.
- Do not manually format tool calls.
- Let the system handle tool execution.

For general questions, answer normally.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)