# DeenAI Telegram Bot — DIC Academy

**Authentic Deen AI chatbot** powered by Quran + Sahih Sunnah.  
Built for dawah, easy to use in Hinglish/English, with strong disclaimers and source citations.

This is the **recommended starting point** for your Deen AI project.

## Why Telegram First? (vs WhatsApp)

| Feature              | Telegram Bot                  | WhatsApp Bot (Unofficial)      | WhatsApp Official API         |
|----------------------|-------------------------------|--------------------------------|-------------------------------|
| **Ease of building** | Very easy                     | Medium                         | Hard + approval needed        |
| **Cost**             | Almost free                   | Free but risky                 | Paid per conversation         |
| **Ban risk**         | Very low                      | **High** (you had issues before) | Low (but needs verification) |
| **Speed to launch**  | 1-2 hours                     | 1-2 days                       | 1-4 weeks + business docs     |
| **Features**         | Buttons, inline, media, groups| Good 1-to-1                    | Good but expensive scaling    |
| **Best for**         | Dawah + community learning    | Personal use only              | Serious business              |

**Recommendation**: Launch on **Telegram first**. It's safe, fast, and perfect for DIC Academy (YouTube audience can join easily).  
Later, if you get a stable verified WhatsApp Business number, we can add a bridge or separate bot.

## Quick Start (Local)

1. **Clone / Download** this folder

2. **Install dependencies**
   ```bash
   cd deen_ai_telegram_bot
   pip install -r requirements.txt
   ```

3. **Get your keys**
   - Telegram bot token → Open Telegram → search **@BotFather** → `/newbot` → copy token
   - Groq API key (free & fast) → https://console.groq.com/keys → create key

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and paste your two keys.

5. **Run the bot**
   ```bash
   python deen_ai_bot.py
   ```

6. Open Telegram → search your bot username → `/start`

Done! Test with "Tawheed kya hai?" or use the buttons.

## How to Customize (Your Brand)

- Edit `SYSTEM_PROMPT` in `deen_ai_bot.py` — add more emphasis on your Tawheed course style, Indian context examples, or specific scholars you like.
- Change model in `get_deenai_response()` if you want smaller/faster/cheaper (e.g. `llama-3.1-8b-instant`).
- Add your own quick buttons or new commands easily.
- Later: Connect real RAG (your course notes + Quran/Hadith PDFs) using ChromaDB + LangChain for even more accurate answers.

## Production Deployment (Free / Cheap)

**Recommended (easiest): Railway.app**
1. Push code to GitHub
2. Connect repo on Railway
3. Add environment variables (TELEGRAM_BOT_TOKEN + GROQ_API_KEY)
4. It auto-deploys. Bot runs 24/7.

Other good free options: Render.com, Hugging Face Spaces (with care), or cheap Hetzner/Contabo VPS (~₹300-500/month).

**For production** (later):
- Switch from polling to **webhook** (more efficient)
- Use Redis to store user history across restarts
- Add rate limiting + logging
- Add admin commands (/broadcast to your channel)

I can help upgrade the code when you're ready.

## Important Notes on Deen Content

- The bot has **strong built-in rules**:
  - Always cites Quran + authentic Hadith
  - Heavy disclaimers on personal fiqh, sihr/jinn, health
  - Warns against shirk & bid'ah
  - Prefers Hinglish when user uses it
- Still: **Never 100% perfect**. Always tell users to verify with scholars.
- For sensitive topics (ruqyah, relationships, etc.) the bot is conservative by design.

## Next Steps / Roadmap

1. **Today**: Launch Telegram bot + test with friends/family
2. **This week**: Share on your YouTube / Instagram / WhatsApp status ("DIC Academy ka DeenAI bot launch — sawal poochho!")
3. **Next**: 
   - Add your Tawheed course content (RAG)
   - Make it bilingual (add Urdu support)
   - Create a simple web version too
4. **Later** (if needed): WhatsApp integration discussion

## Support

This bot was built specifically for your DIC Academy vision.  
If you want any changes (different personality, more topics, logo in responses, voice messages later, etc.) — just tell me.

**Bismillah** — let's spread authentic Deen with this tool. May Allah accept it and make it beneficial. Ameen.

---

**Files in this folder**:
- `deen_ai_bot.py` — Main bot code (ready to run)
- `requirements.txt` — Python packages
- `.env.example` — Template for your keys
- `README.md` — This file

Run it and tell me how it feels! 🚀
