from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
from openai import OpenAI

app = FastAPI()

# 🔐 VERIFY TOKEN (Meta webhook)
VERIFY_TOKEN = "mytoken123"

# 🔐 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔐 Page token mapping
PAGE_TOKENS = {
    "1090689544121845": os.getenv("APEXCORE_AI"),
    "122098392890004279": os.getenv("STORE_ONLINE_SHOP")
}

# 🧠 Барааны мэдээлэл (түр MVP)
PRODUCTS = {
    "122098392890004279": [
        {"name": "iPhone 15 Pro", "price": "5,000,000₮"},
        {"name": "Samsung S23", "price": "3,500,000₮"},
        {"name": "AirPods Pro", "price": "800,000₮"},
        {"name": "Smart Watch", "price": "600,000₮"}
    ]
}

# 🔍 VERIFY ENDPOINT (Meta шалгах үед)
@app.get("/webhook")
async def verify(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error", status_code=403)


# 💬 MESSAGE RECEIVE
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "entry" in data:
        for entry in data["entry"]:
            page_id = entry["id"]  # 🔥 ЯМАР PAGE гэдгийг эндээс авна

            for messaging in entry["messaging"]:
                sender_id = messaging["sender"]["id"]

                if "message" in messaging:
                    user_text = messaging["message"].get("text", "")

                    # 🤖 AI + Product reply
                    reply = generate_reply(page_id, user_text)

                    # 📤 Send message
                    send_message(page_id, sender_id, reply)

    return "ok"


# 🤖 AI + БАРАА ЛОГИК
def generate_reply(page_id, user_text):
    try:
        product_list = PRODUCTS.get(page_id, [])

        product_text = ""
        if product_list:
            product_text = "\n".join(
                [f"- {p['name']} ({p['price']})" for p in product_list]
            )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
Та Монгол хэл дээр хариулдаг онлайн дэлгүүрийн борлуулалтын assistant.

Бараанууд:
{product_text}

Хэрэглэгчид тусалж, товч, ойлгомжтой, найрсаг хариул.
"""
                },
                {"role": "user", "content": user_text}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return "Уучлаарай, AI хариу өгөхөд алдаа гарлаа."


# 📤 MESSAGE SEND
def send_message(page_id, recipient_id, text):
    token = PAGE_TOKENS.get(page_id)

    if not token:
        print("TOKEN NOT FOUND FOR PAGE:", page_id)
        return

    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={token}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    requests.post(url, json=payload)


# 🧪 TEST
@app.get("/")
def home():
    return {"message": "AI chatbot ажиллаж байна 🚀"}
