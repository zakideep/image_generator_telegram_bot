import os
import json
import requests
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from keep_alive import keep_alive
from diffusers import DiffusionPipeline
import torch
# load .env
load_dotenv("token.env")

# get tokens
bot_token = os.getenv("BOT_TOKEN")

# banned words to generate
with open("banned_words.json", "r") as f:
    banned = json.load(f)["banned_words"]

def check_prompt(prompt):
    prompt_lower = prompt.lower()
    for word in banned:
        if word in prompt_lower:
            return False, word
    return True, None

# diffusion pipeline
model_id="xyn-ai/openjourney"
pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
pipe = pipe.to("cpu")



# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a prompt to generate an image ✨")

# message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    is_valid, bad_word = check_prompt(user_input)
    if is_valid:
        image = pipe(user_input).images[0]
        filename = f"{user_input}.png"
        image.save(filename)
        with open(filename, "rb") as img_file:
            await update.message.reply_document(img_file)
    else:
        await update.message.reply_text(f"🚫 The word '{bad_word}' is not allowed to generate")

def main():
    # DELETE any previous webhook to avoid Conflict error
    bot = Bot(bot_token)
    bot.delete_webhook()  # <-- key line

    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    keep_alive()
    main()




