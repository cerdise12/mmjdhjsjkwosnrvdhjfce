from telebot import types
from funpayace import FunpayAce, FunpayConfig
from config import user_sessions
import threading

def add_account(user_id, golden_key):
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

def setup_funpay_handlers(user_id, account_index, client):
    """Настройка обработчиков событий FunPay для аккаунта"""
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

def handle_new_message(user_id, account_index, message, client):
    """Обработка нового сообщения"""
    if user_id not in user_sessions or account_index >= len(user_sessions[user_id]['accounts']):
        return
    
    account = user_sessions[user_id]['accounts'][account_index]
    if not account.get('online', False):
        return
    
    # Обработка ключевых слов
    if account.get('keywords'):
        message_text = ""
        try:
            if hasattr(message, 'text'):
                message_text = message.text.lower() if message.text else ""
            elif isinstance(message, dict):
                message_text = message.get('text', '').lower()
            elif isinstance(message, str):
                message_text = message.lower()
        except:
            pass
        
        for keyword_data in account['keywords']:
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
                        except Exception as e:
                            pass
                    break

def handle_new_order(user_id, account_index, order, client):
    """Обработка нового заказа"""
    if user_id not in user_sessions or account_index >= len(user_sessions[user_id]['accounts']):
        return
    
    account = user_sessions[user_id]['accounts'][account_index]
    if not account.get('online', False):
        return
    
    # Обработка возвратов/ЧС
    if account.get('return_settings', {}).get('enabled', False):
        settings = account['return_settings']
        # Логика обработки возвратов
        # Проверка условий возврата (сумма, валюта, звезды и т.д.)
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
            if settings.get('sum', 0) > 0 and order_sum < settings['sum']:
                return
            if settings.get('currency') and order_currency != settings['currency']:
                return
            if settings.get('stars', 0) > 0 and order_stars < settings['stars']:
                return
            
            # Здесь можно добавить логику автоматического возврата
            # в зависимости от API FunpayAce
        except:
            pass

def handle_new_review(user_id, account_index, review, client):
    """Обработка нового отзыва"""
    if user_id not in user_sessions or account_index >= len(user_sessions[user_id]['accounts']):
        return
    
    account = user_sessions[user_id]['accounts'][account_index]
    if not account.get('online', False):
        return
    
    # Автоответ на отзыв
    if account.get('auto_review_response', {}).get('enabled', False):
        response_text = account['auto_review_response'].get('response_text', '')
        if response_text:
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
            except Exception as e:
                pass

def toggle_online(user_id, index):
    account = user_sessions[user_id]['accounts'][index]
    client = account['client']
    if account['online']:
        try:
            client.cancel_background_tasks()
        except:
            pass
        account['online'] = False
    else:
        client.run_forever_online_in_thread()
        account['online'] = True
    return account['online']

def build_accounts_keyboard(user_id, callback_prefix="acc"):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if user_id in user_sessions and user_sessions[user_id]['accounts']:
        for i, acc in enumerate(user_sessions[user_id]['accounts']):
            status = "Онлайн" if acc['online'] else "Оффлайн"
            kb.add(types.InlineKeyboardButton(f"{acc['name']} ({status})", callback_data=f"{callback_prefix}_{i}"))
    kb.add(types.InlineKeyboardButton("⬅ Назад", callback_data="functions"))
    return kb

def set_return_settings(user_id, index, settings):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        account = user_sessions[user_id]['accounts'][index]
        account['return_settings'] = settings

def get_return_settings(user_id, index):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        return user_sessions[user_id]['accounts'][index]['return_settings']
    return None

def add_keyword_response(user_id, index, keyword_data):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        account = user_sessions[user_id]['accounts'][index]
        account['keywords'].append(keyword_data)

def get_keywords(user_id, index):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        return user_sessions[user_id]['accounts'][index]['keywords']
    return []

def remove_keyword(user_id, index, keyword_index):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        account = user_sessions[user_id]['accounts'][index]
        if keyword_index < len(account['keywords']):
            account['keywords'].pop(keyword_index)
            return True
    return False

def set_auto_review_response(user_id, index, enabled, response_text=""):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        account = user_sessions[user_id]['accounts'][index]
        account['auto_review_response'] = {
            "enabled": enabled,
            "response_text": response_text
        }
        return True
    return False

def get_auto_review_response(user_id, index):
    if user_id in user_sessions and index < len(user_sessions[user_id]['accounts']):
        return user_sessions[user_id]['accounts'][index]['auto_review_response']
    return None
