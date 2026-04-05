# This file does:
# 1. Defines API endpoint (/api/chat)
# 2. Takes user input
# 3. Stores conversation history
# 4. Sends data to LangGraph
# 5. Returns AI response
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph import graph # Import the compiled graph

chat_router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str # To maintain conversation history per session

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Dictionary to store conversation history for each session
# In a real application, this would be a database or a more robust state management system
session_histories = {}

@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles a chat request, invoking the LangGraph chatbot.
    """
    session_id = request.session_id
    user_message = request.message

    # Retrieve or initialize conversation history for the session
    if session_id not in session_histories:
        session_histories[session_id] = []
    
    conversation_history = session_histories[session_id]

    # Add the current user message to the history
    conversation_history.append(HumanMessage(content=user_message))

    # Invoke the graph with the full history
    inputs = {"messages": conversation_history}
    result = graph.invoke(inputs)
    
    # Update history with the AI's response
    session_histories[session_id] = result['messages']
    
    # Get the AI's last response
    ai_response = session_histories[session_id][-1].content

    return ChatResponse(
        response=ai_response,
        session_id=session_id
    )



