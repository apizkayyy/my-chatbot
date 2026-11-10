from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT, SUMMARY_TRIGGER, KEEP_RECENT
from db import load_unsummarized, save_summary

client = OpenAI(api_key=OPENAI_API_KEY)


def summarize(old_summary: str, rows: list) -> str:
    convo = "\n".join(f"{role}: {content}" for _, role, content in rows)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=200,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You maintain a short memory of a chat. "
                    "Merge the existing summary with the new messages into ONE updated summary. "
                    "Keep: the customer's name, preferences, dietary needs, bookings, "
                    "and what they asked about. Drop greetings and filler. "
                    "Record facts about the customer and the topics they asked about. "
                    "Do NOT record the assistant's 'I don't know' or 'call the cafe' replies. "
                    "Maximum 5 short lines. Return ONLY the summary."
                ),
            },
            {
                "role": "user",
                "content": f"Existing summary:\n{old_summary or '(none)'}\n\nNew messages:\n{convo}",
            },
        ],
    )
    return response.choices[0].message.content.strip()


def build_history(session_id: str) -> list:
    summary, rows = load_unsummarized(session_id)

    if len(rows) > SUMMARY_TRIGGER:
        old, recent = rows[:-KEEP_RECENT], rows[-KEEP_RECENT:]
        summary = summarize(summary, old)
        save_summary(session_id, summary, old[-1][0])
        rows = recent

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    if summary:
        history.append(
            {"role": "system", "content": f"Summary of the earlier conversation:\n{summary}"}
        )
    for _, role, content in rows:
        history.append({"role": role, "content": content})
    return history