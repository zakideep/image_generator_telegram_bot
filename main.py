from diffusers import DiffusionPipeline
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import torch

# load token.env
load_dotenv("token.env")
# get bot token
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
model_id = "xyn-ai/openjourney"
pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
pipe = pipe.to("cpu")  # or "cuda" if you have GPU

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! write your prompt to generate")


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
    # Create the app with your token
    app = Application.builder().token(bot_token).build()

    # Register /start handler
    app.add_handler(CommandHandler("start", start))
    # message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Run bot (polling mode)
    app.run_polling()
# run bot
if __name__ == "__main__":
    main()
