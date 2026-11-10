from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_TOKENS

client = OpenAI(api_key=OPENAI_API_KEY)

history = [
    {
        "role": "system",
        "content": (
            "You are Kopi, a friendly assistant for a small cafe in Kuala Lumpur. "
            "Only answer questions about the cafe, its menu, and opening hours. "
            "If asked about anything else, politely say you can only help with cafe questions. "
            "Opening hours: 8am to 6pm, closed on Mondays. "
            "When asked about hours, always mention opening time, closing time, and that we are closed on Mondays. "
            "Address: 12 Jalan Bukit Bintang, Kuala Lumpur. "
            "Menu: Latte RM12, Americano RM9, Nasi Lemak RM10, Croissant RM8. "
            "If you don't know the answer, say so and suggest the customer call the cafe. "
            "Reply in short, warm sentences."
        ),
    }
]

while True:
    user_input = input("You: ")

    if user_input.lower() in ["quit", "exit"]:
        print("Bye!")
        break

    history.append({"role": "user", "content": user_input})

    ##stream=True,so the output will be sent piece by piece, not wait until finish to send whole output
    stream = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=MAX_TOKENS,
        messages=history,
        stream=True,
    )

    print("Bot: ", end="", flush=True)
    reply = ""

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            print(piece, end="", flush=True)
            reply += piece

    print()
    history.append({"role": "assistant", "content": reply})