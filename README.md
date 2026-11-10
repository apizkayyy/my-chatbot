# Chatbot

A streaming AI chatbot, built with **FastAPI** and the **OpenAI API**.
Built step by step to learn how LLM chatbots work under the hood.

## Features

- Real-time streaming replies over Server-Sent Events (SSE)
- Per-session conversation memory stored in SQLite (survives server restarts)
- Browser chat UI with Markdown rendering (sanitized with DOMPurify)
- Session ID saved in `localStorage`, so a page refresh keeps the conversation
- System prompt with role, scope, knowledge, and "I don't know" handling
- Terminal version for quick experiments

## RAG Pipeline

The bot answers from `knowledge.txt` instead of a hard-coded prompt.

- **Chunking:** one paragraph per topic
- **Embeddings:** OpenAI `text-embedding-3-small`, computed once at startup
- **Retrieval:** dot-product similarity, top 3 chunks, filtered by a score threshold (0.25) so off-topic questions get "I don't know" instead of a made-up answer
- **Query rewriting:** follow-ups like "And how much does it cost?" are rewritten using chat history before searching ("How much does parking cost?"). Without this, retrieval lost the topic on follow-up questions.
- **Rewritten query is also passed to the answering model**, which fixed contradictory "I don't know, but..." answers.

## Conversation memory

- Full history is always stored in SQLite and shown in the UI
- Only a rolling summary plus the most recent messages are sent to the model, which keeps cost and latency flat as chats grow
- The summarizer is told what to keep (name, dietary needs, bookings) and not to record "I don't know" replies

## Tech stack

Python, FastAPI, Uvicorn, OpenAI API, SQLite, vanilla JavaScript

## How it works

The LLM API is stateless. Every request sends the full message history,
so "memory" is just the app storing messages and resending them.

```
Browser  --POST /chat/stream-->  FastAPI  --history-->  OpenAI API
   ^                                |                        |
   |------- SSE chunks -------------|<------ token stream ---|
                                    |
                                 SQLite (messages table)
```

## Project structure

```
app.py           FastAPI app and endpoints
db.py            SQLite helpers (save and load messages)
config.py        Settings and system prompt
chat.py          Terminal chatbot version
index.html       Browser chat UI
view_db.py       Small script to inspect chat.db
knowledge.txt    Knowledge base for the RAG (one topic per paragraph)
rag.py           RAG pipeline: chunking, embeddings, similarity search, query rewriting
memory.py        Store the summarize conversation
```

## Getting started

```bash
git clone https://github.com/apizkayyy/my-chatbot.git
cd chatbot

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then put your real OpenAI key in .env

uvicorn app:app --reload
```

Open http://127.0.0.1:8000

## API endpoints

| Method | Path                    | Description                  |
|--------|-------------------------|------------------------------|
| POST | `/chat`                 | Full reply as JSON           |
| POST | `/chat/stream`          | Streamed reply (SSE)         |
| GET | `/history/{session_id}` | Stored conversation          |
| GET | `/sessions`             | List of session IDs          |
| GET | `/summary/{session_id}` | List summary of conversation |


Request body for both POST endpoints:

```json
{ "session_id": "ali", "message": "How much is a latte?" }
```

## Roadmap

- [x] Phase 1: streaming chatbot, FastAPI, SQLite memory, web UI
- [x] Phase 2: RAG over documents (chunking, embeddings, retrieval)
- [x] Trim or summarize long conversations to control cost
- [ ] Docker deployment
- [ ] Tool calling (e.g. check order status)

## Notes

- Debug endpoints (`/history`, `/sessions`) are for development. Protect or remove them in production.
- Never commit `.env` or `chat.db`.

## License

MIT, see [LICENSE](LICENSE).