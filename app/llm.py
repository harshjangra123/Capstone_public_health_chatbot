# Initializes the LLM (Groq model).

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv


load_dotenv()

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)