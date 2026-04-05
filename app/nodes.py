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
llm_with_tools = llm.bind_tools([search_web]) 

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


tool_node = ToolNode([search_web])
