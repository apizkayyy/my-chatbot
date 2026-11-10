"""
RAG (Retrieval-Augmented Generation) helpers.

Flow for each customer message:
1. rewrite_query()  - turn vague follow-ups ("and how much?") into standalone questions
2. search()         - embed the question and rank knowledge chunks by dot-product similarity
3. build_context()  - keep chunks above SCORE_THRESHOLD and return them with the rewritten query

Knowledge is loaded from knowledge.txt (one chunk per paragraph) and embedded once at import time.
"""

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, SCORE_THRESHOLD, TOP_K, EMBED_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

def load_chunks(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return [c.strip() for c in text.split("\n\n") if c.strip()]


def embed_texts(texts: list[str]) -> list[list[float]]:
    result = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in result.data]


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def search(question: str, chunks: list[str], vectors: list[list[float]], top_k: int = 3):
    q_vec = embed_texts([question])[0]
    scored = [(dot(q_vec, v), chunk) for chunk, v in zip(chunks, vectors)]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]

_chunks = load_chunks("knowledge.txt")
_vectors = embed_texts(_chunks)

def rewrite_query(question: str, history: list) -> str:
    # history[0] is the system prompt; the last item is the current question
    previous = [m for m in history[1:-1] if m["role"] in ("user", "assistant")]
    if not previous:
        return question

    recent = previous[-6:]
    convo = "\n".join(f'{m["role"]}: {m["content"]}' for m in recent)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=60,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
    "You rewrite the customer's latest message into a standalone question for a cafe FAQ search. "
    "Replace pronouns and vague words (it, that, there, they, 'and on Monday?') "
    "with the specific topic from the conversation. "
    "Only leave the message unchanged if it already names its own topic. "
    "Return ONLY the rewritten question.\n\n"
    "Example:\n"
    "Conversation:\nuser: Do you have parking?\nassistant: Yes, at Lot 10, RM3 per hour.\n"
    "Latest message: And how much does it cost?\n"
    "Rewritten: How much does parking cost near the cafe?\n\n"
    "Example:\n"
    "Conversation:\nuser: Do you have parking?\nassistant: Yes, at Lot 10, RM3 per hour.\n"
    "Latest message: What time do you open?\n"
    "Rewritten: What time does the cafe open?"
),
            },
            {
                "role": "user",
                "content": f"Conversation:\n{convo}\n\nLatest message: {question}",
            },
        ],
    )
    return response.choices[0].message.content.strip()

def build_context(question: str, history: list) -> tuple[str, str]:
    search_question = rewrite_query(question, history)

    results = search(search_question, _chunks, _vectors, top_k=TOP_K)
    good = [chunk for score, chunk in results if score >= SCORE_THRESHOLD]

    context = "\n\n".join(good) if good else "No relevant information found."
    return context, search_question


if __name__ == "__main__":
    chunks = load_chunks("knowledge.txt")
    vectors = embed_texts(chunks)
    print(f"Embedded {len(chunks)} chunks. Type a question (or quit).\n")

    while True:
        question = input("Question: ")
        if question.lower() in ["quit", "exit"]:
            break

        for score, chunk in search(question, chunks, vectors):
            print(f"  {score:.3f} | {chunk[:70]}")
        print()