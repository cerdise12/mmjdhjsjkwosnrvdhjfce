from telebot import types
from funpayace import FunpayAce, FunpayConfig
from config import user_sessions

# ==================== УПРАВЛЕНИЕ АККАУНТАМИ ====================

def add_account(user_id, golden_key):
    """Добавление нового аккаунта FunPay"""
    try:
        config = FunpayConfig()
        client = FunpayAce(golden_key=golden_key, config=config)
        client.run_forever_online_in_thread()
        
        if user_id not in user_sessions:
            user_sessions[user_id] = {"accounts": []}
        
        acc_name = f"acc{len(user_sessions[user_id]['accounts'])+1}"
        account_data = {
            "client": client,
            "online": True,
            "name": acc_name,
            "return_settings": {
                "enabled": False,
                "sum": 0,
                "currency": "RUB",
                "stars": 0,
                "max_returns": 0,
                "max_percent": 0
            },
            "keywords": [],
            "auto_review_response": {
                "enabled": False,
                "response_text": ""
            }
        }
        user_sessions[user_id]['accounts'].append(account_data)
        
        # Настройка обработчиков событий FunPay
        setup_funpay_handlers(user_id, len(user_sessions[user_id]['accounts']) - 1, client)
        
        return True, acc_name
    except Exception as e:
        return False, str(e)

def toggle_online(user_id, index):
    """Переключение статуса онлайн/оффлайн для аккаунта"""
    try:
        if user_id not in user_sessions:
            return False
        if index >= len(user_sessions[user_id]['accounts']):
            return False
        
        account = user_sessions[user_id]['accounts'][index]
        client = account['client']
        
        if account['online']:
            try:
                client.cancel_background_tasks()
            except:
                pass
            account['online'] = False
        else:
            try:
                client.run_forever_online_in_thread()
            except:
                pass
            account['online'] = True
        
        return account['online']
    except Exception as e:
        return False

def build_accounts_keyboard(user_id, callback_prefix="acc", back_callback="back_control"):
    """Создание клавиатуры со списком аккаунтов"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {"accounts": []}
    
    accounts = user_sessions[user_id].get('accounts', [])
    
    if not accounts:
        kb.add(types.InlineKeyboardButton("⬅ Назад", callback_data=back_callback))
        return kb
    
    for i, acc in enumerate(accounts):
        status = "🟢 Онлайн" if acc.get('online', False) else "🔴 Оффлайн"
        button_text = f"{acc.get('name', f'acc{i+1}')} ({status})"
        kb.add(types.InlineKeyboardButton(button_text, callback_data=f"{callback_prefix}_{i}"))
    
    kb.add(types.InlineKeyboardButton("⬅ Назад", callback_data=back_callback))
    return kb

# ==================== НАСТРОЙКИ ВОЗВРАТОВ ====================

def set_return_settings(user_id, index, settings):
    """Установка настроек возврата для аккаунта"""
    try:
        if user_id not in user_sessions:
            return False
        if index >= len(user_sessions[user_id]['accounts']):
            return False
        
        account = user_sessions[user_id]['accounts'][index]
        account['return_settings'] = settings
        return True
    except:
        return False

def get_return_settings(user_id, index):
    """Получение настроек возврата для аккаунта"""
    try:
        if user_id not in user_sessions:
            return None
        if index >= len(user_sessions[user_id]['accounts']):
            return None
        
        account = user_sessions[user_id]['accounts'][index]
        return account.get('return_settings', {
            "enabled": False,
            "sum": 0,
            "currency": "RUB",
            "stars": 0,
            "max_returns": 0,
            "max_percent": 0
        })
    except:
        return None

# ==================== КЛЮЧЕВЫЕ СЛОВА ====================

def add_keyword_response(user_id, index, keyword_data):
    """Добавление ключевого слова с ответом"""
    try:
        if user_id not in user_sessions:
            return False
        if index >= len(user_sessions[user_id]['accounts']):
            return False
        
        account = user_sessions[user_id]['accounts'][index]
        if 'keywords' not in account:
            account['keywords'] = []
        account['keywords'].append(keyword_data)
        return True
    except:
        return False

def get_keywords(user_id, index):
    """Получение списка ключевых слов для аккаунта"""
    try:
        if user_id not in user_sessions:
            return []
        if index >= len(user_sessions[user_id]['accounts']):
            return []
        
        account = user_sessions[user_id]['accounts'][index]
        return account.get('keywords', [])
    except:
        return []

def remove_keyword(user_id, index, keyword_index):
    """Удаление ключевого слова"""
    try:
        if user_id not in user_sessions:
            return False
        if index >= len(user_sessions[user_id]['accounts']):
            return False
        
        account = user_sessions[user_id]['accounts'][index]
        keywords = account.get('keywords', [])
        
        if keyword_index < len(keywords):
            keywords.pop(keyword_index)
            return True
        return False
    except:
        return False

# ==================== АВТООТВЕТ НА ОТЗЫВЫ ====================

def set_auto_review_response(user_id, index, enabled, response_text=""):
    """Установка настроек автоответа на отзыв"""
    try:
        if user_id not in user_sessions:
            return False
        if index >= len(user_sessions[user_id]['accounts']):
            return False
        
        account = user_sessions[user_id]['accounts'][index]
        account['auto_review_response'] = {
            "enabled": enabled,
            "response_text": response_text
        }
        return True
    except:
        return False

def get_auto_review_response(user_id, index):
    """Получение настроек автоответа на отзыв"""
    try:
        if user_id not in user_sessions:
            return None
        if index >= len(user_sessions[user_id]['accounts']):
            return None
        
        account = user_sessions[user_id]['accounts'][index]
        return account.get('auto_review_response', {
            "enabled": False,
            "response_text": ""
        })
    except:
        return None

# ==================== ОБРАБОТЧИКИ FUNPAY ====================

def setup_funpay_handlers(user_id, account_index, client):
    """Настройка обработчиков событий FunPay для аккаунта"""
    try:
        if user_id not in user_sessions:
            return
        if account_index >= len(user_sessions[user_id]['accounts']):
            return
        
        account = user_sessions[user_id]['accounts'][account_index]
        
        # Обработчик новых сообщений
        try:
            if hasattr(client, 'on_new_message'):
                @client.on_new_message
                def on_new_message(message):
                    handle_new_message(user_id, account_index, message, client)
            elif hasattr(client, 'add_message_handler'):
                client.add_message_handler(lambda msg: handle_new_message(user_id, account_index, msg, client))
        except:
            pass
        
        # Обработчик новых заказов
        try:
            if hasattr(client, 'on_new_order'):
                @client.on_new_order
                def on_new_order(order):
                    handle_new_order(user_id, account_index, order, client)
            elif hasattr(client, 'add_order_handler'):
                client.add_order_handler(lambda order: handle_new_order(user_id, account_index, order, client))
        except:
            pass
        
        # Обработчик новых отзывов
        try:
            if hasattr(client, 'on_new_review'):
                @client.on_new_review
                def on_new_review(review):
                    handle_new_review(user_id, account_index, review, client)
            elif hasattr(client, 'add_review_handler'):
                client.add_review_handler(lambda review: handle_new_review(user_id, account_index, review, client))
        except:
            pass
    except:
        pass

def handle_new_message(user_id, account_index, message, client):
    """Обработка нового сообщения"""
    try:
        if user_id not in user_sessions:
            return
        if account_index >= len(user_sessions[user_id]['accounts']):
            return
        
        account = user_sessions[user_id]['accounts'][account_index]
        if not account.get('online', False):
            return
        
        # Обработка ключевых слов
        keywords = account.get('keywords', [])
        if not keywords:
            return
        
        message_text = ""
        try:
            if hasattr(message, 'text'):
                message_text = message.text.lower() if message.text else ""
            elif isinstance(message, dict):
                message_text = message.get('text', '').lower()
            elif isinstance(message, str):
                message_text = message.lower()
        except:
            return
        
        for keyword_data in keywords:
            if keyword_data.get('enabled', False):
                keyword = keyword_data.get('keyword', '').lower()
                if keyword and keyword in message_text:
                    response_text = keyword_data.get('response', '')
                    if response_text:
                        try:
                            chat_id = None
                            if hasattr(message, 'chat_id'):
                                chat_id = message.chat_id
                            elif hasattr(message, 'chat'):
                                chat_id = message.chat.id if hasattr(message.chat, 'id') else message.chat
                            elif isinstance(message, dict):
                                chat_id = message.get('chat_id') or message.get('chat', {}).get('id')
                            
                            if chat_id:
                                if hasattr(client, 'send_message'):
                                    client.send_message(chat_id, response_text)
                                elif hasattr(client, 'reply'):
                                    client.reply(message, response_text)
                        except:
                            pass
                    break
    except:
        pass

def handle_new_order(user_id, account_index, order, client):
    """Обработка нового заказа"""
    try:
        if user_id not in user_sessions:
            return
        if account_index >= len(user_sessions[user_id]['accounts']):
            return
        
        account = user_sessions[user_id]['accounts'][account_index]
        if not account.get('online', False):
            return
        
        # Обработка возвратов/ЧС
        return_settings = account.get('return_settings', {})
        if not return_settings.get('enabled', False):
            return
        
        # Логика обработки возвратов
        try:
            order_sum = 0
            order_currency = "RUB"
            order_stars = 0
            
            if hasattr(order, 'sum'):
                order_sum = order.sum
            elif isinstance(order, dict):
                order_sum = order.get('sum', 0)
                order_currency = order.get('currency', 'RUB')
                order_stars = order.get('stars', 0)
            
            # Проверка условий
            if return_settings.get('sum', 0) > 0 and order_sum < return_settings['sum']:
                return
            if return_settings.get('currency') and order_currency != return_settings['currency']:
                return
            if return_settings.get('stars', 0) > 0 and order_stars < return_settings['stars']:
                return
            
            # Здесь можно добавить логику автоматического возврата
        except:
            pass
    except:
        pass

def handle_new_review(user_id, account_index, review, client):
    """Обработка нового отзыва"""
    try:
        if user_id not in user_sessions:
            return
        if account_index >= len(user_sessions[user_id]['accounts']):
            return
        
        account = user_sessions[user_id]['accounts'][account_index]
        if not account.get('online', False):
            return
        
        # Автоответ на отзыв
        auto_review = account.get('auto_review_response', {})
        if not auto_review.get('enabled', False):
            return
        
        response_text = auto_review.get('response_text', '')
        if not response_text:
            return
        
        try:
            review_id = None
            if hasattr(review, 'id'):
                review_id = review.id
            elif isinstance(review, dict):
                review_id = review.get('id')
            
            if review_id:
                if hasattr(client, 'respond_to_review'):
                    client.respond_to_review(review_id, response_text)
                elif hasattr(client, 'reply_to_review'):
                    client.reply_to_review(review_id, response_text)
                elif hasattr(client, 'send_review_response'):
                    client.send_review_response(review_id, response_text)
        except:
            pass
    except:
        pass
