import os
import requests
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

# --- CONFIGURATION ---
# IMPORTANT: Render will automatically load this from your Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# --- FASTAPI APP ---
app = FastAPI()

# --- WEBHOOK HANDLER ---
# This is the main function that receives updates from Telegram
@app.post("/webhook")
async def handle_webhook(request: Request):
    update = await request.json()
    
    # Handle /start command
    if "message" in update and update["message"].get("text") == "/start":
        chat_id = update["message"]["chat"]["id"]
        await send_welcome_message(chat_id)
        return Response("OK", status_code=200)

    # Handle other text messages
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]
        await handle_user_message(chat_id, user_text)
        return Response("OK", status_code=200)

    return Response("OK", status_code=200)


# --- BOT FUNCTIONS ---
async def send_welcome_message(chat_id: int):
    """Sends the welcome photo with inline buttons."""
    photo_url = "https://iili.io/2kYJYnn.jpg"
    caption = "Welcome! Send me a message, and I'll process it for you."
    reply_markup = {
        "inline_keyboard": [
            [{"text": "Channel", "url": "https://t.me/PAYOUTNEXU"}],
            [{"text": "Developer", "url": "https://t.me/PAYOUTNEXU"}],
        ]
    }
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "reply_markup": reply_markup,
    }
    await send_telegram_request("sendPhoto", payload)

async def handle_user_message(chat_id: int, user_text: str):
    """Processes user's text by calling an external API."""
    api_url = f"https://last-warning.serv00.net/Muskan_gf.php?wife={requests.utils.quote(user_text)}"
    
    try:
        api_response = requests.get(api_url)
        api_response.raise_for_status()  # Raises an error for bad responses
        data = api_response.json()
        reply_text = data.get("response", "Sorry, I couldn't find a response.")
        
        await send_telegram_request("sendMessage", {"chat_id": chat_id, "text": reply_text})

    except requests.exceptions.RequestException:
        await send_telegram_request("sendMessage", {"chat_id": chat_id, "text": "Sorry, the external service is down."})
    except Exception:
        await send_telegram_request("sendMessage", {"chat_id": chat_id, "text": "An internal error occurred."})


async def send_telegram_request(method: str, payload: dict):
    """A helper function to send requests to the Telegram Bot API."""
    url = f"{TELEGRAM_API}/{method}"
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send {method} to Telegram: {e}")
