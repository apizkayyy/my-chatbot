import json

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_TOKENS
from db import init_db, save_message, load_history, list_sessions

from rag import build_context

from memory import build_history

app = FastAPI()
client = OpenAI(api_key=OPENAI_API_KEY)

init_db()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    save_message(req.session_id, "user", req.message)
    history = build_history(req.session_id)

    context, search_question = build_context(req.message, history)
    history[-1] = {
        "role": "user",
        "content": (
            f"CONTEXT:\n{context}\n\n"
            f"CUSTOMER MESSAGE: {req.message}\n"
            f"WHAT THE CUSTOMER MEANS: {search_question}"
        ),
    }
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=MAX_TOKENS,
        messages=history,
    )

    reply = response.choices[0].message.content
    save_message(req.session_id, "assistant", reply)

    return ChatResponse(reply=reply)


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    save_message(req.session_id, "user", req.message)
    history = build_history(req.session_id)

    context, search_question = build_context(req.message, history)
    history[-1] = {
        "role": "user",
        "content": (
            f"CAFE INFORMATION (retrieved for this message):\n{context}\n\n"
            f"CUSTOMER MESSAGE: {req.message}\n"
            f"WHAT THE CUSTOMER MEANS: {search_question}"
        ),
    }

    def generate():
        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            max_tokens=MAX_TOKENS,
            messages=history,
            stream=True,
        )

        reply = ""
        for chunk in stream:
            piece = chunk.choices[0].delta.content
            if piece:
                reply += piece
                yield f"data: {json.dumps(piece)}\n\n"

        save_message(req.session_id, "assistant", reply)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/history/{session_id}")
def show_history(session_id: str):
    return load_history(session_id)


@app.get("/sessions")
def show_sessions():
    return list_sessions()

from db import get_summary

@app.get("/summary/{session_id}")
def show_summary(session_id: str):
    summary, last_id = get_summary(session_id)
    return {"summary": summary, "covers_up_to_message_id": last_id}