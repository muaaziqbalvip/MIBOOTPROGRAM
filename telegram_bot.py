"""
MI AI - Multi-Bot Telegram Runner
GitHub Actions par chalta hai. Ek se zyada bots ek sath chala sakta hai,
har bot ki apni fixed identity (naam/creator/personality) hoti hai.
"""

import os
import logging
import threading

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters,
)

from config import get_active_bots, build_system_identity
from model_client import generate_reply
from image_gen import generate_image
from file_gen import generate_pdf, generate_docx
from website_builder import build_website
from task_manager import add_task, format_task_list, complete_task, clear_tasks
from web_search import web_search

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

user_state = {}


def get_user(user_id):
    if user_id not in user_state:
        user_state[user_id] = {"mode": "fast", "history": []}
    return user_state[user_id]


def make_handlers(bot_cfg: dict):
    system_identity = build_system_identity(bot_cfg)
    bot_name = bot_cfg["bot_name"]
    creator = bot_cfg["creator"]

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = (
            f"👋 Salam! Main **{bot_name}** hoon — {creator} ne banaya hai mujhe.\n\n"
            "✨ Main yeh sab kar sakta hoon:\n"
            "💬 Chat (Urdu/English/Roman Urdu)\n"
            "🖼️ /image <prompt> — image banao\n"
            "📄 /pdf <topic> — PDF document\n"
            "📝 /word <topic> — Word document\n"
            "🌐 /website <topic> — poori website ZIP me\n"
            "🔍 /search <query> — quick web search\n"
            "✅ /addtask <kaam> — task add karo\n"
            "📋 /tasks — apne tasks dekho\n"
            "☑️ /done <number> — task complete karo\n"
            "⚡ /fast — turant chota jawab mode\n"
            "🧠 /pro — soch samajh kar lamba jawab mode\n\n"
            f"Abhi mode: **{get_user(update.effective_user.id)['mode'].upper()}**"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    async def fast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        get_user(update.effective_user.id)["mode"] = "fast"
        await update.message.reply_text("⚡ Fast mode ON — turant, chote jawab milenge.")

    async def pro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        get_user(update.effective_user.id)["mode"] = "pro"
        await update.message.reply_text("🧠 Pro mode ON — thora time lagega, jawab behtar hoga.")

    async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        prompt = " ".join(context.args)
        if not prompt:
            await update.message.reply_text("Prompt likhna zaroori hai. Misal: /image ek khoobsurat sunset")
            return

        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        msg = await update.message.reply_text("🎨 Image ban rahi hai...")

        filepath = generate_image(prompt)
        if filepath:
            with open(filepath, "rb") as f:
                await update.message.reply_photo(photo=f, caption=f"🖼️ {prompt}")
            os.remove(filepath)
        else:
            await update.message.reply_text("❌ Image nahi ban saki, dobara try karein.")
        try:
            await msg.delete()
        except Exception:
            pass

    async def pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = " ".join(context.args)
        if not topic:
            await update.message.reply_text("Topic likhna zaroori hai. Misal: /pdf Trading basics")
            return

        await update.message.chat.send_action(ChatAction.TYPING)
        msg = await update.message.reply_text("📄 PDF taiyar ho rahi hai...")

        try:
            content = generate_reply(
                f"Is topic par detailed, well-organized article likho: {topic}",
                mode="pro", history=[], system_identity=system_identity,
            )
            filepath = generate_pdf(topic, content)
            with open(filepath, "rb") as f:
                await update.message.reply_document(document=f, filename=os.path.basename(filepath))
            os.remove(filepath)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        try:
            await msg.delete()
        except Exception:
            pass

    async def word_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = " ".join(context.args)
        if not topic:
            await update.message.reply_text("Topic likhna zaroori hai. Misal: /word Business plan")
            return

        await update.message.chat.send_action(ChatAction.TYPING)
        msg = await update.message.reply_text("📝 Word document taiyar ho rahi hai...")

        try:
            content = generate_reply(
                f"Is topic par detailed, well-organized document likho: {topic}",
                mode="pro", history=[], system_identity=system_identity,
            )
            filepath = generate_docx(topic, content)
            with open(filepath, "rb") as f:
                await update.message.reply_document(document=f, filename=os.path.basename(filepath))
            os.remove(filepath)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        try:
            await msg.delete()
        except Exception:
            pass

    async def website_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = " ".join(context.args)
        if not topic:
            await update.message.reply_text("Topic likhna zaroori hai. Misal: /website IPTV landing page")
            return

        await update.message.chat.send_action(ChatAction.TYPING)
        msg = await update.message.reply_text("🌐 Poori website ban rahi hai, thora time lagega...")

        try:
            zip_path = build_website(topic, system_identity)
            with open(zip_path, "rb") as f:
                await update.message.reply_document(document=f, filename=os.path.basename(zip_path))
            os.remove(zip_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        try:
            await msg.delete()
        except Exception:
            pass

    async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = " ".join(context.args)
        if not query:
            await update.message.reply_text("Query likhna zaroori hai. Misal: /search Pakistan population")
            return

        await update.message.chat.send_action(ChatAction.TYPING)
        result = web_search(query)
        await update.message.reply_text(f"🔍 **{query}**\n\n{result}", parse_mode="Markdown")

    async def addtask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        task_text = " ".join(context.args)
        if not task_text:
            await update.message.reply_text("Task likhna zaroori hai. Misal: /addtask Client ko call karo")
            return
        add_task(update.effective_user.id, task_text)
        await update.message.reply_text(f"✅ Task add ho gaya: {task_text}")

    async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = format_task_list(update.effective_user.id)
        await update.message.reply_text(text, parse_mode="Markdown")

    async def done_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("Task number likhna zaroori hai. Misal: /done 1")
            return
        index = int(context.args[0]) - 1
        if complete_task(update.effective_user.id, index):
            await update.message.reply_text("☑️ Task complete mark ho gaya!")
        else:
            await update.message.reply_text("❌ Yeh task number nahi mila.")

    async def cleartasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        clear_tasks(update.effective_user.id)
        await update.message.reply_text("🗑️ Saare tasks clear ho gaye.")

    async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        state = get_user(user_id)
        text = update.message.text

        await update.message.chat.send_action(ChatAction.TYPING)

        reply = generate_reply(text, mode=state["mode"], history=state["history"], system_identity=system_identity)

        state["history"].append({"user": text, "bot": reply})
        state["history"] = state["history"][-10:]

        await update.message.reply_text(reply)

    return {
        "start": start_cmd,
        "fast": fast_cmd,
        "pro": pro_cmd,
        "image": image_cmd,
        "pdf": pdf_cmd,
        "word": word_cmd,
        "website": website_cmd,
        "search": search_cmd,
        "addtask": addtask_cmd,
        "tasks": tasks_cmd,
        "done": done_cmd,
        "cleartasks": cleartasks_cmd,
        "chat": chat_handler,
    }


def build_app(bot_cfg: dict) -> Application:
    handlers = make_handlers(bot_cfg)
    app = Application.builder().token(bot_cfg["token"]).build()

    app.add_handler(CommandHandler("start", handlers["start"]))
    app.add_handler(CommandHandler("fast", handlers["fast"]))
    app.add_handler(CommandHandler("pro", handlers["pro"]))
    app.add_handler(CommandHandler("image", handlers["image"]))
    app.add_handler(CommandHandler("pdf", handlers["pdf"]))
    app.add_handler(CommandHandler("word", handlers["word"]))
    app.add_handler(CommandHandler("website", handlers["website"]))
    app.add_handler(CommandHandler("search", handlers["search"]))
    app.add_handler(CommandHandler("addtask", handlers["addtask"]))
    app.add_handler(CommandHandler("tasks", handlers["tasks"]))
    app.add_handler(CommandHandler("done", handlers["done"]))
    app.add_handler(CommandHandler("cleartasks", handlers["cleartasks"]))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers["chat"]))

    return app


def run_bot(bot_cfg: dict):
    logger.info(f"🚀 Starting bot: {bot_cfg['bot_name']} (creator: {bot_cfg['creator']})")
    app = build_app(bot_cfg)
    app.run_polling(drop_pending_updates=True, stop_signals=None)


def main():
    active_bots = get_active_bots()

    if not active_bots:
        raise RuntimeError(
            "Koi bot token nahi mila! GitHub repo -> Settings -> Secrets and variables -> Actions "
            "me BOT_TOKEN_1 (ya jitne bhi bots config.py me set hain) add karein."
        )

    logger.info(f"{len(active_bots)} bot(s) active: {[b['bot_name'] for b in active_bots]}")

    if len(active_bots) == 1:
        run_bot(active_bots[0])
    else:
        threads = []
        for cfg in active_bots[1:]:
            t = threading.Thread(target=run_bot, args=(cfg,), daemon=True)
            t.start()
            threads.append(t)

        run_bot(active_bots[0])


if __name__ == "__main__":
    main()