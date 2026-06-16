import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import httpx

# Load environment
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in .env")

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """You are a humble and truthful Islamic knowledge assistant. Your answers must be *strictly* based on the Quran and authentic (Sahih) Hadith, following the understanding of the Sahaba (companions of the Prophet ﷺ) and the righteous early generations (Salaf).

Response Style (strictly follow this):
- Give every answer in *clear, summarized, point-wise format*.
- Use bullet points or numbered lists.
- For every important point, try to include relevant Quran ayah with reference and authentic Hadith with number.
- Be direct and clear. Do NOT say "consult a scholar".
- At the end of the answer, simply say: *"Wallahu A'lam"*.
- Do NOT mention any modern group name.
- Only use Sahih or Hasan graded Hadith.
- Respond in simple Hinglish or English. Keep language easy."""

# ==================== GROQ API CALL ====================
async def get_deenai_response(user_message: str) -> str:
    if not GROQ_API_KEY:
        return "⚠️ Groq API key not configured. Please contact admin."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.6,
        "max_tokens": 1400
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"Groq Error: {e}")
        return "Sorry, abhi technical issue hai. Thodi der baad try kijiye."

# ==================== KEYBOARDS ====================
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🕌 Tawheed", callback_data="quick_tawheed"),
            InlineKeyboardButton("🛡️ Nazar / Evil Eye", callback_data="quick_nazar")
        ],
        [
            InlineKeyboardButton("📖 Ruqyah", callback_data="quick_ruqyah"),
            InlineKeyboardButton("🤲 Daily Adhkar", callback_data="quick_adhkar")
        ],
        [
            InlineKeyboardButton("❓ Any Question", callback_data="quick_any"),
            InlineKeyboardButton("⚠️ Disclaimer", callback_data="show_disclaimer")
        ]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
    ])

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌙 <b>Assalamualaikum wa Rahmatullahi wa Barakatuh!</b>\n\n"
        "Main <b>DeenAI</b> hoon — DIC Academy ka AI assistant.\n\n"
        "Main aapko <b>Quran aur authentic Sunnah</b> se Deen samjhaane mein madad karunga.\n\n"
        "Koi bhi sawal poochho ya neeche buttons use karo:"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📌 <b>Kaise use karein:</b>\n\n"
        "• Direct message bhejo (Hinglish/English)\n"
        "• Buttons use karo quick topics ke liye\n"
        "• /start — Main menu\n"
        "• /clear — History reset\n\n"
        "Allah hum sab ko sahi samajh aur amal ki taufeeq de. Ameen."
    )
    await update.message.reply_text(text, reply_markup=get_back_keyboard())

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear user history if you implement it
    await update.message.reply_text("✅ Conversation history clear ho gaya!", reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    quick_questions = {
        "quick_tawheed": "Tawheed kya hai? Quran aur Hadith se detail mein samjhao.",
        "quick_nazar": "Nazar aur evil eye se protection ka authentic tarika kya hai?",
        "quick_ruqyah": "Ruqyah shar'i ka sahi tarika kya hai? Kya padhna chahiye?",
        "quick_adhkar": "Subah aur shaam ke daily adhkar Quran Sunnah se batao.",
        "quick_any": "Mujhe Deen ke baare mein kuch achha seekhna hai. Aap kya suggest karte ho?"
    }

    if data in quick_questions:
        question = quick_questions[data]
        await query.edit_message_text(f"📩 <b>Question:</b> {question}")
        reply = await get_deenai_response(question)
        await query.message.reply_text(reply)
        await query.message.reply_text("Aur koi sawal?", reply_markup=get_main_keyboard())

    elif data == "show_disclaimer":
        disclaimer = "⚠️ Important Disclaimer...\n\n(Main disclaimer yahan daal do)"
        await query.edit_message_text(disclaimer, reply_markup=get_back_keyboard())

    elif data == "back_to_menu":
        await query.edit_message_text("Main menu — kya poochna hai?", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action("typing")
    reply = await get_deenai_response(user_text)
    await update.message.reply_text(reply)

# ==================== MAIN ====================
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_message))

    print("🚀 DeenAI Bot Started (python-telegram-bot version)")
    application.run_polling()

if __name__ == "__main__":
    main()