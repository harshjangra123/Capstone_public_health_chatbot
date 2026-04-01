# <-- All your nodes will live here (e.g., call_model, tool_nodes).
from app.llm import llm
from app.state import GraphState

def call_model(state: GraphState):
    """
    The primary node that calls the LLM.

    Args:
        state: The current graph state.

    Returns:
        A dictionary with the LLM's response.
    """
    messages = state["messages"]
    response = llm.invoke(messages)
    # We return a dictionary with the new message to add to the state
    return {"messages": [response]}



