# <-- All your nodes will live here (e.g., call_model, tool_nodes).
from app.llm import llm, prompt
from app.state import GraphState
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from langchain.tools import tool  
from langgraph.prebuilt import ToolNode 
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

from app.routing_logic import get_best_dataset
from app.data_loader import fetch_dataset_by_id, json_to_text
from app.rag_pipeline import chunk_documents, create_vectorstore, retrieve_context

@tool
def fetch_dataset(query: str) -> str:
    """
    Use this tool ONLY for structured, numerical, and statistical health datasets.

    This tool is designed for:
    - government or survey-based health data
    - numerical reports (counts, percentages, prevalence)
    - tabular data like:
        - HIV prevalence by state
        - diabetes patient statistics
        - population health metrics

    Examples of when to use:
    - "HIV prevalence in Delhi"
    - "number of diabetes patients in India"
    - "state-wise health statistics"
    - "percentage of infected people"

    DO NOT use this tool for:
    - latest or recent developments
    - new medical tests or treatments
    - current trends or innovations
    - market-related queries
    - general medical advice

    Examples of when NOT to use:
    - "latest test for diabetes"
    - "new treatment for HIV"
    - "best medicine for diabetes"

    This tool is ONLY for static, numerical dataset-based information.
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

        return context[:800]

    except Exception as e:
        return f"Dataset tool error: {str(e)}"

@tool
def search_web(query: str) -> str:
    """
    Search the web for real-time, recent, or evolving information.

    Use this tool when the user asks about:
    - latest developments, trends, or technologies
    - new medical tests, treatments, or innovations
    - current news or recent updates
    - market availability of products or services
    - anything that may have changed recently

    Examples:
    - "latest test available for diabetes"
    - "new HIV treatment methods"
    - "recent trends in cancer research"
    - "current price of bitcoin"
    - "weather in Delhi today"

    DO NOT use this tool for:
    - structured statistical datasets
    - historical numerical data from government datasets
    - queries about counts, percentages, or tabular reports

    This tool is best for dynamic, real-world, and up-to-date information.
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
    chain = prompt | llm_with_tools
    response = chain.invoke({"messages": messages})  
    return {"messages": [response]}


tool_node = ToolNode([search_web, fetch_dataset])