import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
import requests
import re
import logging
from telebot import types
import time
from datetime import datetime, timedelta
import signal
import psutil
import sqlite3
import threading
import base64

# Cấu hình logging để debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = '8229532769:AAEmi_-iTE5aNWHF19-OYGsK4HC6dQCVubM'  # Your bot token
ADMIN_ID = 7509896689  # Your admin ID
YOUR_USERNAME = '@doanhvip12'  # Your username with @

print("🚀 Đang khởi động bot...")
logger.info("Bot starting...")

try:
    bot = telebot.TeleBot(TOKEN)
    print("✅ Bot được khởi tạo thành công")
    logger.info("Bot initialized successfully")
except Exception as e:
    print(f"❌ Lỗi khởi tạo bot: {e}")
    logger.error(f"Bot initialization failed: {e}")
    exit(1)

uploaded_files_dir = 'uploaded_bots'
bot_scripts = {}
stored_tokens = {}
user_subscriptions = {}  
user_files = {}  
active_users = set()  

bot_locked = False
free_mode = False  

if not os.path.exists(uploaded_files_dir):
    os.makedirs(uploaded_files_dir)

def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_files
                 (user_id INTEGER, file_name TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS active_users
                 (user_id INTEGER PRIMARY KEY)''')
    
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM subscriptions')
    subscriptions = c.fetchall()
    for user_id, expiry in subscriptions:
        user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
    
    c.execute('SELECT * FROM user_files')
    user_files_data = c.fetchall()
    for user_id, file_name in user_files_data:
        if user_id not in user_files:
            user_files[user_id] = []
        user_files[user_id].append(file_name)
    
    c.execute('SELECT * FROM active_users')
    active_users_data = c.fetchall()
    for user_id, in active_users_data:
        active_users.add(user_id)
    
    conn.close()

def save_subscription(user_id, expiry):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', 
              (user_id, expiry.isoformat()))
    conn.commit()
    conn.close()

def remove_subscription_db(user_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def save_user_file(user_id, file_name):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO user_files (user_id, file_name) VALUES (?, ?)', 
              (user_id, file_name))
    conn.commit()
    conn.close()

def remove_user_file_db(user_id, file_name):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', 
              (user_id, file_name))
    conn.commit()
    conn.close()

def add_active_user(user_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def remove_active_user(user_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM active_users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

init_db()
load_data()

def create_main_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    upload_button = types.InlineKeyboardButton('📤 Tải File Lên', callback_data='upload')
    speed_button = types.InlineKeyboardButton('⚡ Tốc Độ Bot', callback_data='speed')
    contact_button = types.InlineKeyboardButton('📞 Liên Hệ Chủ Bot', url=f'https://t.me/{YOUR_USERNAME[1:]}')
    if user_id == ADMIN_ID:
        subscription_button = types.InlineKeyboardButton('💳 Quản Lý Gói', callback_data='subscription')
        stats_button = types.InlineKeyboardButton('📊 Thống Kê', callback_data='stats')
        lock_button = types.InlineKeyboardButton('🔒 Khóa Bot', callback_data='lock_bot')
        unlock_button = types.InlineKeyboardButton('🔓 Mở Khóa Bot', callback_data='unlock_bot')
        free_mode_button = types.InlineKeyboardButton('🔓 Chế Độ Miễn Phí', callback_data='free_mode')
        broadcast_button = types.InlineKeyboardButton('📢 Phát Thông Báo', callback_data='broadcast')
        markup.add(upload_button)
        markup.add(speed_button, subscription_button, stats_button)
        markup.add(lock_button, unlock_button, free_mode_button)
        markup.add(broadcast_button)
    else:
        markup.add(upload_button)
        markup.add(speed_button)
    markup.add(contact_button)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if bot_locked:
        bot.send_message(message.chat.id, "⚠️ Bot hiện đang bị khóa. Vui lòng thử lại sau.")
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username

    try:
        user_profile = bot.get_chat(user_id)
        user_bio = user_profile.bio if user_profile.bio else "Không có tiểu sử"
    except Exception as e:
        print(f"❌ Lỗi khi lấy tiểu sử: {e}")
        user_bio = "Không có tiểu sử"

    try:
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos:
            photo_file_id = user_profile_photos.photos[0][-1].file_id  
        else:
            photo_file_id = None
    except Exception as e:
        print(f"❌ Lỗi khi lấy ảnh đại diện: {e}")
        photo_file_id = None

    if user_id not in active_users:
        active_users.add(user_id)  
        add_active_user(user_id)  

        try:
            welcome_message_to_admin = f"🎉 Người dùng mới tham gia bot!\n\n"
            welcome_message_to_admin += f"👤 Tên: {user_name}\n"
            welcome_message_to_admin += f"📌 Username: @{user_username}\n"
            welcome_message_to_admin += f"🆔 ID: {user_id}\n"
            welcome_message_to_admin += f"📝 Tiểu sử: {user_bio}\n"

            if photo_file_id:
                bot.send_photo(ADMIN_ID, photo_file_id, caption=welcome_message_to_admin)
            else:
                bot.send_message(ADMIN_ID, welcome_message_to_admin)
        except Exception as e:
            print(f"❌ Lỗi khi gửi thông tin người dùng cho admin: {e}")

    welcome_message = f"〽️┇Chào mừng: {user_name}\n"
    welcome_message += f"🆔┇ID của bạn: {user_id}\n"
    welcome_message += f"♻️┇Username: @{user_username}\n"
    welcome_message += f"📰┇Tiểu sử: {user_bio}\n\n"
    welcome_message += "〽️ Tôi là bot lưu trữ file Python 🎗\n\n"
    welcome_message += "📋 **LỆNH CƠ BẢN:**\n"
    welcome_message += "📤 `/upload` - Tải file lên\n"
    welcome_message += "⚡ `/speed` - Kiểm tra tốc độ bot\n"
    welcome_message += "📞 `/contact` - Liên hệ chủ bot\n"
    welcome_message += "⏹️ `/stop` - Dừng bot đang chạy\n"
    welcome_message += "🗑️ `/delete` - Xóa file bot\n"
    welcome_message += "📊 `/status` - Xem trạng thái\n"
    welcome_message += "📂 `/myfiles` - Xem file đã tải\n"
    welcome_message += "❓ `/help` - Xem tất cả lệnh\n"
    if user_id == ADMIN_ID:
        welcome_message += "\n🔧 **LỆNH ADMIN:**\n"
        welcome_message += "💳 `/subscription` - Quản lý gói đăng ký\n"
        welcome_message += "📊 `/stats` - Xem thống kê\n"
        welcome_message += "🔒 `/lock` - Khóa bot\n"
        welcome_message += "🔓 `/unlock` - Mở khóa bot\n"
        welcome_message += "🆓 `/freemode` - Bật/tắt chế độ miễn phí\n"
        welcome_message += "📢 `/broadcast` - Phát thông báo\n"
        welcome_message += "👥 `/user_files <user_id>` - Xem file của user\n"
        welcome_message += "🗑️ `/delete_user_file <user_id> <file_name>` - Xóa file\n"
        welcome_message += "⏹️ `/stop_user_bot <user_id> <file_name>` - Dừng bot user\n"
        welcome_message += "➕ `/add_subscription <user_id> <days>` - Thêm gói\n"
        welcome_message += "➖ `/remove_subscription <user_id>` - Xóa gói"

    if photo_file_id:
        bot.send_photo(message.chat.id, photo_file_id, caption=welcome_message, reply_markup=create_main_menu(user_id))
    else:
        bot.send_message(message.chat.id, welcome_message, reply_markup=create_main_menu(user_id))

@bot.message_handler(commands=['upload'])
def upload_command(message):
    user_id = message.from_user.id
    if bot_locked:
        bot.send_message(message.chat.id, f"⚠️ Bot hiện đang bị khóa. Vui lòng liên hệ nhà phát triển {YOUR_USERNAME}.")
        return
    if free_mode or (user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now()):
        bot.send_message(message.chat.id, "📄 Vui lòng gửi file mà bạn muốn tải lên.")
    else:
        bot.send_message(message.chat.id, f"⚠️ Bạn cần có gói đăng ký để sử dụng tính năng này. Vui lòng liên hệ nhà phát triển {YOUR_USERNAME}")

@bot.message_handler(commands=['speed'])
def speed_command(message):
    try:
        start_time = time.time()
        response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe')
        latency = time.time() - start_time
        if response.ok:
            bot.send_message(message.chat.id, f"⚡ Tốc độ bot: {latency:.2f} giây.")
        else:
            bot.send_message(message.chat.id, "⚠️ Lỗi khi kiểm tra tốc độ bot.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi khi kiểm tra tốc độ bot: {e}")

@bot.message_handler(commands=['contact'])
def contact_command(message):
    bot.send_message(message.chat.id, f"📞 Liên hệ chủ bot: {YOUR_USERNAME}")

@bot.message_handler(commands=['subscription'])
def subscription_command(message):
    if message.from_user.id == ADMIN_ID:
        help_text = "💳 **QUẢN LÝ GÓI ĐĂNG KÝ:**\n\n"
        help_text += "➕ `/add_subscription <user_id> <days>` - Thêm gói đăng ký\n"
        help_text += "➖ `/remove_subscription <user_id>` - Xóa gói đăng ký\n\n"
        help_text += "**Ví dụ:**\n"
        help_text += "`/add_subscription 123456789 30` - Thêm 30 ngày cho user\n"
        help_text += "`/remove_subscription 123456789` - Xóa gói của user"
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id == ADMIN_ID:
        total_files = sum(len(files) for files in user_files.values())
        total_users = len(user_files)
        active_users_count = len(active_users)
        subscribed_users = len(user_subscriptions)
        
        stats_text = f"📊 **THỐNG KÊ BOT:**\n\n"
        stats_text += f"📂 File đã tải lên: {total_files}\n"
        stats_text += f"👤 Tổng số người dùng: {total_users}\n"
        stats_text += f"👥 Người dùng hoạt động: {active_users_count}\n"
        stats_text += f"💳 Người dùng có gói: {subscribed_users}\n"
        stats_text += f"🔒 Trạng thái bot: {'Khóa' if bot_locked else 'Mở'}\n"
        stats_text += f"🆓 Chế độ miễn phí: {'Bật' if free_mode else 'Tắt'}"
        
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['freemode'])
def freemode_command(message):
    if message.from_user.id == ADMIN_ID:
        global free_mode
        free_mode = not free_mode
        status = "bật" if free_mode else "tắt"
        bot.send_message(message.chat.id, f"🔓 Chế độ miễn phí đã được {status}.")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📢 Nhập tin nhắn cần phát thông báo:")
        bot.register_next_step_handler(message, process_broadcast_command)
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

def process_broadcast_command(message):
    if message.from_user.id == ADMIN_ID:
        broadcast_message = message.text
        success_count = 0
        fail_count = 0

        for user_id in active_users:
            try:
                bot.send_message(user_id, f"📢 **THÔNG BÁO TỪ ADMIN:**\n\n{broadcast_message}")
                success_count += 1
            except Exception as e:
                print(f"❌ Lỗi khi gửi tin nhắn đến người dùng {user_id}: {e}")
                fail_count += 1

        bot.send_message(message.chat.id, f"✅ Đã gửi tin nhắn đến {success_count} người dùng.\n❌ Lỗi khi gửi đến {fail_count} người dùng.")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    help_text = "📋 **DANH SÁCH LỆNH:**\n\n"
    help_text += "📤 `/upload` - Tải file lên\n"
    help_text += "⚡ `/speed` - Kiểm tra tốc độ bot\n"
    help_text += "📞 `/contact` - Liên hệ chủ bot\n"
    help_text += "❓ `/help` - Hiển thị trợ giúp\n"
    help_text += "⏹️ `/stop` - Dừng bot đang chạy\n"
    help_text += "🗑️ `/delete` - Xóa file bot\n"
    help_text += "📊 `/status` - Xem trạng thái\n"
    help_text += "📂 `/myfiles` - Xem file đã tải lên\n"
    
    if user_id == ADMIN_ID:
        help_text += "\n🔧 **LỆNH ADMIN:**\n"
        help_text += "💳 `/subscription` - Hướng dẫn quản lý gói\n"
        help_text += "📊 `/stats` - Xem thống kê tổng thể\n"
        help_text += "🔒 `/lock` - Khóa bot\n"
        help_text += "🔓 `/unlock` - Mở khóa bot\n"
        help_text += "🆓 `/freemode` - Bật/tắt chế độ miễn phí\n"
        help_text += "📢 `/broadcast` - Phát thông báo\n"
        help_text += "👥 `/user_files <user_id>` - Xem file của user\n"
        help_text += "🗑️ `/delete_user_file <user_id> <file_name>` - Xóa file\n"
        help_text += "⏹️ `/stop_user_bot <user_id> <file_name>` - Dừng bot user\n"
        help_text += "➕ `/add_subscription <user_id> <days>` - Thêm gói\n"
        help_text += "➖ `/remove_subscription <user_id>` - Xóa gói"
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    if call.from_user.id == ADMIN_ID:
        bot.send_message(call.message.chat.id, "Gửi tin nhắn mà bạn muốn phát thông báo:")
        bot.register_next_step_handler(call.message, process_broadcast_message)
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

def process_broadcast_message(message):
    if message.from_user.id == ADMIN_ID:
        broadcast_message = message.text
        success_count = 0
        fail_count = 0

        for user_id in active_users:
            try:
                bot.send_message(user_id, broadcast_message)
                success_count += 1
            except Exception as e:
                print(f"❌ Lỗi khi gửi tin nhắn đến người dùng {user_id}: {e}")
                fail_count += 1

        bot.send_message(message.chat.id, f"✅ Đã gửi tin nhắn đến {success_count} người dùng.\n❌ Lỗi khi gửi đến {fail_count} người dùng.")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'speed')
def bot_speed_info(call):
    try:
        start_time = time.time()
        response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe')
        latency = time.time() - start_time
        if response.ok:
            bot.send_message(call.message.chat.id, f"⚡ Tốc độ bot: {latency:.2f} giây.")
        else:
            bot.send_message(call.message.chat.id, "⚠️ Lỗi khi kiểm tra tốc độ bot.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Lỗi khi kiểm tra tốc độ bot: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'upload')
def ask_to_upload_file(call):
    user_id = call.from_user.id
    if bot_locked:
        bot.send_message(call.message.chat.id, f"⚠️ Bot hiện đang bị khóa. Vui lòng liên hệ nhà phát triển {YOUR_USERNAME}.")
        return
    if free_mode or (user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now()):
        bot.send_message(call.message.chat.id, "📄 Vui lòng gửi file mà bạn muốn tải lên.")
    else:
        bot.send_message(call.message.chat.id, f"⚠️ Bạn cần có gói đăng ký để sử dụng tính năng này. Vui lòng liên hệ nhà phát triển {YOUR_USERNAME}")

@bot.callback_query_handler(func=lambda call: call.data == 'subscription')
def subscription_menu(call):
    if call.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        add_subscription_button = types.InlineKeyboardButton('➕ Thêm Gói Đăng Ký', callback_data='add_subscription')
        remove_subscription_button = types.InlineKeyboardButton('➖ Xóa Gói Đăng Ký', callback_data='remove_subscription')
        markup.add(add_subscription_button, remove_subscription_button)
        bot.send_message(call.message.chat.id, "Chọn hành động bạn muốn thực hiện:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'stats')
def stats_menu(call):
    if call.from_user.id == ADMIN_ID:
        total_files = sum(len(files) for files in user_files.values())
        total_users = len(user_files)
        active_users_count = len(active_users)
        bot.send_message(call.message.chat.id, f"📊 Thống kê:\n\n📂 File đã tải lên: {total_files}\n👤 Tổng số người dùng: {total_users}\n👥 Người dùng hoạt động: {active_users_count}")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'add_subscription')
def add_subscription_callback(call):
    if call.from_user.id == ADMIN_ID:
        bot.send_message(call.message.chat.id, "Gửi ID người dùng và số ngày theo định dạng này:\n/add_subscription <user_id> <days>")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'remove_subscription')
def remove_subscription_callback(call):
    if call.from_user.id == ADMIN_ID:
        bot.send_message(call.message.chat.id, "Gửi ID người dùng theo định dạng này:\n/remove_subscription <user_id>")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['add_subscription'])
def add_subscription(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            days = int(message.text.split()[2])
            expiry_date = datetime.now() + timedelta(days=days)
            user_subscriptions[user_id] = {'expiry': expiry_date}
            save_subscription(user_id, expiry_date)
            bot.send_message(message.chat.id, f"✅ Đã thêm gói đăng ký {days} ngày cho người dùng {user_id}.")
            bot.send_message(user_id, f"🎉 Gói đăng ký của bạn đã được kích hoạt trong {days} ngày. Bây giờ bạn có thể sử dụng bot!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi: {e}")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['remove_subscription'])
def remove_subscription(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            if user_id in user_subscriptions:
                del user_subscriptions[user_id]
                remove_subscription_db(user_id)
                bot.send_message(message.chat.id, f"✅ Đã xóa gói đăng ký cho người dùng {user_id}.")
                bot.send_message(user_id, "⚠️ Gói đăng ký của bạn đã bị xóa. Bạn không thể sử dụng bot nữa.")
            else:
                bot.send_message(message.chat.id, f"⚠️ Người dùng {user_id} không có gói đăng ký.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi: {e}")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['user_files'])
def show_user_files(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            if user_id in user_files:
                files_list = "\n".join(user_files[user_id])
                bot.send_message(message.chat.id, f"📂 File được tải lên bởi người dùng {user_id}:\n{files_list}")
            else:
                bot.send_message(message.chat.id, f"⚠️ Người dùng {user_id} chưa tải lên file nào.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi: {e}")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['lock'])
def lock_bot(message):
    if message.from_user.id == ADMIN_ID:
        global bot_locked
        bot_locked = True
        bot.send_message(message.chat.id, "🔒 Bot đã bị khóa.")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['unlock'])
def unlock_bot(message):
    if message.from_user.id == ADMIN_ID:
        global bot_locked
        bot_locked = False
        bot.send_message(message.chat.id, "🔓 Bot đã được mở khóa.")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'lock_bot')
def lock_bot_callback(call):
    if call.from_user.id == ADMIN_ID:
        global bot_locked
        bot_locked = True
        bot.send_message(call.message.chat.id, "🔒 Bot đã bị khóa.")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'unlock_bot')
def unlock_bot_callback(call):
    if call.from_user.id == ADMIN_ID:
        global bot_locked
        bot_locked = False
        bot.send_message(call.message.chat.id, "🔓 Bot đã được mở khóa.")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.callback_query_handler(func=lambda call: call.data == 'free_mode')
def toggle_free_mode(call):
    if call.from_user.id == ADMIN_ID:
        global free_mode
        free_mode = not free_mode
        status = "mở" if free_mode else "đóng"
        bot.send_message(call.message.chat.id, f"🔓 Chế độ miễn phí hiện tại: {status}.")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    if bot_locked:
        bot.reply_to(message, f"⚠️ Bot hiện đang bị khóa. Vui lòng liên hệ nhà phát triển {YOUR_USERNAME}")
        return
    if free_mode or (user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now()):
        try:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_name = message.document.file_name

            if not file_name.endswith('.py') and not file_name.endswith('.zip'):
                bot.reply_to(message, "⚠️ Bot này chỉ chấp nhận file Python (.py) hoặc file nén (.zip).")
                return

            if file_name.endswith('.zip'):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Tạo tên folder an toàn
                    folder_name = re.sub(r'[<>:"/\\|?*]', '_', file_name.split('.')[0])
                    zip_folder_path = os.path.join(temp_dir, folder_name)

                    zip_path = os.path.join(temp_dir, file_name)
                    with open(zip_path, 'wb') as new_file:
                        new_file.write(downloaded_file)
                    
                    # Tạo thư mục trích xuất
                    os.makedirs(zip_folder_path, exist_ok=True)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(zip_folder_path)

                    # Tạo thư mục đích với tên an toàn
                    final_folder_path = os.path.join(uploaded_files_dir, folder_name)
                    os.makedirs(final_folder_path, exist_ok=True)

                    # Copy tất cả file từ thư mục tạm sang thư mục đích
                    for root, dirs, files in os.walk(zip_folder_path):
                        for file in files:
                            src_file = os.path.join(root, file)
                            # Tạo tên file an toàn
                            safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', file)
                            dest_file = os.path.join(final_folder_path, safe_file_name)
                            
                            # Đảm bảo không ghi đè file
                            counter = 1
                            original_dest = dest_file
                            while os.path.exists(dest_file):
                                name, ext = os.path.splitext(original_dest)
                                dest_file = f"{name}_{counter}{ext}"
                                counter += 1
                            
                            shutil.copy2(src_file, dest_file)

                    py_files = [f for f in os.listdir(final_folder_path) if f.endswith('.py')]
                    if py_files:
                        main_script = py_files[0]  
                        script_path = os.path.join(final_folder_path, main_script)
                        
                        # Validate, clean và patch file
                        validate_and_clean_file(script_path)
                        patch_common_issues(script_path)
                        
                        run_script(script_path, message.chat.id, final_folder_path, main_script, message)
                    else:
                        bot.send_message(message.chat.id, f"❌ Không tìm thấy file Python (.py) nào trong file nén.")
                        return

            else:
                # Tạo tên file an toàn
                safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
                script_path = os.path.join(uploaded_files_dir, safe_file_name)
                
                # Đảm bảo thư mục tồn tại
                os.makedirs(uploaded_files_dir, exist_ok=True)
                
                with open(script_path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                
                # Validate, clean và patch file
                validate_and_clean_file(script_path)
                patch_common_issues(script_path)

                run_script(script_path, message.chat.id, uploaded_files_dir, safe_file_name, message)

            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append(file_name)
            save_user_file(user_id, file_name)

        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {e}")
    else:
        bot.reply_to(message, f"⚠️ Bạn cần có gói đăng ký để sử dụng tính năng này. Vui lòng liên hệ nhà phát triển {YOUR_USERNAME}")

def get_python_executable():
    """Tìm đường dẫn Python executable"""
    import sys
    return sys.executable

def patch_common_issues(file_path):
    """Sửa các vấn đề thường gặp trong file Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Thêm encoding declaration nếu chưa có
        if not content.startswith('#') or 'coding' not in content.split('\n')[0]:
            content = '# -*- coding: utf-8 -*-\n' + content
        
        # Thay thế các hàm print có thể gây lỗi
        import re
        
        # Tìm và thay thế các console.print với rich
        if 'console.print' in content or 'console.' in content:
            # Thêm try-catch cho rich console
            rich_patch = '''
import sys
import os
try:
    from rich.console import Console
    console = Console(force_terminal=True, width=80)
except:
    class FakeConsole:
        def print(self, *args, **kwargs):
            try:
                print(*args)
            except:
                pass
    console = FakeConsole()
'''
            
            # Thêm patch vào đầu file sau encoding declaration
            lines = content.split('\n')
            insert_index = 1 if lines[0].startswith('#') else 0
            lines.insert(insert_index, rich_patch)
            content = '\n'.join(lines)
        
        # Chỉ ghi file nếu có thay đổi
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Đã patch các vấn đề thường gặp trong: {file_path}")
            return True
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi patch file: {e}")
        return False

def validate_and_clean_file(file_path):
    """Kiểm tra và làm sạch file Python nếu cần"""
    try:
        # Thử đọc file với các encoding khác nhau
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
                
            except UnicodeDecodeError:
                continue
        
        if content is None:
            # Nếu tất cả encoding đều thất bại, đọc với errors='ignore'
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            used_encoding = 'utf-8 (with errors ignored)'
        
        # Làm sạch nội dung - loại bỏ các ký tự có thể gây lỗi với console
        if content:
            # Thay thế các ký tự Unicode có thể gây vấn đề
            import unicodedata
            
            # Chuẩn hóa Unicode
            content = unicodedata.normalize('NFKD', content)
            
            # Loại bỏ các ký tự điều khiển không cần thiết (trừ \n, \r, \t)
            content = ''.join(char for char in content 
                            if unicodedata.category(char) != 'Cc' 
                            or char in '\n\r\t')
            
            # Ghi lại file với UTF-8
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
                
            print(f"✅ File đã được chuẩn hóa từ {used_encoding} sang UTF-8: {file_path}")
            return True
        else:
            print(f"⚠️ File rỗng hoặc không thể đọc: {file_path}")
            return False
        
    except Exception as e:
        print(f"❌ Lỗi khi validate file: {e}")
        return False

def run_script(script_path, chat_id, folder_path, file_name, original_message):
    try:
        # Đảm bảo đường dẫn tồn tại và hợp lệ
        script_path = os.path.abspath(script_path)
        script_dir = os.path.dirname(script_path)
        
        if not os.path.exists(script_path):
            bot.send_message(chat_id, f"❌ File không tồn tại: {script_path}")
            return
            
        if not os.path.exists(script_dir):
            bot.send_message(chat_id, f"❌ Thư mục không tồn tại: {script_dir}")
            return

        requirements_path = os.path.join(script_dir, 'requirements.txt')
        if os.path.exists(requirements_path):
            bot.send_message(chat_id, "🔄 Đang cài đặt các thư viện cần thiết...")
            python_executable = get_python_executable()
            try:
                subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', requirements_path])
                bot.send_message(chat_id, "✅ Đã cài đặt các thư viện thành công!")
            except subprocess.CalledProcessError as e:
                bot.send_message(chat_id, f"⚠️ Một số thư viện có thể không được cài đặt: {e}")

        bot.send_message(chat_id, f"🚀 Đang chạy bot {file_name}...")
        # Sử dụng đường dẫn Python hiện tại
        python_executable = get_python_executable()
        
        # Lưu thư mục hiện tại
        original_cwd = os.getcwd()
        
        try:
            # Chỉ thay đổi thư mục nếu script_dir khác thư mục hiện tại
            if os.path.abspath(script_dir) != os.path.abspath(original_cwd):
                os.chdir(script_dir)
            
            # Tạo environment variables để xử lý Unicode trên Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONLEGACYWINDOWSSTDIO'] = '1'
            
            # Chạy script với đường dẫn tuyệt đối và environment cải thiện
            process = subprocess.Popen([python_executable, script_path], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     cwd=script_dir,
                                     env=env,
                                     creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
        finally:
            # Luôn khôi phục thư mục gốc
            os.chdir(original_cwd)
        
        bot_scripts[chat_id] = {'process': process, 'folder_path': folder_path, 'script_path': script_path}

        token = extract_token_from_script(script_path)
        user_info = f"@{original_message.from_user.username}" if original_message.from_user.username else str(original_message.from_user.id)
        
        if token:
            try:
                bot_info = requests.get(f'https://api.telegram.org/bot{token}/getMe').json()
                bot_username = bot_info['result']['username']
                caption = f"📤 Người dùng {user_info} đã tải lên file bot mới. Tên bot: @{bot_username}"
            except:
                caption = f"📤 Người dùng {user_info} đã tải lên file bot mới, nhưng không thể lấy tên bot."
        else:
            caption = f"📤 Người dùng {user_info} đã tải lên file bot mới, nhưng không tìm thấy token."

        try:
            with open(script_path, 'rb') as file:
                bot.send_document(ADMIN_ID, file, caption=caption)
        except FileNotFoundError:
            print(f"❌ File không tồn tại khi gửi cho admin: {script_path}")
        except PermissionError:
            print(f"❌ Không có quyền đọc file: {script_path}")
        except Exception as e:
            print(f"❌ Lỗi khi gửi file cho admin: {e}")

        markup = types.InlineKeyboardMarkup()
        stop_button = types.InlineKeyboardButton(f"🔴 Dừng {file_name}", callback_data=f'stop_{chat_id}_{file_name}')
        delete_button = types.InlineKeyboardButton(f"🗑️ Xóa {file_name}", callback_data=f'delete_{chat_id}_{file_name}')
        markup.add(stop_button, delete_button)
        
        # Kiểm tra xem bot có chạy thành công không
        time.sleep(3)  # Tăng thời gian chờ lên 3 giây
        if process.poll() is not None:
            # Process đã dừng, có lỗi
            try:
                stdout, stderr = process.communicate(timeout=5)
                stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
                stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
                
                error_msg = stderr_text if stderr_text else stdout_text
                if not error_msg:
                    error_msg = "Bot đã dừng mà không có thông báo lỗi"
                    
                # Cắt ngắn thông báo lỗi
                if len(error_msg) > 2000:
                    error_msg = error_msg[:2000] + "..."
                    
                bot.send_message(chat_id, f"❌ Bot không thể khởi động:\n```\n{error_msg}\n```", parse_mode='Markdown')
            except subprocess.TimeoutExpired:
                bot.send_message(chat_id, f"❌ Bot không phản hồi trong thời gian chờ")
            except Exception as e:
                bot.send_message(chat_id, f"❌ Lỗi khi đọc output: {e}")
            return
        else:
            bot.send_message(chat_id, f"✅ Bot {file_name} đã được khởi chạy thành công!\n\n🎮 **LỆNH ĐIỀU KHIỂN:**\n⏹️ `/stop` - Dừng bot đang chạy\n🗑️ `/delete` - Xóa file bot\n\n📋 Hoặc sử dụng các nút bên dưới:", reply_markup=markup)

    except FileNotFoundError as e:
        bot.send_message(chat_id, f"❌ Không tìm thấy file Python executable: {e}")
    except PermissionError as e:
        bot.send_message(chat_id, f"❌ Không có quyền chạy file: {e}")
    except OSError as e:
        bot.send_message(chat_id, f"❌ Lỗi hệ thống: {e}")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi khi chạy bot: {e}")
        print(f"❌ Chi tiết lỗi: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

def extract_token_from_script(script_path):
    try:
        # Thử nhiều encoding khác nhau
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        file_content = None
        
        for encoding in encodings:
            try:
                with open(script_path, 'r', encoding=encoding) as script_file:
                    file_content = script_file.read()
                break
            except UnicodeDecodeError:
                continue
        
        if file_content is None:
            # Nếu tất cả encoding đều thất bại, đọc dưới dạng binary và ignore lỗi
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as script_file:
                file_content = script_file.read()
                print(f"[CẢNH BÁO] Sử dụng encoding UTF-8 với ignore errors cho {script_path}")

        # Tìm token với regex
        token_match = re.search(r"['\"]([0-9]{9,10}:[A-Za-z0-9_-]+)['\"]", file_content)
        if token_match:
            return token_match.group(1)
        else:
            print(f"[CẢNH BÁO] Không tìm thấy token trong {script_path}")
            
    except FileNotFoundError:
        print(f"[LỖI] File không tồn tại: {script_path}")
    except PermissionError:
        print(f"[LỖI] Không có quyền đọc file: {script_path}")
    except Exception as e:
        print(f"[LỖI] Lỗi khi trích xuất token từ {script_path}: {e}")
        
    return None

def get_custom_file_to_run(message):
    try:
        chat_id = message.chat.id
        folder_path = bot_scripts[chat_id]['folder_path']
        custom_file_path = os.path.join(folder_path, message.text)

        if os.path.exists(custom_file_path):
            run_script(custom_file_path, chat_id, folder_path, message.text, message)
        else:
            bot.send_message(chat_id, f"❌ File được chỉ định không tồn tại. Vui lòng kiểm tra tên và thử lại.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi: {e}")

@bot.message_handler(commands=['stop'])
def stop_command(message):
    chat_id = message.chat.id
    if chat_id in bot_scripts and 'process' in bot_scripts[chat_id]:
        kill_process_tree(bot_scripts[chat_id]['process'])
        bot.send_message(chat_id, "🔴 Bot của bạn đã được dừng.")
    else:
        bot.send_message(chat_id, "⚠️ Bạn hiện không có bot nào đang chạy.")

@bot.message_handler(commands=['delete'])
def delete_command(message):
    chat_id = message.chat.id
    if chat_id in bot_scripts and 'folder_path' in bot_scripts[chat_id]:
        folder_path = bot_scripts[chat_id]['folder_path']
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            bot.send_message(chat_id, "🗑️ File bot của bạn đã được xóa.")
            # Xóa khỏi danh sách bot_scripts
            del bot_scripts[chat_id]
        else:
            bot.send_message(chat_id, "⚠️ File không tồn tại.")
    else:
        bot.send_message(chat_id, "⚠️ Bạn không có file bot để xóa.")

@bot.message_handler(commands=['status'])
def status_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    status_text = f"📊 **TRẠNG THÁI CỦA BẠN:**\n\n"
    
    # Kiểm tra bot có đang chạy không
    if chat_id in bot_scripts and 'process' in bot_scripts[chat_id]:
        try:
            process = bot_scripts[chat_id]['process']
            if process.poll() is None:  # Process đang chạy
                status_text += "🟢 Bot: Đang chạy\n"
            else:
                status_text += "🔴 Bot: Đã dừng\n"
        except:
            status_text += "🔴 Bot: Không xác định\n"
    else:
        status_text += "⚫ Bot: Chưa có bot nào được tải lên\n"
    
    # Kiểm tra gói đăng ký
    if user_id in user_subscriptions:
        expiry = user_subscriptions[user_id]['expiry']
        if expiry > datetime.now():
            remaining_days = (expiry - datetime.now()).days
            status_text += f"💳 Gói đăng ký: Còn {remaining_days} ngày\n"
        else:
            status_text += "💳 Gói đăng ký: Đã hết hạn\n"
    elif free_mode:
        status_text += "🆓 Chế độ: Miễn phí (đang bật)\n"
    else:
        status_text += "⚠️ Gói đăng ký: Chưa có\n"
    
    # Kiểm tra số file đã tải lên
    if user_id in user_files:
        file_count = len(user_files[user_id])
        status_text += f"📂 Số file đã tải: {file_count}\n"
    else:
        status_text += "📂 Số file đã tải: 0\n"
    
    bot.send_message(chat_id, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['myfiles'])
def myfiles_command(message):
    user_id = message.from_user.id
    
    if user_id in user_files and user_files[user_id]:
        files_text = "📂 **FILE CỦA BẠN:**\n\n"
        for i, file_name in enumerate(user_files[user_id], 1):
            files_text += f"{i}. {file_name}\n"
        files_text += f"\n📊 Tổng cộng: {len(user_files[user_id])} file"
    else:
        files_text = "📂 Bạn chưa tải lên file nào."
    
    bot.send_message(message.chat.id, files_text, parse_mode='Markdown')
    if call.data.startswith('stop_'):
        chat_id = int(call.data.split('_')[1])
        stop_running_bot(chat_id)
    elif call.data.startswith('delete_'):
        chat_id = int(call.data.split('_')[1])
        delete_uploaded_file(chat_id)

def stop_running_bot(chat_id):
    if chat_id in bot_scripts and 'process' in bot_scripts[chat_id]:
        kill_process_tree(bot_scripts[chat_id]['process'])
        bot.send_message(chat_id, "🔴 Bot đã dừng.")
    else:
        bot.send_message(chat_id, "⚠️ Hiện tại không có bot nào đang chạy.")

def delete_uploaded_file(chat_id):
    if chat_id in bot_scripts and 'folder_path' in bot_scripts[chat_id]:
        folder_path = bot_scripts[chat_id]['folder_path']
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            bot.send_message(chat_id, f"🗑️ File bot đã được xóa.")
        else:
            bot.send_message(chat_id, "⚠️ File không tồn tại.")
    else:
        bot.send_message(chat_id, "⚠️ Không có file bot để xóa.")

def kill_process_tree(process):
    try:
        parent = psutil.Process(process.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except Exception as e:
        print(f"❌ Lỗi khi tắt tiến trình: {e}")

@bot.message_handler(commands=['delete_user_file'])
def delete_user_file(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            file_name = message.text.split()[2]
            
            if user_id in user_files and file_name in user_files[user_id]:
                file_path = os.path.join(uploaded_files_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    user_files[user_id].remove(file_name)
                    remove_user_file_db(user_id, file_name)
                    bot.send_message(message.chat.id, f"✅ Đã xóa file {file_name} của người dùng {user_id}.")
                else:
                    bot.send_message(message.chat.id, f"⚠️ File {file_name} không tồn tại.")
            else:
                bot.send_message(message.chat.id, f"⚠️ Người dùng {user_id} chưa tải lên file {file_name}.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi: {e}")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

@bot.message_handler(commands=['stop_user_bot'])
def stop_user_bot(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            file_name = message.text.split()[2]
            
            if user_id in user_files and file_name in user_files[user_id]:
                for chat_id, script_info in bot_scripts.items():
                    if script_info.get('folder_path', '').endswith(file_name.split('.')[0]):
                        kill_process_tree(script_info['process'])
                        bot.send_message(chat_id, f"🔴 Đã dừng bot {file_name}.")
                        bot.send_message(message.chat.id, f"✅ Đã dừng bot {file_name} của người dùng {user_id}.")
                        break
                else:
                    bot.send_message(message.chat.id, f"⚠️ Bot {file_name} hiện không chạy.")
            else:
                bot.send_message(message.chat.id, f"⚠️ Người dùng {user_id} chưa tải lên file {file_name}.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi: {e}")
    else:
        bot.send_message(message.chat.id, "⚠️ Bạn không phải là nhà phát triển.")

if __name__ == "__main__":
    try:
        print("🔧 Đang khởi tạo database...")
        init_db()
        print("📊 Đang tải dữ liệu...")
        load_data()
        print("✅ Bot sẵn sàng! Đang bắt đầu polling...")
        logger.info("Starting infinity polling...")
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("⏹️ Bot dừng bởi người dùng")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {e}")
        logger.error(f"Critical error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        raise