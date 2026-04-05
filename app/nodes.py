# <-- All your nodes will live here (e.g., call_model, tool_nodes).
from app.llm import llm
from app.state import GraphState
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from langchain.tools import tool  
from langgraph.prebuilt import ToolNode 
from app.llm import llm
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

from app.routing_logic import get_best_dataset
from app.data_loader import fetch_dataset_by_id, json_to_text
from app.rag_pipeline import chunk_documents, create_vectorstore, retrieve_context

@tool
def fetch_dataset(query: str) -> str:
    """
    Use this tool for questions related to structured datasets like health, census, demographics, etc.
    It retrieves relevant information from dataset APIs using RAG.
    """

    try:
        # 1. routing
        resource_id = get_best_dataset(query)
        print("Selected dataset:", resource_id)

        # 2. fetch JSON
        data = fetch_dataset_by_id(resource_id)

        # 3. JSON → text
        documents = json_to_text(data)

        # 4. chunk
        chunks = chunk_documents(documents)

        # 5. create TEMP vector DB
        vectorstore = create_vectorstore(chunks)

        # 6. retrieve relevant context
        context = retrieve_context(vectorstore, query)

        return context

    except Exception as e:
        return f"Dataset tool error: {str(e)}"

@tool
def search_web(query: str) -> str:
    """
    Search the web for real-time or unknown information.
    Use this when the question involves recent events, news, or facts not in training data.
    """
    response = tavily.search(query=query, max_results=3)

    results = []
    for r in response["results"]:
        results.append(f"{r['title']}: {r['content']}")

    return "\n".join(results)



# bind tools
llm_with_tools = llm.bind_tools([search_web, fetch_dataset])

def call_model(state: GraphState):
    """
    The primary node that calls the LLM.

    Args:
        state: The current graph state.

    Returns:
        A dictionary with the LLM's response.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)  
    return {"messages": [response]}


tool_node = ToolNode([search_web, fetch_dataset])