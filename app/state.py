# Defines the `GraphState` (the memory structure).

from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage


# 1. Define the state for our graph
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: A list of messages in the conversation.
    """
    messages: Annotated[list[AnyMessage], lambda x, y: x + y]