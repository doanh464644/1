# -*- coding: utf-8 -*-
import telebot
import threading
import time
import requests
import json

# Token bot
TOKEN = "8229062858:AAGeAmWU_hJHYSBdNeIzgreXh29MLt-ijXg"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Biến global từ file gốc
users = {}
running = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """
🎮 <b>TELEGRAM BOT - LOGIC GỐC 100%</b>

📝 <b>SETUP:</b>
/setup - Thiết lập tool (giống file gốc)
/run - Chạy tool với logic gốc
/stop - Dừng tool

✨ Bắt đầu với /setup
""")

@bot.message_handler(commands=['setup'])  
def setup(message):
    users[message.from_user.id] = {'step': 'uid'}
    bot.send_message(message.chat.id, "📝 Gửi <b>UID</b>:")

@bot.message_handler(commands=['run'])
def run_tool(message):
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ Chưa setup! Dùng /setup")
        return
    
    if user_id in running and running[user_id]:
        bot.send_message(message.chat.id, "⚠️ Tool đang chạy!")
        return
    
    bot.send_message(message.chat.id, "🚀 <b>KHỞI ĐỘNG TOOL...</b>")
    
    thread = threading.Thread(target=original_game_logic, args=(message.chat.id, user_id))
    thread.daemon = True
    thread.start()

@bot.message_handler(commands=['stop'])
def stop_tool(message):
    user_id = message.from_user.id
    if user_id in running:
        running[user_id] = False
        bot.send_message(message.chat.id, "⏹️ <b>ĐANG DỪNG...</b>")

@bot.message_handler(func=lambda message: True)
def handle_setup(message):
    user_id = message.from_user.id
    if user_id not in users:
        return
    
    user = users[user_id]
    step = user.get('step')
    
    if step == 'uid':
        user['user_id'] = message.text.strip()
        user['step'] = 'user_login'
        bot.send_message(message.chat.id, "✅ UID OK!\n📝 Gửi <b>user_login</b> (mặc định: login_v2):")
        
    elif step == 'user_login':
        user['user_login'] = message.text.strip() or "login_v2"
        user['step'] = 'user_secret_key'
        bot.send_message(message.chat.id, "✅ User login OK!\n📝 Gửi <b>secret key</b>:")
        
    elif step == 'user_secret_key':
        user['user_secret_key'] = message.text.strip()
        user['step'] = 'amount'
        bot.send_message(message.chat.id, "✅ Secret key OK!\n📝 Gửi <b>số tiền cược ban đầu</b>:")
        
    elif step == 'amount':
        try:
            amount = int(message.text.strip())
            if amount < 1:
                bot.send_message(message.chat.id, "❌ Phải ≥ 1 BUILD!")
                return
            
            user['amount'] = amount
            user['cuoc_ban_dau'] = amount
            
            # Thiết lập mặc định như file gốc
            user['stop_loss_enabled'] = False
            user['stop_loss_amount'] = 0
            user['take_profit_amount'] = 0
            user['multiplier_1'] = 15
            user['multiplier_2'] = 20
            user['multiplier_3'] = 15
            user['step'] = None
            
            info = f"""
✅ <b>SETUP HOÀN TẤT - LOGIC GỐC!</b>

👤 <b>UID:</b> {user['user_id']}
🔑 <b>User Login:</b> {user['user_login']}
💰 <b>Cược ban đầu:</b> {amount:,} BUILD
⚡ <b>Hệ số gấp:</b> x{user['multiplier_1']} | x{user['multiplier_2']} | x{user['multiplier_3']}

🎮 Dùng /run để chạy!
"""
            bot.send_message(message.chat.id, info)
        except:
            bot.send_message(message.chat.id, "❌ Nhập số hợp lệ!")

def original_game_logic(chat_id, user_id):
    """Logic game từ file gốc 10.wxx.py"""
    try:
        running[user_id] = True
        user = users[user_id]
        
        # Biến global từ file gốc
        current_time = int(time.time() * 1000)
        amount = user['amount']
        cuoc_ban_dau = user['cuoc_ban_dau']
        stop_loss_enabled = user['stop_loss_enabled']
        stop_loss_amount = user['stop_loss_amount']
        take_profit_amount = user['take_profit_amount']
        multiplier_1 = user['multiplier_1']
        multiplier_2 = user['multiplier_2']
        multiplier_3 = user['multiplier_3']
        so_du_ban_dau = 0
        tool_running = True
        vong_choi = None
        chuoi_thang = 0
        count_thang = 0
        number_cuoc = 0
        
        # URLs như file gốc
        url = f"https://user.3games.io/user/regist?is_cwallet=1&is_mission_setting=true&version=&time={current_time}"
        api_10_van = f"https://api.escapemaster.net/escape_game/recent_10_issues?asset=BUILD"
        api_cuoc = "https://api.escapemaster.net/escape_game/bet"
        
        headers = {
            "user-id": user['user_id'],
            "user-login": user['user_login'],
            "user-secret-key": user['user_secret_key']
        }
        
        # Hàm Login từ file gốc
        def Login():
            nonlocal so_du_ban_dau
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        username = data["data"]["username"]
                        ctoken_contribute = data["data"]["cwallet"]["ctoken_contribute"]
                        token_contribute_rounded = round(ctoken_contribute)
                        
                        login_msg = f"""
✅ <b>ĐĂNG NHẬP THÀNH CÔNG!</b>

👤 <b>Username:</b> {username}
💰 <b>Số dư:</b> {token_contribute_rounded:,} BUILD

🚀 <b>BẮT ĐẦU TOOL...</b>
"""
                        bot.send_message(chat_id, login_msg)
                        so_du_ban_dau = token_contribute_rounded
                        return True
                    else:
                        bot.send_message(chat_id, "❌ <b>ĐĂNG NHẬP THẤT BẠI!</b>")
                        return False
                else:
                    bot.send_message(chat_id, f"❌ <b>LỖI MẠNG:</b> {response.status_code}")
                    return False
            except Exception as e:
                bot.send_message(chat_id, f"❌ <b>LỖI LOGIN:</b> {str(e)}")
                return False
        
        # Hàm tong_loi_lo từ file gốc
        def tong_loi_lo():
            nonlocal tool_running
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        ctoken_contribute = data["data"]["cwallet"]["ctoken_contribute"]
                        token_contribute_rounded = round(ctoken_contribute)
                        loi_lo = token_contribute_rounded - so_du_ban_dau

                        # Kiểm tra Stop Loss/Take Profit
                        if stop_loss_enabled:
                            if loi_lo <= -stop_loss_amount:
                                bot.send_message(chat_id, f"🛑 <b>ĐÃ ĐẠT STOP LOSS: {loi_lo} BUILD</b>\n🛑 DỪNG TOOL TỰ ĐỘNG!")
                                tool_running = False
                                return
                            elif loi_lo >= take_profit_amount:
                                bot.send_message(chat_id, f"🎯 <b>ĐÃ ĐẠT TAKE PROFIT: {loi_lo} BUILD</b>\n🎯 DỪNG TOOL TỰ ĐỘNG!")
                                tool_running = False
                                return

                        if loi_lo >= 0:
                            bot.send_message(chat_id, f"💚 <b>Số dư:</b> {token_contribute_rounded:,} BUILD\n💰 <b>Đang lời:</b> +{loi_lo:,} BUILD")
                        else:
                            bot.send_message(chat_id, f"💔 <b>Số dư:</b> {token_contribute_rounded:,} BUILD\n💸 <b>Đang lỗ:</b> {loi_lo:,} BUILD")
            except Exception as e:
                bot.send_message(chat_id, f"❌ <b>Lỗi kiểm tra lợi nhuận:</b> {str(e)}")
        
        # Hàm lich_su từ file gốc
        def lich_su():
            nonlocal vong_choi
            try:
                response = requests.get(api_10_van, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # QUAN TRỌNG: API này trả code = 0, không phải 200!
                    if data.get("code") == 0:
                        room_mapping = {
                            1: "Nhà Kho",
                            2: "Phòng Họp", 
                            3: "Phòng Giám Đốc",
                            4: "Phòng Trò Chuyện",
                            5: "Phòng Giám Sát",
                            6: "Văn Phòng",
                            7: "Phòng Tài Vụ",
                            8: "Phòng Nhân Sự"
                        }
                        issues = data.get("data", [])[:3]
                        vong_choi_truoc = issues[0]["issue_id"]
                        id_ket_qua_vong_truoc = issues[0]["killed_room_id"]
                        ten_phong_vong_truoc = room_mapping.get(id_ket_qua_vong_truoc, "Không xác định")
                        vong_choi_hien_tai = issues[0]["issue_id"] + 1
                        issue_details = []
                        for issue in issues:
                            issue_id = issue["issue_id"]
                            killed_room_id = issue["killed_room_id"]
                            room_name = room_mapping.get(killed_room_id, "Không xác định")
                            issue_details.append(f"Issue ID: {issue_id}, Room: {room_name}")

                        if vong_choi_truoc != vong_choi:
                            vong_msg = f"""
🎮 <b>VÒNG #{vong_choi_hien_tai}</b>

📊 <b>Kết quả vòng #{vong_choi_truoc}:</b> {ten_phong_vong_truoc}

📋 <b>3 kết quả gần nhất:</b>
🥇 {room_mapping.get(issues[0]['killed_room_id'])}
🥈 {room_mapping.get(issues[1]['killed_room_id'])}
🥉 {room_mapping.get(issues[2]['killed_room_id'])}

⏰ {time.strftime('%H:%M:%S')}
"""
                            bot.send_message(chat_id, vong_msg)
                            vong_choi = vong_choi_truoc
                            kiem_tra_dieu_kien(issue_details)
                    else:
                        bot.send_message(chat_id, f"❌ <b>API History Error:</b> Code {data.get('code')} - {data.get('message', 'Unknown')}")
                else:
                    bot.send_message(chat_id, f"❌ <b>HTTP Error:</b> {response.status_code}")
            except Exception as e:
                bot.send_message(chat_id, f"❌ <b>Lỗi lịch sử:</b> {str(e)}")
        
        # Hàm kiem_tra_dieu_kien từ file gốc (LOGIC CHÍNH)
        def kiem_tra_dieu_kien(issue_details):
            nonlocal number_cuoc, amount, cuoc_ban_dau, chuoi_thang, count_thang, tool_running
            room_mapping = {
                "Nhà Kho": 1,
                "Phòng Họp": 2,
                "Phòng Giám Đốc": 3,
                "Phòng Trò Chuyện": 4,
                "Phòng Giám Sát": 5,
                "Văn Phòng": 6,
                "Phòng Tài Vụ": 7,
                "Phòng Nhân Sự": 8
            }
            room_0 = issue_details[0].split(",")[1].split(":")[1].strip()
            room_1 = issue_details[1].split(",")[1].split(":")[1].strip()
            room_2 = issue_details[2].split(",")[1].split(":")[1].strip()
            
            if room_0 != room_1 and number_cuoc == 0:
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 1
                return
            elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 1:
                bot.send_message(chat_id, "🎉 <b>Trốn sát thủ thành công!</b>")
                tong_loi_lo()
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 1
                chuoi_thang += 1
                bot.send_message(chat_id, f"🔥 <b>Chuỗi thắng liên tiếp: {chuoi_thang} ván</b>")
                return
            elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 1:
                bot.send_message(chat_id, "💔 <b>Trốn sát thủ thất bại!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = int(amount * multiplier_1)
                bot.send_message(chat_id, f"💰 <b>Gấp cược x{multiplier_1}: {amount:,} BUILD</b>")
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 2
                chuoi_thang = 0
                return
            # Tiếp tục logic cho number_cuoc = 2, 3, 4...
            elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 2:
                bot.send_message(chat_id, "🎉 <b>Trốn sát thủ thành công!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = cuoc_ban_dau
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 1
                chuoi_thang += 1
                bot.send_message(chat_id, f"🔥 <b>Chuỗi thắng liên tiếp: {chuoi_thang} ván</b>")
                return
            elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 2:
                bot.send_message(chat_id, "💔 <b>Trốn sát thủ thất bại!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = int(amount * multiplier_2)
                bot.send_message(chat_id, f"💰 <b>Gấp cược x{multiplier_2}: {amount:,} BUILD</b>")
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 3
                chuoi_thang = 0
                return
            elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 3:
                bot.send_message(chat_id, "🎉 <b>Trốn sát thủ thành công!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = cuoc_ban_dau
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 1
                chuoi_thang += 1
                bot.send_message(chat_id, f"🔥 <b>Chuỗi thắng liên tiếp: {chuoi_thang} ván</b>")
                return
            elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 3:
                bot.send_message(chat_id, "💔 <b>Trốn sát thủ thất bại!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = int(amount * multiplier_3)
                bot.send_message(chat_id, f"💰 <b>Gấp cược x{multiplier_3}: {amount:,} BUILD</b>")
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 4
                chuoi_thang = 0
                return
            elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 4:
                bot.send_message(chat_id, "🎉 <b>Trốn sát thủ thành công!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = cuoc_ban_dau
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 1
                chuoi_thang += 1
                bot.send_message(chat_id, f"🔥 <b>Chuỗi thắng liên tiếp: {chuoi_thang} ván</b>")
                return
            elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 4:
                bot.send_message(chat_id, "⚠️ <b>Đã đạt gấp cược tối đa!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                amount = cuoc_ban_dau
                room_name = issue_details[1].split(",")[1].split(":")[1].strip()
                room_id = room_mapping.get(room_name, None)
                dat_cuoc(room_id)
                number_cuoc = 1
                chuoi_thang = 0
                return
            elif room_0 == room_1:
                bot.send_message(chat_id, "🔴 <b>Phát hiện sát thủ vào 1 phòng liên tục!</b>")
                tong_loi_lo()
                if not tool_running:
                    return
                bot.send_message(chat_id, f"🔥 <b>Chuỗi thắng liên tiếp hiện tại: {chuoi_thang} ván</b>")
        
        # Hàm dat_cuoc từ file gốc
        def dat_cuoc(room_id):
            room_names = {
                1: "Nhà Kho", 2: "Phòng Họp", 3: "Phòng Giám Đốc", 4: "Phòng Trò Chuyện",
                5: "Phòng Giám Sát", 6: "Văn Phòng", 7: "Phòng Tài Vụ", 8: "Phòng Nhân Sự"
            }
            
            body = {
                "asset_type": "BUILD",
                "bet_amount": amount,
                "room_id": room_id,
                "user_id": headers["user-id"]
            }
            try:
                response = requests.post(api_cuoc, headers=headers, json=body)
                if response.status_code == 200:
                    room_name = room_names.get(room_id, "Unknown")
                    bot.send_message(chat_id, f"""
🎯 <b>CƯỢC THÀNH CÔNG!</b>

💰 <b>Số tiền:</b> {amount:,} BUILD
🏠 <b>Phòng:</b> {room_name}
📊 <b>Lần cược:</b> {number_cuoc}
⏰ <b>Thời gian:</b> {time.strftime('%H:%M:%S')}
""")
                else:
                    bot.send_message(chat_id, f"❌ <b>Lỗi cược:</b> {response.status_code}")
            except Exception as e:
                bot.send_message(chat_id, f"❌ <b>Lỗi cược:</b> {str(e)}")
        
        # Bắt đầu chạy như file gốc
        if not Login():
            return
        
        # Main loop như file gốc
        try:
            while tool_running and running.get(user_id, False):
                lich_su()
                if not tool_running:
                    bot.send_message(chat_id, "🛑 <b>Tool đã dừng do đạt điều kiện Stop Loss/Take Profit!</b>")
                    break
                time.sleep(15)
        except Exception as e:
            bot.send_message(chat_id, f"❌ <b>Lỗi main loop:</b> {str(e)}")
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ <b>LỖI NGHIÊM TRỌNG:</b> {str(e)}")
    finally:
        running[user_id] = False
        bot.send_message(chat_id, "🛑 <b>TOOL ĐÃ DỪNG!</b>")

if __name__ == "__main__":
    print("🤖 Telegram Bot với logic gốc 100%...")
    print("✅ Bot ready!")
    bot.infinity_polling()
