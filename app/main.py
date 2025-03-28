from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatMessage
from app.memory.stm import ShortTermMemory
from app.memory.ltm import LongTermMemory
from app.llm.gemini import GeminiLLM
from app.embeddings.google_embeddings import GoogleEmbeddings

app = FastAPI(
    title="AI Chatbot",
    description="Conversational chatbot using STM and LTM memory management",
    version="1.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Default single-user ID (no auth)
DEFAULT_USER = "default_user"

# Initialize components
stm = ShortTermMemory()
ltm = LongTermMemory()
llm = GeminiLLM()
embeddings = GoogleEmbeddings()

@app.post("/chat/stm", summary="Chat using Short-Term Memory", tags=["STM"])
async def chat_stm(message: ChatMessage):
    """
    Handles a chat message using Short-Term Memory (STM).
    
    Messages are only stored temporarily during the session.
    STM is cleared on page refresh or reset.
    """
    stm.add_message(DEFAULT_USER, message)
    history = stm.get_session(DEFAULT_USER)

    gemini_messages = [
        {"role": msg.role, "parts": [{"text": msg.content}]} for msg in history
    ]

    response_content = llm.generate_response(gemini_messages)
    stm.add_message(DEFAULT_USER, ChatMessage(role="assistant", content=response_content))

    return {"response": response_content}


@app.post("/chat/ltm", summary="Chat using Long-Term Memory", tags=["LTM"])
async def chat_ltm(message: ChatMessage):
    """
    Handles a chat message using Long-Term Memory (LTM).

    Retrieves similar past embeddings to provide personalized context.
    New message is saved into memory as a vector embedding.
    """
    query_embedding = embeddings.get_embedding(message.content)
    relevant_memories = ltm.retrieve_memory(query_embedding)

    context = "\n".join([mem["content"] for mem in relevant_memories])
    print("[LTM] Retrieved context:")
    print(context)

    combined_prompt = f"""
    Known background information about the user:

    {context}

    New user message:
    {message.content}
    """

    gemini_messages = [
        {"role": "user", "parts": [{"text": combined_prompt}]}
    ]

    response_content = llm.generate_response(gemini_messages)
    ltm.store_memory(message.content, query_embedding)

    return {"response": response_content}


@app.delete("/memory/delete", summary="Clear Long-Term Memory", tags=["LTM"])
async def delete_memory():
    """
    Deletes all records stored in Long-Term Memory (LTM).
    """
    ltm.delete_all_memories()
    return {"message": "All memory entries successfully deleted."}


@app.get("/session/clear", summary="Clear STM Session", tags=["STM"])
async def clear_session():
    """
    Clears all messages stored in the current Short-Term Memory (STM) session.
    """
    stm.clear_session(DEFAULT_USER)
    return {"message": "Session memory cleared."}


@app.on_event("shutdown")
def shutdown_event():
    """
    Gracefully closes the database connection when the server shuts down.
    """
    ltm.close()

