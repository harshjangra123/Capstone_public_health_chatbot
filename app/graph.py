# <-- The main graph logic. Builds and compiles the graph.

from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.nodes import call_model

# This is where we define the flow of the conversation.
workflow = StateGraph(GraphState)

# Add our single node
workflow.add_node("llm", call_model)

# Set the entry point and the end point.
# For now, it's a simple loop: the user talks, the LLM responds.
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)

# Compile the graph into a runnable object
graph = workflow.compile()