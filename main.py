from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

PAGE_ACCESS_TOKEN = "EAGBiyPUiZClABRDVkcofHw5Ia1IMaLuA9EzsvF8PZBFJRdiAZB1PXzfQXnfuhZArYhjr25zL9ok4GvgKpFUbNVSvjBNn2XBWdkY6nPeJ1nMrAUOqvPz8b3j92Bq9cwyeJZBNPB21cRXGCJGWZB4CXUGuROmiaj90RcUOzXgehRRLnFZA4oV0jjb0BLHKlvnCtXVqEjFcwZDZD"

@app.get("/")
def home():
    return {"message": "AI chatbot ажиллаж байна"}

from fastapi import Request

@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    
    if params.get("hub.verify_token") == "mytoken123":
        return params.get("hub.challenge")
    
    return "error"

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    
    if "entry" in data:
        for entry in data["entry"]:
            for messaging in entry["messaging"]:
                sender_id = messaging["sender"]["id"]
                
                if "message" in messaging:
                    user_text = messaging["message"].get("text", "")
                    
                    reply = f"Та бичсэн: {user_text}"
                    
                    send_message(sender_id, reply)
    
    return "ok"

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    
    requests.post(url, json=payload)
