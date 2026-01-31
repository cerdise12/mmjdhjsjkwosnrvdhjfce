BOT_TOKEN = "8396306941:AAEuwWU9i2qe9fr_QYC9lj43ESVEa2x3He4"
CHANNEL_ID = "@alphafunpay"
CHANNEL_URL = "https://t.me/alphafunpay"

user_lang = {}
user_sessions = {}

global_settings = {
    "watermark": True,
    "ignore_support": True,
    "ignore_self": True,
    "ignore_system": True
}

ASK_LANG_TEXT = "<b>выберите язык</b>"
WELCOME_TEXT = (
    "<b>приветствую <tg-emoji emoji-id=\"5260249440450520061\">🤚</tg-emoji> {user} в XaslerFunpay"
    "<tg-emoji emoji-id=\"5258093637450866522\">🤖</tg-emoji>\n\n"
    "<tg-emoji emoji-id=\"5260268501515377807\">📣</tg-emoji> подпишись на канал для работы"
    "<tg-emoji emoji-id=\"5260268501515377807\">📣</tg-emoji></b>"
)
MENU_TEXT = (
    "<b><tg-emoji emoji-id=\"5316727448644103237\">👤</tg-emoji> {user}</b>\n\n"
    "<blockquote><b>XaslerFunpay ваш помощник в бизнесе</b></blockquote>\n\n"
    "<b>выберите действия <tg-emoji emoji-id=\"5429571366384842791\">🔎</tg-emoji></b>"
)
HELP_TEXT = (
    "<b>$bot — автоматизированный помощник FunPay.\n"
    "Бесплатный план + продвинутые (mid/extra).\n"
    "Безопасность гарантирована.\n"
    "Вопросы — в поддержку.</b>"
)

def tr(text, lang):
    # Всегда возвращаем русский текст, независимо от выбранного языка
    return text
