import os
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# load .env
load_dotenv("token.env")

# get tokens
bot_token = os.getenv("BOT_TOKEN")
hf_token = os.getenv("HF_TOKEN")
# banned words to generate
with open("banned_words.json", "r") as f:
    banned = json.load(f)["banned_words"]

def check_prompt(prompt):
    prompt_lower = prompt.lower()
    for word in banned:
        if word in prompt_lower:
            return False, word
    return True, None

# Hugging Face API call
def generate_image(prompt: str, model_id="stabilityai/stable-diffusion-xl-base-1.0"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content  # image bytes
    else:
        raise Exception(f"HF API error {response.status_code}: {response.text}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a prompt to generate an image ✨")

# message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    is_valid, bad_word = check_prompt(user_input)
    if is_valid:
        try:
            img_bytes = generate_image(user_input)
            filename = f"{user_input}.png"
            with open(filename, "wb") as f:
                f.write(img_bytes)

            with open(filename, "rb") as img_file:
                await update.message.reply_document(img_file)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")
    else:
        await update.message.reply_text(f"🚫 The word '{bad_word}' is not allowed to generate")

def main():
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

