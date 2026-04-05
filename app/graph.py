# <-- The main graph logic. Builds and compiles the graph.

from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.nodes import call_model , tool_node

# This is where we define the flow of the conversation.
workflow = StateGraph(GraphState)

# Add our single nodes
workflow.add_node("llm", call_model)
workflow.add_node("tools",tool_node)

# Set the entry point and the end point.
workflow.set_entry_point("llm")

#CONDITIONAL ROUTING
def route_tools(state):
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges(
    "llm",
    route_tools
)

# loop back after tool
workflow.add_edge("tools", "llm")

# Compile the graph into a runnable object
graph = workflow.compile()
