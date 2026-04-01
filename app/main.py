from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from app.api.chat_routes import chat_router

app = FastAPI(
    title="LangGraph Chatbot API",
    description="A FastAPI application for a LangGraph-powered chatbot.",
    version="1.0.0"
)

# Add CORS middleware
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the LangGraph Chatbot API"}
