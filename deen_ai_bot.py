#!/usr/bin/env python3
"""
DeenAI Telegram Bot - DIC Academy
A humble AI assistant for authentic Islamic knowledge (Quran + Sunnah)
Start with Telegram (easy + safe). Later you can add WhatsApp if needed.

Setup:
1. Get bot token from @BotFather on Telegram
2. Get free Groq API key: https://console.groq.com/keys (recommended - fast & generous free tier)
   or use Gemini / OpenAI compatible key
3. pip install -r requirements.txt
4. Create .env file (see .env.example)
5. python deen_ai_bot.py

For production deploy: Railway.app, Render.com or cheap VPS. Use webhook instead of polling.
"""

import os
import logging
import asyncio
from typing import Dict, List

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, 
    CallbackQuery, BotCommand
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # or OPENAI_API_KEY with compatible endpoint

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in .env file. Get it from @BotFather")

if not GROQ_API_KEY:
    logging.warning("⚠️ GROQ_API_KEY not set. Bot will not be able to answer AI questions.")

# Bot setup
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# ==================== DEENAI SYSTEM PROMPT ====================
# This is the core personality + rules. Customize as you like for DIC Academy style.
SYSTEM_PROMPT = """You are a humble and truthful Islamic knowledge assistant. Your answers must be **strictly** based on the Quran and authentic (Sahih) Hadith, following the understanding of the Sahaba (companions of the Prophet ﷺ) and the righteous early generations (Salaf).

Response Style (strictly follow this):
- Give every answer in **clear, summarized, point-wise format** (like ChatGPT style — easy to read and well structured).
- Use bullet points or numbered lists.
- For every important point, try to include:
  - Relevant Quran ayah with reference (Surah name + ayah number)
  - Authentic Hadith with specific number (e.g., Sahih Bukhari Hadith no. 1234, Sahih Muslim Hadith no. 567, Sunan Tirmidhi, Abu Dawud, etc.)
  - Saying of Sahaba (RA) or Salaf, with book/reference if available and relevant
- Be direct and clear. Do NOT add "consult a scholar" or "verify with alim".
- At the end of the answer, simply say: **"Wallahu A'lam"** (Allah knows best). This shows humility.
- Emphasize that the answer is based on authentic Quran and Hadith.

Important Rules:
- Do NOT mention any modern group name or label.
- Only use Sahih or Hasan graded Hadith. Mention if something is weak.
- Always give proper references.
- Strongly focus on Tawheed according to the Sahaba's understanding.
- Respond in Hinglish or simple English according to the user. Keep language easy.
- Structure answers nicely with points for better readability.

Help people learn Deen directly from Quran and authentic Sunnah in a clear, structured, and confident way. Stay humble and truthful."""

# ==================== IN-MEMORY HISTORY (Demo only) ====================
# For production: Use Redis, PostgreSQL or file-based per user with TTL
user_histories: Dict[int, List[dict]] = {}
MAX_HISTORY = 10  # Keep last N messages to control token usage

async def get_deenai_response(user_id: int, user_message: str) -> str:
    """Call Groq (OpenAI compatible) with full context + system prompt."""
    
    if not GROQ_API_KEY:
        return ("⚠️ AI brain (Groq API key) not configured yet.\n\n"
                "Please ask the admin to add GROQ_API_KEY in environment.\n"
                "Meanwhile you can ask basic questions or I can share some adhkar/duas from memory.")
    
    # Build / update history
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    history = user_histories[user_id]
    history.append({"role": "user", "content": user_message})
    
    # Trim history (keep system + last MAX_HISTORY pairs)
    if len(history) > (MAX_HISTORY * 2 + 1):
        history = [history[0]] + history[-(MAX_HISTORY * 2):]
        user_histories[user_id] = history
    
    # Groq API call (OpenAI compatible endpoint - very fast & cheap)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",   # Excellent free tier model (change if needed)
        "messages": history,
        "temperature": 0.6,
        "max_tokens": 1400,
        "top_p": 0.95,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            assistant_reply = data["choices"][0]["message"]["content"]
            
            # Save assistant reply to history
            history.append({"role": "assistant", "content": assistant_reply})
            user_histories[user_id] = history
            
            return assistant_reply.strip()
            
    except httpx.HTTPStatusError as e:
        logging.error(f"Groq API error: {e.response.status_code} - {e.response.text}")
        return "Sorry bhai, AI service mein thodi problem aa rahi hai. Thodi der baad try karein ya koi simple sawal poochhein."
    except Exception as e:
        logging.error(f"Unexpected error in LLM call: {e}")
        return "Technical issue ho gaya. Please try again in a minute or ask a different question."

# ==================== KEYBOARDS ====================
def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🕌 Tawheed", callback_data="quick_tawheed"),
            InlineKeyboardButton(text="🛡️ Nazar/Evil Eye", callback_data="quick_nazar")
        ],
        [
            InlineKeyboardButton(text="📖 Ruqyah", callback_data="quick_ruqyah"),
            InlineKeyboardButton(text="🤲 Daily Adhkar", callback_data="quick_adhkar")
        ],
        [
            InlineKeyboardButton(text="❓ Any Question", callback_data="quick_any"),
            InlineKeyboardButton(text="⚠️ Disclaimer", callback_data="show_disclaimer")
        ]
    ])

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Main Menu", callback_data="back_to_menu")]
    ])

# ==================== HANDLERS ====================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "🌙 <b>Assalamualaikum wa Rahmatullahi wa Barakatuh!</b>\n\n"
        "Main <b>DeenAI</b> hoon — <b>DIC Academy</b> ka AI assistant.\n\n"
        "Main aapko <b>Quran aur authentic Sunnah</b> se Deen samjhaane mein madad karunga "
        "(Tawheed, ibadah, protection, daily life, etc.).\n\n"
        "<b>⚠️ Important Disclaimer:</b>\n"
        "• Main sirf AI hoon. Har jawab ko qualified scholar (alim) se verify karein.\n"
        "• Personal maslon (nikah, talaq, sihr, etc.) mein main fatwa nahi de sakta — alim se mashwara karein.\n"
        "• Health issues mein pehle doctor se check-up karayein. Ruqyah complementary hai.\n\n"
        "Koi bhi sawal poochh sakte ho ya neeche buttons use karo:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📌 <b>Kaise use karein:</b>\n\n"
        "• Direct message bhejo (Hinglish ya English mein) — main jawab dunga with Quran/Hadith references.\n"
        "• Buttons use karo quick topics ke liye.\n"
        "• /start — Main menu\n"
        "• /clear — Conversation history reset karo (agar bot confuse ho)\n\n"
        "<b>Topics examples:</b>\n"
        "• Tawheed kya hai with evidence?\n"
        "• Nazar se bachne ka tarika\n"
        "• Subah shaam ke adhkar\n"
        "• Ruqyah ka sahi tareeqa\n\n"
        "Allah hum sab ko sahi Deen samajhne aur amal karne ki taufeeq de. Ameen."
    )
    await message.answer(help_text, reply_markup=get_back_keyboard())

@dp.message(Command("clear"))
async def cmd_clear(message: Message):
    user_id = message.from_user.id
    if user_id in user_histories:
        del user_histories[user_id]
    await message.answer("✅ Conversation history clear ho gaya. Ab fresh start karte hain!", 
                         reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "back_to_menu")
async def cb_back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Main menu — kya poochna hai?",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("quick_"))
async def cb_quick_questions(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    
    quick_map = {
        "quick_tawheed": "Tawheed kya hai? Detail mein Quran aur Hadith se samjhao.",
        "quick_nazar": "Nazar aur evil eye se protection ka authentic tarika kya hai? Quran aur Sunnah se batao.",
        "quick_ruqyah": "Ruqyah shar'i ka sahi tarika batao. Kya padhna chahiye aur kya avoid karna chahiye?",
        "quick_adhkar": "Subah aur shaam ke daily adhkar aur duas Quran Sunnah se batao with Arabic + translation.",
        "quick_any": "Mujhe Deen ke baare mein kuch achha seekhna hai. Aap kya suggest karte ho?"
    }
    
    question = quick_map.get(data, "Tell me something beneficial about Deen.")
    
    await callback.message.edit_text(f"📩 <b>Question:</b> {question}")
    await callback.answer()
    
    # Process the question
    reply = await get_deenai_response(user_id, question)
    
    # Send reply (split if very long)
    if len(reply) > 3800:
        for chunk in [reply[i:i+3800] for i in range(0, len(reply), 3800)]:
            await callback.message.answer(chunk)
    else:
        await callback.message.answer(reply)
    
    # Re-show menu
    await callback.message.answer("Aur koi sawal?", reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "show_disclaimer")
async def cb_disclaimer(callback: CallbackQuery):
    disclaimer = (
        "⚠️ <b>Important Disclaimer - DeenAI</b>\n\n"
        "• This is an AI chatbot, not a human scholar or mufti.\n"
        "• All answers are generated based on training + retrieved knowledge from Quran & authentic Hadith.\n"
        "• AI can make mistakes. <b>Always verify</b> with qualified scholars who follow Quran & Sunnah.\n"
        "• For personal religious rulings (fiqh), marriage, inheritance, or spiritual issues — consult a local righteous alim.\n"
        "• For any physical/mental health symptoms, see a qualified doctor first. Ruqyah is not a substitute for medical treatment.\n"
        "• We do not promote or tolerate shirk, bid'ah, or unverified spiritual practices.\n\n"
        "Our goal is only to help you get closer to Allah through authentic knowledge. "
        "May Allah guide us all to the straight path. Ameen."
    )
    await callback.message.edit_text(disclaimer, reply_markup=get_back_keyboard())
    await callback.answer()

@dp.message()
async def handle_user_message(message: Message):
    """Main handler for free-text questions."""
    if not message.text or message.text.startswith("/"):
        return
    
    user_id = message.from_user.id
    user_text = message.text.strip()
    
    # Show typing
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    reply = await get_deenai_response(user_id, user_text)
    
    if len(reply) > 3800:
        for chunk in [reply[i:i+3800] for i in range(0, len(reply), 3800)]:
            await message.answer(chunk)
    else:
        await message.answer(reply)
    
    # Occasionally remind about menu
    if len(user_histories.get(user_id, [])) % 6 == 0:
        await message.answer("Koi aur sawal ho to poochho ya menu use karo 👇", 
                             reply_markup=get_main_keyboard())

# ==================== MAIN ====================
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Start DeenAI / Main menu"),
        BotCommand(command="help", description="How to use + examples"),
        BotCommand(command="clear", description="Reset conversation history"),
    ]
    await bot.set_my_commands(commands)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logging.info("🚀 Starting DeenAI Telegram Bot for DIC Academy...")
    
    await set_bot_commands()
    
    # Start polling (simple). For production use webhook + aiohttp server.
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user.")
