# main.py
import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks
import openai
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("8340544799:AAFuzj2q7mjdtRPwjoVUcNeQ-Kh6l9pj7qc")
OPENAI_API_KEY = os.getenv("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")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1")  # change if needed

openai.api_key = OPENAI_API_KEY
BOT_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = FastAPI()

def send_telegram(chat_id: int, text: str):
    requests.post(f"{BOT_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def ask_openai(prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role":"system","content":"You are a helpful assistant."},
                  {"role":"user","content":prompt}],
        max_tokens=500,
        temperature=0.7
    )
    return resp.choices[0].message["content"].strip()

@app.post("/webhook")
async def webhook(req: Request, background: BackgroundTasks):
    data = await req.json()
    # extract text and chat id safely
    message = data.get("message") or data.get("edited_message") or {}
    text = message.get("text")
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if not text or not chat_id:
        return {"ok": True}

    # do OpenAI call in background to speed up response 200 to Telegram if needed
    def process():
        try:
            reply = ask_openai(text)
        except Exception as e:
            reply = "Sorry, OpenAI error."
        send_telegram(chat_id, reply)

    background.add_task(process)
    return {"ok": True}
