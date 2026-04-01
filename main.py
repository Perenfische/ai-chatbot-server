from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
from openai import OpenAI

app = FastAPI()

# 🔐 Facebook page token
PAGE_ACCESS_TOKEN = "EAGBiyPUiZClABRDVkcofHw5Ia1IMaLuA9EzsvF8PZBFJRdiAZB1PXzfQXnfuhZArYhjr25zL9ok4GvgKpFUbNVSvjBNn2XBWdkY6nPeJ1nMrAUOqvPz8b3j92Bq9cwyeJZBNPB21cRXGCJGWZB4CXUGuROmiaj90RcUOzXgehRRLnFZA4oV0jjb0BLHKlvnCtXVqEjFcwZDZD"

# 🔐 Webhook verify token
VERIFY_TOKEN = "mytoken123"

# 🤖 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🏠 Test endpoint
@app.get("/")
def home():
    return {"message": "AI chatbot ажиллаж байна"}


# 🔐 Facebook webhook verify (GET)
@app.get("/webhook")
async def verify(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error", status_code=403)


# 📩 Facebook message авах (POST)
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "entry" in data:
        for entry in data["entry"]:
            for messaging in entry["messaging"]:
                sender_id = messaging["sender"]["id"]

                if "message" in messaging:
                    user_text = messaging["message"].get("text", "")

                    try:
                        # 🤖 AI response
                        response = client.chat.completions.create(
                            model="gpt-4.1-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a Mongolian sales assistant. Reply shortly, friendly, and help users choose products."
                                },
                                {
                                    "role": "user",
                                    "content": user_text
                                }
                            ]
                        )

                        reply = response.choices[0].message.content

                    except Exception as e:
                        reply = "Уучлаарай, AI хариу өгөхөд алдаа гарлаа."

                    send_message(sender_id, reply)

    return "ok"


# 📤 Facebook message илгээх
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    requests.post(url, json=payload)
