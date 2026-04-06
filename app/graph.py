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
    messages = state["messages"]
    last_message = messages[-1]

    # count tool calls
    tool_calls_count = sum(
        1 for m in messages
        if hasattr(m, "tool_calls") and m.tool_calls
    )

    #if LLM wants tool → go to tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    #if tools already used → FORCE FINAL ANSWER
    if tool_calls_count > 2:
        return END

    return END

workflow.add_conditional_edges(
    "llm",
    route_tools
)

# loop back after tool
workflow.add_edge("tools", "llm")

# Compile the graph into a runnable object
graph = workflow.compile()

with open('mermaid.txt', 'w') as f:
    f.write(graph.get_graph().draw_mermaid())