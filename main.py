from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
import json
from openai import OpenAI

app = FastAPI()

# 🔐 VERIFY TOKEN
VERIFY_TOKEN = "mytoken123"

# 🔐 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔐 Page Tokens
PAGE_TOKENS = {
    "1090689544121845": os.getenv("APEXCORE_AI"),
    "122098392890004279": os.getenv("STORE_ONLINE_SHOP")
}

# 📦 Load products
def load_products():
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)

PRODUCTS = load_products()


# 🔍 VERIFY ENDPOINT
@app.get("/webhook")
async def verify(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("error", status_code=403)


# 💬 WEBHOOK
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "entry" in data:
        for entry in data["entry"]:
            page_id = entry["id"]

            for messaging in entry["messaging"]:
                sender_id = messaging["sender"]["id"]

                if "message" in messaging:
                    user_text = messaging["message"].get("text", "").lower()

                    product_list = PRODUCTS.get(page_id, [])

                    # 🔍 PRODUCT MATCH
                    matched = []
                    for p in product_list:
                        if p["name"].lower() in user_text:
                            matched.append(p)

                    # 🟢 Хэрвээ бараа олдвол зураг явуулна
                    if matched:
                        for product in matched:
                            send_product(page_id, sender_id, product)
                        continue

                    # 🤖 AI reply
                    reply = generate_reply(page_id, user_text)
                    send_message(page_id, sender_id, reply)

    return "ok"


# 🤖 AI RESPONSE
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
Та Монгол хэл дээр хариулдаг онлайн дэлгүүрийн assistant.

Дараах бараанууд байна:
{product_text}

Хэрэглэгчид тусалж, бараа санал болго.
"""
                },
                {"role": "user", "content": user_text}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return "Уучлаарай, AI хариу өгөхөд алдаа гарлаа."


# 📤 TEXT MESSAGE
def send_message(page_id, recipient_id, text):
    token = PAGE_TOKENS.get(page_id)

    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={token}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    requests.post(url, json=payload)


# 🖼️ PRODUCT CARD (Зураг + товч)
def send_product(page_id, recipient_id, product):
    token = PAGE_TOKENS.get(page_id)

    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={token}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": product["name"],
                            "image_url": product["image"],
                            "subtitle": f"{product['price']} - {product['description']}",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Захиалах",
                                    "payload": f"ORDER_{product['name']}"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

    requests.post(url, json=payload)


# 🧪 TEST
@app.get("/")
def home():
    return {"message": "AI chatbot ажиллаж байна 🚀"}
