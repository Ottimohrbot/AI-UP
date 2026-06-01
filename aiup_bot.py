import os
import logging
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════
# CONFIG — o'zgartiring
# ═══════════════════════════════════════
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8970482071:AAEy6xthMW1btri3XBo7F4M8ySzZdwMudFM")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Li2KunD8qzDsDd6fltwxajkgY7TlQGdO95k8m-bt_M1g")
ADMIN_CHAT_ID  = int(os.environ.get("ADMIN_CHAT_ID", "6613741078"))  # sizning Telegram ID

# ═══════════════════════════════════════
# XIZMATLAR
# ═══════════════════════════════════════
SERVICES = {
    "bot": {
        "uz": "🤖 Telegram Bot",
        "ru": "🤖 Telegram Bot",
        "en": "🤖 Telegram Bot",
        "price": 100,
        "desc": {
            "uz": "Biznesingiz uchun professional Telegram bot. Buyurtma qabul qilish, mijozlar bilan muloqot, avtomatik javoblar.",
            "ru": "Профессиональный Telegram бот для вашего бизнеса. Приём заказов, общение с клиентами, автоответы.",
            "en": "Professional Telegram bot for your business. Order management, customer communication, auto-replies."
        }
    },
    "agent": {
        "uz": "🧠 Suniy Intellekt Agent",
        "ru": "🧠 ИИ Агент",
        "en": "🧠 AI Agent",
        "price": 150,
        "desc": {
            "uz": "Aqlli AI agent — mijozlar savollariga avtomatik javob beradi, 24/7 ishlaydi, biznesingizni tushunadi.",
            "ru": "Умный ИИ агент — автоматически отвечает на вопросы клиентов, работает 24/7.",
            "en": "Smart AI agent — automatically answers customer questions, works 24/7, understands your business."
        }
    },
    "attendance": {
        "uz": "📊 Ishchi Keldi-Ketdi Tizimi",
        "ru": "📊 Система Посещаемости",
        "en": "📊 Employee Attendance System",
        "price": 75,
        "desc": {
            "uz": "Xodimlar keldi-ketdisini kuzatish tizimi. Avtomatik hisobot, jarima hisoblash, ish vaqti nazorati.",
            "ru": "Система отслеживания посещаемости сотрудников. Авто-отчёты, штрафы, контроль рабочего времени.",
            "en": "Employee attendance tracking system. Auto reports, penalty calculation, work time control."
        }
    },
    "test": {
        "uz": "📝 Ishchi Test Tizimi",
        "ru": "📝 Система Тестирования",
        "en": "📝 Employee Testing System",
        "price": 75,
        "desc": {
            "uz": "Xodimlarni sinov muddatida baholash tizimi. Onlayn test, natijalar tahlili, Telegram bildirishnoma.",
            "ru": "Система оценки сотрудников на испытательном сроке. Онлайн тест, анализ результатов.",
            "en": "Employee probation evaluation system. Online test, result analysis, Telegram notification."
        }
    }
}

# ═══════════════════════════════════════
# TIL KONFIGURATSIYASI
# ═══════════════════════════════════════
TEXTS = {
    "uz": {
        "welcome": (
            "👋 Salom, *{}*!\n\n"
            "🚀 *AIUP* ga xush kelibsiz — biznesingizni AI bilan tezlashtiring!\n\n"
            "Quyidagilardan birini tanlang:"
        ),
        "menu": [
            ["🛍 Xizmatlar", "💰 Narxlar"],
            ["📁 Portfolio", "📞 Bog'lanish"],
            ["🤖 AI Maslahat", "🌐 Til tanlash"]
        ],
        "services_title": "🛍 *Bizning xizmatlar:*\n\nQaysi xizmat haqida ko'proq bilmoqchisiz?",
        "price_title": "💰 *Narxlar ro'yxati:*\n\n",
        "order_title": "📋 *Buyurtma berish*\n\nQaysi xizmatni buyurtma qilmoqchisiz?",
        "portfolio_title": (
            "📁 *Portfolio — Bizning ishlarimiz:*\n\n"
            "✅ 20+ muvaffaqiyatli loyiha\n"
            "✅ Telegram botlar — restoran, HR, e-commerce\n"
            "✅ AI agentlar — mijozlar qo'llab-quvvatlash\n"
            "✅ Keldi-ketdi tizimlari — 5+ kafe va kompaniya\n"
            "✅ HR test tizimlari — 100+ xodim baholangan\n\n"
            "📱 Namunalar: @aiup_demo\n"
            "🌐 Veb: aiup.uz"
        ),
        "contact_title": (
            "📞 *Bog'lanish:*\n\n"
            "👤 Menejer: @Ibr0kh1_M\n"
            "📱 Telefon: +998 77 877 00 84\n"
            "🌐 Veb: aiup.uz\n\n"
            "⏰ Ish vaqti: 09:00 — 18:00"
        ),
        "order_name": "📝 Ismingizni kiriting:",
        "order_phone": "📱 Telefon raqamingizni kiriting:\n(Masalan: +998901234567)",
        "order_comment": "💬 Qo'shimcha izoh yoki savolingiz bo'lsa yozing:\n(Yo'q bo'lsa 'Yo'q' deb yozing)",
        "order_confirm": (
            "✅ *Buyurtmangiz qabul qilindi!*\n\n"
            "📋 Xizmat: {service}\n"
            "👤 Ism: {name}\n"
            "📱 Telefon: {phone}\n"
            "💬 Izoh: {comment}\n\n"
            "📞 Menejerimiz 30 daqiqa ichida siz bilan bog'lanadi!"
        ),
        "ai_hint": "🤖 *AI Maslahat*\n\nBiznesingiz haqida savolingizni yozing — AI maslahat beradi!",
        "lang_select": "🌐 Tilni tanlang:",
        "order_btn": "📋 Buyurtma berish",
        "back_btn": "🔙 Orqaga",
        "cancel_btn": "❌ Bekor qilish",
        "lang_changed": "✅ Til o'zgartirildi!",
        "phone_err": "⚠️ Noto'g'ri telefon. Iltimos qaytadan kiriting.",
    },
    "ru": {
        "welcome": (
            "👋 Привет, *{}*!\n\n"
            "🚀 Добро пожаловать в *AIUP* — ускорьте свой бизнес с ИИ!\n\n"
            "Выберите один из разделов:"
        ),
        "menu": [
            ["🛍 Услуги", "💰 Цены"],
            ["📁 Портфолио", "📞 Контакты"],
            ["🤖 ИИ Консультация", "🌐 Язык"]
        ],
        "services_title": "🛍 *Наши услуги:*\n\nО какой услуге хотите узнать подробнее?",
        "price_title": "💰 *Прайс-лист:*\n\n",
        "order_title": "📋 *Оформить заказ*\n\nКакую услугу хотите заказать?",
        "portfolio_title": (
            "📁 *Портфолио — Наши работы:*\n\n"
            "✅ 20+ успешных проектов\n"
            "✅ Telegram боты — ресторан, HR, e-commerce\n"
            "✅ ИИ агенты — поддержка клиентов\n"
            "✅ Системы учёта посещаемости — 5+ компаний\n"
            "✅ HR системы тестирования — 100+ сотрудников\n\n"
            "📱 Демо: @aiup_demo\n"
            "🌐 Сайт: aiup.uz"
        ),
        "contact_title": (
            "📞 *Контакты:*\n\n"
            "👤 Менеджер: @Ibr0kh1_M\n"
            "📱 Телефон: +998 77 877 00 84\n"
            "🌐 Сайт: aiup.uz\n\n"
            "⏰ Рабочее время: 09:00 — 18:00"
        ),
        "order_name": "📝 Введите ваше имя:",
        "order_phone": "📱 Введите номер телефона:\n(Например: +998901234567)",
        "order_comment": "💬 Напишите комментарий или вопрос:\n(Если нет — напишите 'Нет')",
        "order_confirm": (
            "✅ *Ваш заказ принят!*\n\n"
            "📋 Услуга: {service}\n"
            "👤 Имя: {name}\n"
            "📱 Телефон: {phone}\n"
            "💬 Комментарий: {comment}\n\n"
            "📞 Менеджер свяжется с вами в течение 30 минут!"
        ),
        "ai_hint": "🤖 *ИИ Консультация*\n\nНапишите вопрос о вашем бизнесе — ИИ даст совет!",
        "lang_select": "🌐 Выберите язык:",
        "order_btn": "📋 Оформить заказ",
        "back_btn": "🔙 Назад",
        "cancel_btn": "❌ Отмена",
        "lang_changed": "✅ Язык изменён!",
        "phone_err": "⚠️ Неверный телефон. Пожалуйста введите снова.",
    },
    "en": {
        "welcome": (
            "👋 Hello, *{}*!\n\n"
            "🚀 Welcome to *AIUP* — accelerate your business with AI!\n\n"
            "Choose one of the sections:"
        ),
        "menu": [
            ["🛍 Services", "💰 Pricing"],
            ["📁 Portfolio", "📞 Contact"],
            ["🤖 AI Consult", "🌐 Language"]
        ],
        "services_title": "🛍 *Our services:*\n\nWhich service would you like to know more about?",
        "price_title": "💰 *Price list:*\n\n",
        "order_title": "📋 *Place an order*\n\nWhich service would you like to order?",
        "portfolio_title": (
            "📁 *Portfolio — Our works:*\n\n"
            "✅ 20+ successful projects\n"
            "✅ Telegram bots — restaurant, HR, e-commerce\n"
            "✅ AI agents — customer support\n"
            "✅ Attendance systems — 5+ companies\n"
            "✅ HR testing systems — 100+ employees evaluated\n\n"
            "📱 Demo: @aiup_demo\n"
            "🌐 Web: aiup.uz"
        ),
        "contact_title": (
            "📞 *Contact us:*\n\n"
            "👤 Manager: @Ibr0kh1_M\n"
            "📱 Phone: +998 77 877 00 84\n"
            "🌐 Web: aiup.uz\n\n"
            "⏰ Working hours: 09:00 — 18:00"
        ),
        "order_name": "📝 Enter your name:",
        "order_phone": "📱 Enter your phone number:\n(Example: +998901234567)",
        "order_comment": "💬 Write a comment or question:\n(If none — write 'None')",
        "order_confirm": (
            "✅ *Your order has been received!*\n\n"
            "📋 Service: {service}\n"
            "👤 Name: {name}\n"
            "📱 Phone: {phone}\n"
            "💬 Comment: {comment}\n\n"
            "📞 Our manager will contact you within 30 minutes!"
        ),
        "ai_hint": "🤖 *AI Consultation*\n\nAsk a question about your business — AI will give advice!",
        "lang_select": "🌐 Choose language:",
        "order_btn": "📋 Place order",
        "back_btn": "🔙 Back",
        "cancel_btn": "❌ Cancel",
        "lang_changed": "✅ Language changed!",
        "phone_err": "⚠️ Invalid phone. Please enter again.",
    }
}

# ═══════════════════════════════════════
# STATE
# ═══════════════════════════════════════
user_lang   = {}   # user_id -> "uz"/"ru"/"en"
user_state  = {}   # user_id -> state
user_orders = {}   # user_id -> {service, name, phone, comment}
user_ai_history = {}  # user_id -> [{"user":..,"agent":..}]

def get_lang(uid):
    return user_lang.get(uid, "uz")

def get_text(uid, key):
    return TEXTS[get_lang(uid)][key]

def get_menu(uid):
    return ReplyKeyboardMarkup(TEXTS[get_lang(uid)]["menu"], resize_keyboard=True)

# ═══════════════════════════════════════
# GEMINI AI
# ═══════════════════════════════════════
def ask_gemini(uid, user_text):
    lang = get_lang(uid)
    history = user_ai_history.get(uid, [])
    hist_txt = "\n\n".join([f"Foydalanuvchi: {h['user']}\nAgent: {h['agent']}" for h in history[-5:]])

    if lang == "ru":
        sys = (
            "Ты умный AI ассистент. Отвечай на любые вопросы. "
            "Отвечай кратко, по-русски, с эмодзи."
        )
    elif lang == "en":
        sys = (
            "You are a smart AI assistant. Answer any question. "
            "Reply briefly in English with emojis."
        )
    else:
        sys = (
            "Sen aqlli AI yordamchisisan. Har qanday savolga javob bera olasan. "
            "O'zbek tilida qisqa, do'stona va emoji bilan javob ber."
        )

    prompt = sys + (f"\n\nOldingi suhbat:\n{hist_txt}" if hist_txt else "") + f"\n\nFoydalanuvchi: {user_text}\nAgent:"

    try:
        res = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}},
            timeout=30
        )
        res.raise_for_status()
        reply = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        if uid not in user_ai_history:
            user_ai_history[uid] = []
        user_ai_history[uid].append({"user": user_text, "agent": reply})
        return reply
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        msgs = {"uz": "⚠️ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.", "ru": "⚠️ Произошла ошибка. Попробуйте снова.", "en": "⚠️ An error occurred. Please try again."}
        return msgs.get(lang, msgs["uz"])

# ═══════════════════════════════════════
# ADMIN XABARDORLIK
# ═══════════════════════════════════════
async def notify_admin(context, order: dict, user):
    lang = order.get("lang", "uz")
    service_key = order.get("service", "")
    service_name = SERVICES.get(service_key, {}).get("uz", service_key)
    username = f"@{user.username}" if user.username else "username yo'q"

    msg = (
        f"🆕 <b>Yangi buyurtma!</b>\n\n"
        f"👤 <b>Ism:</b> {order.get('name', '—')}\n"
        f"📱 <b>Telefon:</b> {order.get('phone', '—')}\n"
        f"🛍 <b>Xizmat:</b> {service_name}\n"
        f"💰 <b>Narx:</b> ${SERVICES.get(service_key, {}).get('price', '—')}\n"
        f"💬 <b>Izoh:</b> {order.get('comment', '—')}\n"
        f"🌐 <b>Til:</b> {lang.upper()}\n"
        f"📲 <b>Telegram:</b> {username}\n"
        f"🕐 <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Admin notify error: {e}")

# ═══════════════════════════════════════
# INLINE KLAVIATURA — XIZMATLAR
# ═══════════════════════════════════════
def services_keyboard(uid):
    lang = get_lang(uid)
    rows = []
    for key, srv in SERVICES.items():
        rows.append([InlineKeyboardButton(f"{srv[lang]} — ${srv['price']}", callback_data=f"srv_{key}")])
    return InlineKeyboardMarkup(rows)

def order_keyboard(uid):
    lang = get_lang(uid)
    rows = []
    for key, srv in SERVICES.items():
        rows.append([InlineKeyboardButton(f"{srv[lang]} — ${srv['price']}", callback_data=f"order_{key}")])
    rows.append([InlineKeyboardButton(get_text(uid, "cancel_btn"), callback_data="cancel")])
    return InlineKeyboardMarkup(rows)

def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    ]])

# ═══════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name or "Foydalanuvchi"
    user_state.pop(uid, None)
    user_orders.pop(uid, None)
    lang = get_lang(uid)
    await update.message.reply_text(
        TEXTS[lang]["welcome"].format(name),
        parse_mode="Markdown",
        reply_markup=get_menu(uid)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    text  = update.message.text or ""
    lang  = get_lang(uid)
    state = user_state.get(uid)

    # ── ORDER STATE MACHINE ──
    if state == "order_name":
        if len(text.strip()) < 2:
            await update.message.reply_text("⚠️ Ism juda qisqa. Qaytadan kiriting:", reply_markup=ReplyKeyboardRemove())
            return
        user_orders[uid]["name"] = text.strip()
        user_state[uid] = "order_phone"
        await update.message.reply_text(get_text(uid, "order_phone"), reply_markup=ReplyKeyboardRemove())
        return

    if state == "order_phone":
        clean = text.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not (clean.startswith("+") and len(clean) >= 10 and clean[1:].isdigit()):
            await update.message.reply_text(get_text(uid, "phone_err"))
            return
        user_orders[uid]["phone"] = text.strip()
        user_state[uid] = "order_comment"
        await update.message.reply_text(get_text(uid, "order_comment"), reply_markup=ReplyKeyboardRemove())
        return

    if state == "order_comment":
        user_orders[uid]["comment"] = text.strip()
        user_orders[uid]["lang"] = lang
        order = user_orders[uid]
        service_key = order.get("service", "")
        service_name = SERVICES.get(service_key, {}).get(lang, service_key)
        # Tasdiqlash
        confirm_msg = get_text(uid, "order_confirm").format(
            service=service_name,
            name=order["name"],
            phone=order["phone"],
            comment=order["comment"]
        )
        user_state.pop(uid, None)
        await update.message.reply_text(confirm_msg, parse_mode="Markdown", reply_markup=get_menu(uid))
        await notify_admin(context, order, update.effective_user)
        return

    # ── AI MODE ──
    if state == "ai_mode":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        reply = ask_gemini(uid, text)
        await update.message.reply_text(reply, reply_markup=get_menu(uid))
        return

    # ── MENU BUTTONS ──
    all_texts = {
        "🛍 Xizmatlar": "services", "🛍 Услуги": "services", "🛍 Services": "services",
        "💰 Narxlar": "prices",    "💰 Цены": "prices",      "💰 Pricing": "prices",
        "📁 Portfolio": "portfolio","📁 Портфолио": "portfolio","📁 Portfolio": "portfolio",
        "📞 Bog'lanish": "contact", "📞 Контакты": "contact",  "📞 Contact": "contact",
        "🤖 AI Maslahat": "ai",    "🤖 ИИ Консультация": "ai","🤖 AI Consult": "ai",
        "🌐 Til tanlash": "lang",  "🌐 Язык": "lang",         "🌐 Language": "lang",
    }

    action = all_texts.get(text)

    if action == "services":
        await update.message.reply_text(
            get_text(uid, "services_title"),
            parse_mode="Markdown",
            reply_markup=services_keyboard(uid)
        )
    elif action == "prices":
        price_msg = get_text(uid, "price_title")
        for key, srv in SERVICES.items():
            price_msg += f"• {srv[lang]} — *${srv['price']}*\n"
            price_msg += f"  _{srv['desc'][lang]}_\n\n"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(get_text(uid, "order_btn"), callback_data="show_order")]])
        await update.message.reply_text(price_msg, parse_mode="Markdown", reply_markup=kb)
    elif action == "portfolio":
        await update.message.reply_text(get_text(uid, "portfolio_title"), parse_mode="Markdown", reply_markup=get_menu(uid))
    elif action == "contact":
        await update.message.reply_text(get_text(uid, "contact_title"), parse_mode="Markdown", reply_markup=get_menu(uid))
    elif action == "ai":
        user_state[uid] = "ai_mode"
        user_ai_history.pop(uid, None)
        await update.message.reply_text(get_text(uid, "ai_hint"), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    elif action == "lang":
        await update.message.reply_text(get_text(uid, "lang_select"), reply_markup=lang_keyboard())
    else:
        # Noma'lum xabar — AI ga yuborish
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        reply = ask_gemini(uid, text)
        await update.message.reply_text(reply, reply_markup=get_menu(uid))

# ═══════════════════════════════════════
# CALLBACK HANDLER
# ═══════════════════════════════════════
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid  = query.from_user.id
    data = query.data
    lang = get_lang(uid)

    # Til o'zgartirish
    if data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_lang[uid] = new_lang
        await query.edit_message_text(TEXTS[new_lang]["lang_changed"])
        await context.bot.send_message(
            chat_id=uid,
            text=TEXTS[new_lang]["welcome"].format(query.from_user.first_name or "User"),
            parse_mode="Markdown",
            reply_markup=get_menu(uid)
        )
        return

    # Xizmat ko'rish
    if data.startswith("srv_"):
        key = data[4:]
        srv = SERVICES.get(key)
        if not srv:
            return
        msg = (
            f"*{srv[lang]}*\n\n"
            f"💰 Narx: *${srv['price']}*\n\n"
            f"📝 {srv['desc'][lang]}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text(uid, "order_btn"), callback_data=f"order_{key}")],
            [InlineKeyboardButton(get_text(uid, "back_btn"), callback_data="back_services")]
        ])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=kb)
        return

    # Buyurtma boshlash
    if data == "show_order":
        await query.edit_message_text(get_text(uid, "order_title"), parse_mode="Markdown", reply_markup=order_keyboard(uid))
        return

    if data.startswith("order_"):
        key = data[6:]
        if key not in SERVICES:
            return
        user_orders[uid] = {"service": key}
        user_state[uid] = "order_name"
        await query.edit_message_text(get_text(uid, "order_name"), parse_mode="Markdown")
        return

    # Orqaga
    if data == "back_services":
        await query.edit_message_text(
            get_text(uid, "services_title"),
            parse_mode="Markdown",
            reply_markup=services_keyboard(uid)
        )
        return

    # Bekor qilish
    if data == "cancel":
        user_state.pop(uid, None)
        user_orders.pop(uid, None)
        await query.edit_message_text("❌ Bekor qilindi.")
        await context.bot.send_message(chat_id=uid, text="🏠 Bosh menyu:", reply_markup=get_menu(uid))
        return

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("AIUP Bot ishga tushdi!")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
