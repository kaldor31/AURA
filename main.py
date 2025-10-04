import os
import asyncio
from typing import List, Dict, Any
import aiohttp
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

# GOOGLE_API_KEY - Google Custom Search API Key
# GOOGLE_CSE_ID - Search Engine ID (cx)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# ---------- Google CSE Web Search Feature ----------
async def search_web_google(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Searches through the Google Custom Search API and returns a list of results:
    [{'title': ..., 'snippet': ..., 'url': ...}, ...]
    """
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": limit
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(GOOGLE_SEARCH_URL, params=params, timeout=15) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"Google CSE API error: {resp.status} {text}")
            data = await resp.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "url": item.get("link")
        })
    return results

# ---------- Formatting a response ----------
def format_answer(query: str, results: List[Dict[str, Any]]) -> str:
    if not results:
        return "К сожалению, по вашему запросу ничего не найдено."

    # Short answer from the first snippets
    top_snippets = [r["snippet"].rstrip(".") + "." for r in results[:2] if r.get("snippet")]
    summary = " ".join(top_snippets) if top_snippets else "Найдено несколько источников по запросу."

    sources = "\n".join(f"{i+1}. [{r['title']}]({r['url']})" for i, r in enumerate(results))
    message = (
        f"{summary}"
        f"\n\n*Источники:*\n{sources}\n\n"
        f"_Ответ основан на общедоступных данных. Проверяйте источники для уверенности._"
    )
    return message

# ---------- Telegram handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуй! Задай мне вопрос о женской физиологии.\n"
        "и я пришлю краткий ответ со ссылками на источники."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — приветствие\n"
        "Просто напиши вопрос, например: 'Что такое квантовый компьютер?'"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if not user_text:
        await update.message.reply_text("Пожалуйста, отправьте текстовый запрос.")
        return

    await update.message.chat.send_action(action="typing")

    try:
        results = await search_web_google(user_text, limit=4)
        answer = format_answer(user_text, results)
        await update.message.reply_text(answer, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=False)
    except Exception as e:
        print("Ошибка при поиске:", e)
        await update.message.reply_text("Произошла ошибка при поиске. Попробуйте позже.")

# ---------- Main Function ----------
def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN not installed!")
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        raise RuntimeError("GOOGLE_API_KEY или GOOGLE_CSE_ID not installedы!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("The bot is working...")
    app.run_polling()

if __name__ == "__main__":
    main()