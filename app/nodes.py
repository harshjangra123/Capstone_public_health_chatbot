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

from langchain_community.vectorstores import Chroma
from app.embeddings import embedding_model

vectorstore = Chroma(
    persist_directory="csv_vector_db",
    embedding_function=embedding_model
)

from langchain_core.messages import AIMessage

@tool
def search_dataset(query: str) -> str:
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
        print("🔍 Query:", query)

        docs = vectorstore.similarity_search(query, k=1)

        if not docs:
            return "No relevant dataset information found."

        context = "\n".join([doc.page_content for doc in docs])

        if not context.strip():
            print("no context found ❌")
            return "No useful information found in dataset."

        # return context[:1000]
        print("context found ")
        print(context[:800])
        return f"Here is relevant dataset information:\n\n{context[:800]}"

    except Exception as e:
        print("❌ ERROR:", str(e))
        return "Dataset tool failed. Please try again."

@tool
def search_web(query: str) -> str:
    """
    Search the web for real-time or recent information.

    IMPORTANT:
    - You MUST pass a 'query' parameter as a string.
    - Example: {"query": "latest diabetes treatment 2025"}

    Use ONLY when:
    - question is about latest news
    - recent updates
    - current events
    - latest medical research

    DO NOT use for:
    - historical data
    - statistics
    - dataset queries (use search_dataset instead)
    """
    response = tavily.search(query=query, max_results=4)

    results = []
    for r in response["results"]:
        results.append(f"{r['title']}: {r['content']}")

    return "\n".join(results)



# bind tools
llm_with_tools = llm.bind_tools([search_web, search_dataset])

def call_model(state: GraphState):
    """
    The primary node that calls the LLM.

    Args:
        state: The current graph state.

    Returns:
        A dictionary with the LLM's response.
    """
    try:
        messages = state["messages"]

        chain = prompt | llm_with_tools
        response = chain.invoke({"messages": messages})

        return {"messages": [response]}

    except Exception as e:
        print("❌ LLM ERROR:", str(e))

        return {
            "messages": [
                AIMessage(content="Something went wrong. Please try again.")
            ]
        }


tool_node = ToolNode([search_web, search_dataset])