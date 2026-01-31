import telebot
from telebot import types
from config import (
    BOT_TOKEN, CHANNEL_ID, CHANNEL_URL, ASK_LANG_TEXT, 
    WELCOME_TEXT, MENU_TEXT, HELP_TEXT, user_lang, tr, user_sessions
)
from functions import (
    add_account, toggle_online, build_accounts_keyboard, 
    set_return_settings, get_return_settings, add_keyword_response, 
    get_keywords, remove_keyword, set_auto_review_response, get_auto_review_response
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== ОБРАБОТЧИКИ СООБЩЕНИЙ ====================

@bot.message_handler(commands=["start"])
def start_command(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    if user_id not in user_lang:
        # Показываем выбор языка
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("Русский 🇷🇺", callback_data="set_lang_ru"),
            types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
        )
        bot.send_message(message.chat.id, ASK_LANG_TEXT, reply_markup=kb)
    else:
        send_main_menu(message.chat.id, message.from_user.first_name, user_id)

def send_main_menu(chat_id, user_name, user_id):
    """Отправка главного меню"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👤 Подписка", callback_data="sub"),
        types.InlineKeyboardButton("⚙ Управление", callback_data="control"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
        types.InlineKeyboardButton("🛠 Техподдержка", callback_data="support"),
        types.InlineKeyboardButton("🌐 Язык", callback_data="change_lang")
    )
    lang = user_lang.get(user_id, "ru")
    bot.send_message(chat_id, tr(MENU_TEXT.format(user=user_name), lang), reply_markup=kb)

def edit_to_main_menu(chat_id, message_id, user_name, user_id):
    """Редактирование сообщения на главное меню"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👤 Подписка", callback_data="sub"),
        types.InlineKeyboardButton("⚙ Управление", callback_data="control"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
        types.InlineKeyboardButton("🛠 Техподдержка", callback_data="support"),
        types.InlineKeyboardButton("🌐 Язык", callback_data="change_lang")
    )
    lang = user_lang.get(user_id, "ru")
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=tr(MENU_TEXT.format(user=user_name), lang),
            reply_markup=kb
        )
    except:
        send_main_menu(chat_id, user_name, user_id)

# ==================== ОБРАБОТЧИКИ CALLBACK ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Главный обработчик всех callback запросов"""
    user_id = call.from_user.id
    data = call.data
    
    # Подтверждаем получение callback
    try:
        bot.answer_callback_query(call.id)
    except:
        pass
    
    # Обработка выбора языка
    if data.startswith("set_lang_"):
        lang = data.split("_")[-1]
        user_lang[user_id] = lang
        send_main_menu(call.message.chat.id, call.from_user.first_name, user_id)
        return
    
    # Главное меню
    if data == "back_main":
        edit_to_main_menu(
            call.message.chat.id, 
            call.message.message_id, 
            call.from_user.first_name, 
            user_id
        )
        return
    
    # Подписка
    if data == "sub":
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"📣 Подпишитесь на канал: {CHANNEL_URL}\nПосле подписки вы получите доступ ко всем функциям бота.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("⬅ Назад", callback_data="back_main")
                )
            )
        except:
            bot.send_message(
                call.message.chat.id,
                f"📣 Подпишитесь на канал: {CHANNEL_URL}\nПосле подписки вы получите доступ ко всем функциям бота."
            )
        return
    
    # Помощь
    if data == "help":
        help_text = tr(HELP_TEXT.replace("$bot", bot.get_me().first_name), user_lang.get(user_id, "ru"))
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_main"))
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=help_text,
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, help_text, reply_markup=kb)
        return
    
    # Техподдержка
    if data == "support":
        support_text = (
            "Здравствуйте, наш менеджер @ilaAkbar67. Напишите ему по любым вопросам.\n"
            "Обязательная подписка на канал: @alphafunpay"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_main"))
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=support_text,
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, support_text, reply_markup=kb)
        return
    
    # Смена языка
    if data == "change_lang":
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("Русский 🇷🇺", callback_data="set_lang_ru"),
            types.InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
        )
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=ASK_LANG_TEXT,
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, ASK_LANG_TEXT, reply_markup=kb)
        return
    
    # Управление
    if data == "control":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("➕ Добавить аккаунт", callback_data="add_account"),
            types.InlineKeyboardButton("🔧 Функции", callback_data="functions"),
            types.InlineKeyboardButton("⬅ Назад", callback_data="back_main")
        )
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⚙ Меню управления",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "⚙ Меню управления", reply_markup=kb)
        return
    
    # Добавление аккаунта
    if data == "add_account":
        msg = bot.send_message(call.message.chat.id, "Пришлите ваш golden_key для подключения FunPay")
        bot.register_next_step_handler(msg, process_add_account)
        return
    
    # Функции
    if data == "functions":
        if user_id not in user_sessions or not user_sessions[user_id].get('accounts'):
            bot.answer_callback_query(call.id, "Сначала добавьте аккаунт", show_alert=True)
            return
        
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("🟢 Онлайн/Оффлайн", callback_data="toggle_online_menu"),
            types.InlineKeyboardButton("↩ Возврат/ЧС", callback_data="returns_menu"),
            types.InlineKeyboardButton("💬 Ключевые слова", callback_data="keywords_menu"),
            types.InlineKeyboardButton("⭐ Автоответ на отзыв", callback_data="auto_review_menu"),
            types.InlineKeyboardButton("⬅ Назад", callback_data="back_control")
        )
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🔧 Функции аккаунтов",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "🔧 Функции аккаунтов", reply_markup=kb)
        return
    
    # Назад в управление
    if data == "back_control":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("➕ Добавить аккаунт", callback_data="add_account"),
            types.InlineKeyboardButton("🔧 Функции", callback_data="functions"),
            types.InlineKeyboardButton("⬅ Назад", callback_data="back_main")
        )
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⚙ Меню управления",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "⚙ Меню управления", reply_markup=kb)
        return
    
    # Онлайн/Оффлайн меню
    if data == "toggle_online_menu":
        kb = build_accounts_keyboard(user_id, callback_prefix="toggle", back_callback="functions")
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🟢 Выберите аккаунт для переключения онлайн/оффлайн",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "🟢 Выберите аккаунт для переключения онлайн/оффлайн", reply_markup=kb)
        return
    
    # Переключение онлайн/оффлайн
    if data.startswith("toggle_"):
        try:
            idx = int(data.split("_")[-1])
            if user_id not in user_sessions or idx >= len(user_sessions[user_id]['accounts']):
                bot.answer_callback_query(call.id, "Ошибка: аккаунт не найден", show_alert=True)
                return
            
            new_status = toggle_online(user_id, idx)
            if new_status is False:
                bot.answer_callback_query(call.id, "Ошибка переключения", show_alert=True)
                return
            
            account_name = user_sessions[user_id]['accounts'][idx]['name']
            status_text = "Онлайн" if new_status else "Оффлайн"
            bot.answer_callback_query(call.id, f"{account_name} теперь {status_text}")
            kb = build_accounts_keyboard(user_id, callback_prefix="toggle", back_callback="functions")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
        except Exception as e:
            bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)
        return
    
    # Возврат/ЧС меню
    if data == "returns_menu":
        kb = build_accounts_keyboard(user_id, callback_prefix="returns_acc", back_callback="functions")
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="↩ Выберите аккаунт для настройки Возврат/ЧС",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "↩ Выберите аккаунт для настройки Возврат/ЧС", reply_markup=kb)
        return
    
    # Настройки возврата для аккаунта
    if data.startswith("returns_acc_"):
        try:
            idx = int(data.split("_")[-1])
            if user_id not in user_sessions or idx >= len(user_sessions[user_id]['accounts']):
                bot.answer_callback_query(call.id, "Ошибка: аккаунт не найден", show_alert=True)
                return
            
            settings = get_return_settings(user_id, idx)
            if settings is None:
                bot.answer_callback_query(call.id, "Ошибка загрузки настроек", show_alert=True)
                return
            
            account_name = user_sessions[user_id]['accounts'][idx]['name']
            
            if settings:
                status = "✅ Включено" if settings.get('enabled', False) else "❌ Выключено"
                text = f"⚙ Настройки Возврат/ЧС для {account_name}\n\n"
                text += f"Статус: {status}\n"
                text += f"Сумма: {settings.get('sum', 0)}\n"
                text += f"Валюта: {settings.get('currency', 'RUB')}\n"
                text += f"Звезды: {settings.get('stars', 0)}\n"
                text += f"Макс. возвратов: {settings.get('max_returns', 0)}\n"
                text += f"Макс. процент: {settings.get('max_percent', 0)}%"
            else:
                text = "Ошибка загрузки настроек"
            
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                types.InlineKeyboardButton(
                    "✅ Включить" if not settings.get('enabled', False) else "❌ Выключить",
                    callback_data=f"returns_toggle_{idx}"
                ),
                types.InlineKeyboardButton("💰 Настроить сумму", callback_data=f"returns_sum_{idx}"),
                types.InlineKeyboardButton("💱 Настроить валюту", callback_data=f"returns_currency_{idx}"),
                types.InlineKeyboardButton("⭐ Настроить звезды", callback_data=f"returns_stars_{idx}"),
                types.InlineKeyboardButton("🔢 Макс. возвратов", callback_data=f"returns_max_{idx}"),
                types.InlineKeyboardButton("📊 Макс. процент", callback_data=f"returns_percent_{idx}"),
                types.InlineKeyboardButton("⬅ Назад", callback_data="returns_menu")
            )
            bot.edit_message_text(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        except Exception as e:
            bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)
        return
    
    # Переключение возврата
    if data.startswith("returns_toggle_"):
        try:
            idx = int(data.split("_")[-1])
            settings = get_return_settings(user_id, idx)
            if settings:
                settings['enabled'] = not settings.get('enabled', False)
                set_return_settings(user_id, idx, settings)
                status_text = "включен" if settings['enabled'] else "выключен"
                bot.answer_callback_query(call.id, f"Возврат/ЧС {status_text}")
                # Обновляем меню
                call.data = f"returns_acc_{idx}"
                callback_handler(call)
        except Exception as e:
            bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)
        return
    
    # Настройка суммы возврата
    if data.startswith("returns_sum_"):
        idx = int(data.split("_")[-1])
        msg = bot.send_message(call.message.chat.id, "💰 Введите сумму для возврата (число):")
        bot.register_next_step_handler(msg, lambda m: process_return_sum(m, user_id, idx))
        return
    
    # Настройка валюты
    if data.startswith("returns_currency_"):
        idx = int(data.split("_")[-1])
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("RUB", callback_data=f"returns_currency_set_{idx}_RUB"),
            types.InlineKeyboardButton("USD", callback_data=f"returns_currency_set_{idx}_USD"),
            types.InlineKeyboardButton("EUR", callback_data=f"returns_currency_set_{idx}_EUR")
        )
        bot.send_message(call.message.chat.id, "💱 Выберите валюту:", reply_markup=kb)
        return
    
    # Установка валюты
    if data.startswith("returns_currency_set_"):
        parts = data.split("_")
        idx = int(parts[-2])
        currency = parts[-1]
        settings = get_return_settings(user_id, idx)
        if settings:
            settings['currency'] = currency
            set_return_settings(user_id, idx, settings)
            bot.answer_callback_query(call.id, f"Валюта установлена: {currency}")
            call.data = f"returns_acc_{idx}"
            callback_handler(call)
        return
    
    # Настройка звезд
    if data.startswith("returns_stars_"):
        idx = int(data.split("_")[-1])
        msg = bot.send_message(call.message.chat.id, "⭐ Введите минимальное количество звезд (0-5):")
        bot.register_next_step_handler(msg, lambda m: process_return_stars(m, user_id, idx))
        return
    
    # Настройка макс. возвратов
    if data.startswith("returns_max_"):
        idx = int(data.split("_")[-1])
        msg = bot.send_message(call.message.chat.id, "🔢 Введите максимальное количество возвратов:")
        bot.register_next_step_handler(msg, lambda m: process_return_max(m, user_id, idx))
        return
    
    # Настройка процента
    if data.startswith("returns_percent_"):
        idx = int(data.split("_")[-1])
        msg = bot.send_message(call.message.chat.id, "📊 Введите максимальный процент возврата (0-100):")
        bot.register_next_step_handler(msg, lambda m: process_return_percent(m, user_id, idx))
        return
    
    # Ключевые слова меню
    if data == "keywords_menu":
        kb = build_accounts_keyboard(user_id, callback_prefix="keywords_acc", back_callback="functions")
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="💬 Выберите аккаунт для настройки ключевых слов",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "💬 Выберите аккаунт для настройки ключевых слов", reply_markup=kb)
        return
    
    # Ключевые слова для аккаунта
    if data.startswith("keywords_acc_"):
        try:
            idx = int(data.split("_")[-1])
            if user_id not in user_sessions or idx >= len(user_sessions[user_id]['accounts']):
                bot.answer_callback_query(call.id, "Ошибка: аккаунт не найден", show_alert=True)
                return
            
            keywords = get_keywords(user_id, idx)
            account_name = user_sessions[user_id]['accounts'][idx]['name']
            text = f"💬 Ключевые слова для {account_name}\n\n"
            
            if keywords:
                for i, kw in enumerate(keywords):
                    status = "✅" if kw.get('enabled', False) else "❌"
                    text += f"{i+1}. {status} {kw.get('keyword', '')} → {kw.get('response', '')[:30]}...\n"
            else:
                text += "Нет настроенных ключевых слов"
            
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                types.InlineKeyboardButton("➕ Добавить ключевое слово", callback_data=f"keywords_add_{idx}"),
                types.InlineKeyboardButton("📝 Список ключевых слов", callback_data=f"keywords_list_{idx}"),
                types.InlineKeyboardButton("⬅ Назад", callback_data="keywords_menu")
            )
            bot.edit_message_text(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        except Exception as e:
            bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)
        return
    
    # Добавление ключевого слова
    if data.startswith("keywords_add_"):
        idx = int(data.split("_")[-1])
        msg = bot.send_message(call.message.chat.id, "💬 Введите ключевое слово:")
        bot.register_next_step_handler(msg, lambda m: process_keyword_word(m, user_id, idx))
        return
    
    # Список ключевых слов
    if data.startswith("keywords_list_"):
        idx = int(data.split("_")[-1])
        keywords = get_keywords(user_id, idx)
        if not keywords:
            bot.answer_callback_query(call.id, "Нет ключевых слов", show_alert=True)
            return
        
        text = "📝 Список ключевых слов:\n\n"
        kb = types.InlineKeyboardMarkup(row_width=1)
        for i, kw in enumerate(keywords):
            status = "✅" if kw.get('enabled', False) else "❌"
            text += f"{i+1}. {status} {kw.get('keyword', '')}\n"
            kb.add(types.InlineKeyboardButton(f"{i+1}. {kw.get('keyword', '')}", callback_data=f"keywords_edit_{idx}_{i}"))
        kb.add(types.InlineKeyboardButton("⬅ Назад", callback_data=f"keywords_acc_{idx}"))
        try:
            bot.edit_message_text(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        except:
            bot.send_message(call.message.chat.id, text, reply_markup=kb)
        return
    
    # Редактирование ключевого слова
    if data.startswith("keywords_edit_"):
        parts = data.split("_")
        idx = int(parts[-2])
        kw_idx = int(parts[-1])
        keywords = get_keywords(user_id, idx)
        if kw_idx < len(keywords):
            kw = keywords[kw_idx]
            text = f"📝 Редактирование ключевого слова:\n\n"
            text += f"Ключевое слово: {kw.get('keyword', '')}\n"
            text += f"Ответ: {kw.get('response', '')}\n"
            text += f"Статус: {'Включено' if kw.get('enabled', False) else 'Выключено'}"
            
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                types.InlineKeyboardButton(
                    "✅ Включить" if not kw.get('enabled', False) else "❌ Выключить",
                    callback_data=f"keywords_toggle_{idx}_{kw_idx}"
                ),
                types.InlineKeyboardButton("✏ Изменить ответ", callback_data=f"keywords_change_response_{idx}_{kw_idx}"),
                types.InlineKeyboardButton("🗑 Удалить", callback_data=f"keywords_delete_{idx}_{kw_idx}"),
                types.InlineKeyboardButton("⬅ Назад", callback_data=f"keywords_list_{idx}")
            )
            try:
                bot.edit_message_text(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
            except:
                bot.send_message(call.message.chat.id, text, reply_markup=kb)
        return
    
    # Переключение ключевого слова
    if data.startswith("keywords_toggle_"):
        parts = data.split("_")
        idx = int(parts[-2])
        kw_idx = int(parts[-1])
        keywords = get_keywords(user_id, idx)
        if kw_idx < len(keywords):
            keywords[kw_idx]['enabled'] = not keywords[kw_idx].get('enabled', False)
            status_text = "включено" if keywords[kw_idx]['enabled'] else "выключено"
            bot.answer_callback_query(call.id, f"Ключевое слово {status_text}")
            call.data = f"keywords_edit_{idx}_{kw_idx}"
            callback_handler(call)
        return
    
    # Изменение ответа ключевого слова
    if data.startswith("keywords_change_response_"):
        parts = data.split("_")
        idx = int(parts[-2])
        kw_idx = int(parts[-1])
        msg = bot.send_message(call.message.chat.id, "✏ Введите новый ответ:")
        bot.register_next_step_handler(msg, lambda m: process_keyword_response_change(m, user_id, idx, kw_idx))
        return
    
    # Удаление ключевого слова
    if data.startswith("keywords_delete_"):
        parts = data.split("_")
        idx = int(parts[-2])
        kw_idx = int(parts[-1])
        if remove_keyword(user_id, idx, kw_idx):
            bot.answer_callback_query(call.id, "Ключевое слово удалено")
            call.data = f"keywords_list_{idx}"
            callback_handler(call)
        else:
            bot.answer_callback_query(call.id, "Ошибка удаления", show_alert=True)
        return
    
    # Автоответ на отзыв меню
    if data == "auto_review_menu":
        kb = build_accounts_keyboard(user_id, callback_prefix="auto_review_acc", back_callback="functions")
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⭐ Выберите аккаунт для настройки автоответа на отзывы",
                reply_markup=kb
            )
        except:
            bot.send_message(call.message.chat.id, "⭐ Выберите аккаунт для настройки автоответа на отзывы", reply_markup=kb)
        return
    
    # Автоответ на отзыв для аккаунта
    if data.startswith("auto_review_acc_"):
        try:
            idx = int(data.split("_")[-1])
            if user_id not in user_sessions or idx >= len(user_sessions[user_id]['accounts']):
                bot.answer_callback_query(call.id, "Ошибка: аккаунт не найден", show_alert=True)
                return
            
            review_settings = get_auto_review_response(user_id, idx)
            if review_settings is None:
                bot.answer_callback_query(call.id, "Ошибка загрузки настроек", show_alert=True)
                return
            
            account_name = user_sessions[user_id]['accounts'][idx]['name']
            
            if review_settings:
                status = "✅ Включено" if review_settings.get('enabled', False) else "❌ Выключено"
                response = review_settings.get('response_text', 'Не настроено')
                text = f"⭐ Автоответ на отзыв для {account_name}\n\n"
                text += f"Статус: {status}\n"
                text += f"Ответ: {response[:100]}{'...' if len(response) > 100 else ''}"
            else:
                text = "Ошибка загрузки настроек"
            
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                types.InlineKeyboardButton(
                    "✅ Включить" if not review_settings.get('enabled', False) else "❌ Выключить",
                    callback_data=f"auto_review_toggle_{idx}"
                ),
                types.InlineKeyboardButton("✏ Настроить ответ", callback_data=f"auto_review_set_{idx}"),
                types.InlineKeyboardButton("⬅ Назад", callback_data="auto_review_menu")
            )
            bot.edit_message_text(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        except Exception as e:
            bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)
        return
    
    # Переключение автоответа на отзыв
    if data.startswith("auto_review_toggle_"):
        idx = int(data.split("_")[-1])
        review_settings = get_auto_review_response(user_id, idx)
        if review_settings:
            new_status = not review_settings.get('enabled', False)
            set_auto_review_response(user_id, idx, new_status, review_settings.get('response_text', ''))
            status_text = "включен" if new_status else "выключен"
            bot.answer_callback_query(call.id, f"Автоответ на отзыв {status_text}")
            call.data = f"auto_review_acc_{idx}"
            callback_handler(call)
        return
    
    # Настройка ответа на отзыв
    if data.startswith("auto_review_set_"):
        idx = int(data.split("_")[-1])
        msg = bot.send_message(call.message.chat.id, "✏ Введите текст ответа на отзыв:")
        bot.register_next_step_handler(msg, lambda m: process_auto_review_response(m, user_id, idx))
        return

# ==================== ОБРАБОТЧИКИ ВВОДА ====================

def process_add_account(message):
    """Обработка добавления аккаунта"""
    user_id = message.from_user.id
    success, result = add_account(user_id, message.text.strip())
    if success:
        bot.send_message(message.chat.id, f"Аккаунт {result} добавлен и включён онлайн 👍")
    else:
        bot.send_message(message.chat.id, f"Ошибка подключения ❌: {result}")

def process_return_sum(message, user_id, idx):
    """Обработка ввода суммы возврата"""
    try:
        sum_value = float(message.text.strip())
        settings = get_return_settings(user_id, idx)
        if settings:
            settings['sum'] = sum_value
            set_return_settings(user_id, idx, settings)
            bot.send_message(message.chat.id, f"✅ Сумма установлена: {sum_value}")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка: настройки не найдены")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка: введите число")

def process_return_stars(message, user_id, idx):
    """Обработка ввода звезд"""
    try:
        stars = int(message.text.strip())
        if 0 <= stars <= 5:
            settings = get_return_settings(user_id, idx)
            if settings:
                settings['stars'] = stars
                set_return_settings(user_id, idx, settings)
                bot.send_message(message.chat.id, f"✅ Звезды установлены: {stars}")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка: настройки не найдены")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка: введите число от 0 до 5")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка: введите число")

def process_return_max(message, user_id, idx):
    """Обработка ввода макс. возвратов"""
    try:
        max_returns = int(message.text.strip())
        if max_returns >= 0:
            settings = get_return_settings(user_id, idx)
            if settings:
                settings['max_returns'] = max_returns
                set_return_settings(user_id, idx, settings)
                bot.send_message(message.chat.id, f"✅ Максимальное количество возвратов установлено: {max_returns}")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка: настройки не найдены")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка: введите положительное число")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка: введите число")

def process_return_percent(message, user_id, idx):
    """Обработка ввода процента"""
    try:
        percent = float(message.text.strip())
        if 0 <= percent <= 100:
            settings = get_return_settings(user_id, idx)
            if settings:
                settings['max_percent'] = percent
                set_return_settings(user_id, idx, settings)
                bot.send_message(message.chat.id, f"✅ Максимальный процент установлен: {percent}%")
            else:
                bot.send_message(message.chat.id, "❌ Ошибка: настройки не найдены")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка: введите число от 0 до 100")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка: введите число")

def process_keyword_word(message, user_id, idx):
    """Обработка ввода ключевого слова"""
    keyword = message.text.strip()
    if not keyword:
        bot.send_message(message.chat.id, "❌ Ошибка: ключевое слово не может быть пустым")
        return
    msg = bot.send_message(message.chat.id, "💬 Теперь введите ответ на это ключевое слово:")
    bot.register_next_step_handler(msg, lambda m: process_keyword_response(m, user_id, idx, keyword))

def process_keyword_response(message, user_id, idx, keyword):
    """Обработка ввода ответа на ключевое слово"""
    response = message.text.strip()
    if not response:
        bot.send_message(message.chat.id, "❌ Ошибка: ответ не может быть пустым")
        return
    keyword_data = {
        "keyword": keyword,
        "response": response,
        "enabled": True
    }
    add_keyword_response(user_id, idx, keyword_data)
    bot.send_message(message.chat.id, f"✅ Ключевое слово добавлено:\n{keyword} → {response}")

def process_keyword_response_change(message, user_id, idx, kw_idx):
    """Обработка изменения ответа ключевого слова"""
    response = message.text.strip()
    if not response:
        bot.send_message(message.chat.id, "❌ Ошибка: ответ не может быть пустым")
        return
    keywords = get_keywords(user_id, idx)
    if kw_idx < len(keywords):
        keywords[kw_idx]['response'] = response
        bot.send_message(message.chat.id, f"✅ Ответ обновлен: {response}")

def process_auto_review_response(message, user_id, idx):
    """Обработка ввода ответа на отзыв"""
    response_text = message.text.strip()
    if not response_text:
        bot.send_message(message.chat.id, "❌ Ошибка: ответ не может быть пустым")
        return
    review_settings = get_auto_review_response(user_id, idx)
    enabled = review_settings.get('enabled', False) if review_settings else False
    set_auto_review_response(user_id, idx, enabled, response_text)
    bot.send_message(message.chat.id, f"✅ Ответ на отзыв установлен:\n{response_text}")

# ==================== ЗАПУСК БОТА ====================

if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling()
