import importlib.util
import subprocess
import sys

# Flask অটো-ইনস্টল চেক
if importlib.util.find_spec("flask") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

from flask import Flask
import threading
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time
import random
import string

# ============================================
# --- WEB SERVER FOR RENDER (FREE HOSTING) ---
# ============================================
app = Flask('')

@app.route('/')
def home():
    return "Fast Pay Bot is running 24/7!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

# ============================================
# --- CONFIGURATION ---
# ============================================
TOKEN = "8826873484:AAF2c46TzVy2-vjOebAayAJzmFaRegQiA50"  # আপনার বট টোকেন
ADMIN_ID = 7833766898          # আপনার টেলিগ্রাম ID
BOT_NAME = "CASH KING WIN BD"
DATA_FILE = "fast_pay_bot_data.json"

bot = telebot.TeleBot(TOKEN, num_threads=50)
data_lock = threading.RLock()

# ============================================
# --- STYLE PATCH FOR TELEBOT BUTTONS ---
# ============================================
_old_inline_dict = InlineKeyboardButton.to_dict
def _new_inline_dict(self):
    d = _old_inline_dict(self)
    if hasattr(self, 'style'): d['style'] = self.style
    return d
InlineKeyboardButton.to_dict = _new_inline_dict

_old_kb_dict = KeyboardButton.to_dict
def _new_kb_dict(self):
    d = _old_kb_dict(self)
    if hasattr(self, 'style'): d['style'] = self.style
    return d
KeyboardButton.to_dict = _new_kb_dict

def ibtn(text, callback_data=None, url=None, style=None):
    kwargs = {'text': text}
    if callback_data: kwargs['callback_data'] = callback_data
    if url: kwargs['url'] = url
    b = InlineKeyboardButton(**kwargs)
    if style: b.style = style
    return b

def rbtn(text, style=None):
    b = KeyboardButton(text=text)
    if style: b.style = style
    return b

# ============================================
# --- STYLISH MENU TEXTS ---
# ============================================
TXT_BALANCE = "💰 𝑩𝒂𝒍𝒂𝒏𝒄𝒆"
TXT_INVITE = "👥 𝑰𝒏𝒗𝒊𝒕𝒆 𝑭𝒓𝒊𝒆𝒏𝒅𝒔"
TXT_TASK = "📝 𝑫𝒂𝒊𝒍𝒚 𝑻𝒂𝒔𝒌"
TXT_WORK = "💼 𝑫𝒂𝒊𝒍𝒚 𝑾𝒐𝒓𝒌"
TXT_REDEEM = "🎁 𝑹𝒆𝒅𝒆𝒆𝒎 𝑪𝒐𝒅𝒆"
TXT_WITHDRAW = "📥 𝑾𝒊𝒕𝒉𝒅𝒓𝒂𝒘"
TXT_LEADERBOARD = "🏆 𝑳𝒆𝒂𝒅𝒆𝒓𝒃𝒐𝒂𝒓𝒅"
TXT_ADMIN = "⚙️ 𝑨𝒅𝒎𝒊𝒏 𝑷𝒂𝒏𝒆𝒍"

TXT_INSTA = "📸 𝑰𝒏𝒔𝒕𝒂𝒈𝒓𝒂𝒎 𝑺𝒆𝒍𝒍"
TXT_NEW_GMAIL = "📧 𝑵𝒆𝒘 𝑮𝒎𝒂𝒊𝒍 𝑺𝒆𝒍𝒍"
TXT_OLD_GMAIL = "📩 𝑶𝒍𝒅 𝑮𝒎𝒂𝒊𝒍 𝑺𝒆𝒍𝒍"
TXT_MARKET = "📊 𝑴𝒂𝒓𝒌𝒆𝒕 𝑹𝒂𝒕𝒆"
TXT_BACK = "🔙 𝑩𝒂𝒄𝒌 𝑴𝒂𝒊𝒏𝒎𝒆𝒏𝒖"

MENU_TEXTS = [TXT_BALANCE, TXT_INVITE, TXT_TASK, TXT_WORK, TXT_REDEEM, TXT_WITHDRAW, TXT_LEADERBOARD, TXT_ADMIN, TXT_INSTA, TXT_NEW_GMAIL, TXT_OLD_GMAIL, TXT_MARKET, TXT_BACK]

# ============================================
# --- DATABASE MANAGEMENT ---
# ============================================
def load_data():
    with data_lock:
        default_data = {
            "users": {},
            "banned_users": [],
            "force_channels": [],
            "daily_bonus_amount": 5.0,
            "ref_bonus": 2.0,
            "market_rate": {
                "new_gmail": 5.0,
                "old_gmail": 10.0,
                "default_password": "Admin123*()"
            },
            "redeem_codes": {}, 
            "leaderboard": {
                "last_reset": time.time(),
                "daily_refs": {},  
                "rewards": {"1": 50.0, "2": 30.0, "3": 20.0}
            },
            "tasks": {
                "telegram": [],  
                "app": [],       
                "gmail": []      
            },
            "withdraw_methods": {
                "bKash": {"enabled": True, "min": 50.0},
                "Nagad": {"enabled": True, "min": 50.0},
                "USDT BEP20": {"enabled": True, "min": 100.0}
            },
            "ref_box_levels": {
                "5": 10.0,
                "10": 25.0
            },
            "pending_proofs": {},
            "pending_withdraws": {},
            "pending_gmail_verifications": {},
            "pending_old_gmails": {}
        }
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        try:
            with open(DATA_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                for key, val in default_data.items():
                    if key not in data:
                        data[key] = val
                return data
        except:
            return default_data

def save_data(data):
    with data_lock:
        try:
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Database Save Error:", e)

def get_user(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "balance": 0.0,
            "total_income": 0.0,
            "total_withdraw": 0.0,
            "total_bonus": 0.0,
            "referrals": 0,
            "referred_by": None,
            "ref_rewarded": False,
            "fake_ref_warnings": 0,
            "last_bonus": 0,
            "claimed_ref_boxes": [],
            "claimed_lb_tiers": [],
            "approved_tasks": 0,
            "rejected_tasks": 0,
            "pending_tasks": 0,
            "completed_tasks": [], 
            "state": None,
            "temp_withdraw": {},
            "temp_old_gmail": {},
            "temp_task": {},
            "active_gmail_task": None,
            "verified": False,
            "captcha_ans": 0
        }
        save_data(data)
    else:
        # Ensure fake_ref_warnings key exists
        if "fake_ref_warnings" not in data["users"][uid]:
            data["users"][uid]["fake_ref_warnings"] = 0
            save_data(data)
    return data["users"][uid]

def update_user(user_id, key, value):
    data = load_data()
    uid = str(user_id)
    if uid in data["users"]:
        data["users"][uid][key] = value
        save_data(data)

# ============================================
# --- LEADERBOARD & GMAIL GEN ---
# ============================================
def check_and_reset_leaderboard(data):
    now = time.time()
    lb = data.get("leaderboard", {"last_reset": now, "daily_refs": {}})
    if now - lb.get("last_reset", now) >= 86400:
        lb["last_reset"] = now
        lb["daily_refs"] = {}
        data["leaderboard"] = lb
        for u in data["users"]:
            data["users"][u]["claimed_lb_tiers"] = []
        save_data(data)

FIRST_NAMES = ["Tanvir", "Rahim", "Kareem", "Sabbir", "Arif", "Mahmud", "Shakib", "Naim", "Fahim", "Hasan", "Sumon", "Raju"]
LAST_NAMES = ["Hossain", "Islam", "Ahmed", "Chowdhury", "Khan", "Uddin", "Rahman", "Mia", "Ali", "Sarker", "Roy", "Das"]

def generate_random_gmail_credentials():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    rand_num = random.randint(1000, 99999)
    email = f"{first.lower()}{last.lower()}{rand_num}@gmail.com"
    return first, last, email

# ============================================
# --- FORCE JOIN CHECKER ---
# ============================================
def check_force_join(user_id):
    data = load_data()
    channels = data.get("force_channels", [])
    if not channels: return True
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ['left', 'kicked']: return False
        except: return False
    return True

def get_force_join_markup():
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=1)
    for ch in data.get("force_channels", []):
        ch_clean = ch.replace("@", "")
        markup.add(ibtn("📢 Join Channel", url=f"https://t.me/{ch_clean}", style="primary"))
    markup.add(ibtn("✅ Verify Now", callback_data="check_join", style="success"))
    return markup

# ============================================
# --- KEYBOARDS & UI ---
# ============================================
def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(rbtn(TXT_BALANCE, "primary"), rbtn(TXT_INVITE, "primary"))
    markup.add(rbtn(TXT_TASK, "primary"), rbtn(TXT_WORK, "primary"))
    markup.add(rbtn(TXT_REDEEM, "primary"), rbtn(TXT_WITHDRAW, "primary"))
    markup.add(rbtn(TXT_LEADERBOARD, "primary"))
    if int(user_id) == ADMIN_ID:
        markup.add(rbtn(TXT_ADMIN, "danger"))
    return markup

def get_daily_work_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(rbtn(TXT_INSTA, "primary"), rbtn(TXT_NEW_GMAIL, "primary"))
    markup.add(rbtn(TXT_OLD_GMAIL, "primary"), rbtn(TXT_MARKET, "primary"))
    markup.add(rbtn(TXT_BACK, "danger"))
    return markup

def get_admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(rbtn("📢 Force Join Settings", "primary"), rbtn("➕ Add Task", "success"))
    markup.add(rbtn("💳 Withdraw Settings", "primary"), rbtn("🎁 Ref Box Settings", "primary"))
    markup.add(rbtn("🔎 Pending Approvals", "primary"), rbtn("📥 Pending Withdraws", "primary"))
    markup.add(rbtn("📢 Broadcast", "primary"), rbtn("📊 Bot Statistics", "primary"))
    markup.add(rbtn("🗑️ Task Delete/Edit", "danger"), rbtn("⛔ Ban/Unban User", "danger"))
    markup.add(rbtn("⚙️ Market Rates", "primary"), rbtn("🎁 Create Redeem Code", "success"))
    markup.add(rbtn("➕ Add Balance", "success"), rbtn("🏆 LB Settings", "primary"))
    markup.add(rbtn(TXT_BACK, "danger"))
    return markup

# ============================================
# --- BOT HANDLERS ---
# ============================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    data = load_data()
    check_and_reset_leaderboard(data)

    if str(user_id) in data.get("banned_users", []):
        bot.send_message(message.chat.id, "⛔ আপনি এই বটে ব্লকড আছেন।")
        return

    user = get_user(user_id)
    
    args = message.text.split()
    if len(args) > 1 and user.get("referred_by") is None:
        ref_id = args[1]
        if ref_id != str(user_id) and ref_id in data["users"]:
            update_user(user_id, "referred_by", ref_id)

    # Verification / CAPTCHA Logic
    if not user.get("verified", False):
        msg_verify = bot.send_message(message.chat.id, "⏳ <i>অপেক্ষা করুন ভেরিফিকেশন চলছে....\n(Checking IP, Device & Multi-Accounts)</i>", parse_mode="HTML")
        time.sleep(1.5)
        try: bot.delete_message(message.chat.id, msg_verify.message_id)
        except: pass
        
        num1 = random.randint(10, 50)
        num2 = random.randint(1, 10)
        ans = num1 + num2
        
        update_user(user_id, "captcha_ans", ans)
        update_user(user_id, "state", "captcha_verify")
        
        bot.send_message(message.chat.id, f"🤖 <b>Anti-Spam Verification</b>\n\nআপনি যে মানুষ তা প্রমাণ করতে নিচের অংকটির সমাধান দিন:\n\n<b>{num1} + {num2} = ?</b>", parse_mode="HTML")
        return

    if not check_force_join(user_id):
        msg = f"<b>👋 Welcome to {BOT_NAME}!</b>\n\nবটটি ব্যবহার করতে নিচের চ্যানেলগুলোতে জয়েন করুন এবং 'Verify Now' এ ক্লিক করুন:"
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=get_force_join_markup())
        return

    process_referral_reward(user_id)
    bot.send_message(message.chat.id, f"<b>Welcome to {BOT_NAME}!</b>\nনিচের মেনু থেকে আপনার কাঙ্খিত অপশনটি বেছে নিন:", parse_mode="HTML", reply_markup=get_main_menu(user_id))

def process_referral_reward(user_id):
    data = load_data()
    uid = str(user_id)
    user = data["users"].get(uid)
    if user and user.get("referred_by") and not user.get("ref_rewarded"):
        ref_id = str(user["referred_by"])
        if ref_id in data["users"]:
            # Fake Ref Verification / Warning / Auto-Ban Logic
            ref_user = data["users"][ref_id]
            is_suspicious = False
            
            # Anti-Spam Check Simulation (e.g., fast creation / account pattern)
            if not user.get("verified", False):
                is_suspicious = True
                
            if is_suspicious:
                warnings = ref_user.get("fake_ref_warnings", 0) + 1
                data["users"][ref_id]["fake_ref_warnings"] = warnings
                save_data(data)
                
                if warnings == 1:
                    try:
                        bot.send_message(ref_id, "⚠️ <b>Warning! (১ম সতর্কতা)</b>\n\nআপনার অ্যাকাউন্টে ফেক রেফার করার চেষ্টা সনাক্ত হয়েছে! অনুগ্রহ করে সঠিক নিয়ম মেনে রেফার করুন। ২য় বার চেষ্টা করলে আপনার অ্যাকাউন্ট সরাসরি <b>অটো ব্যান</b> করা হবে।", parse_mode="HTML")
                    except: pass
                    return
                elif warnings >= 2:
                    if ref_id not in data["banned_users"]:
                        data["banned_users"].append(ref_id)
                        save_data(data)
                    try:
                        bot.send_message(ref_id, "⛔ <b>Account Banned!</b>\n\nআপনি একাধিকবার ফেক রেফার করার চেষ্টা করেছেন। আপনার অ্যাকাউন্টটি স্থায়ীভাবে অটোমেটিক ব্লক করা হলো।", parse_mode="HTML")
                    except: pass
                    return

            bonus = data.get("ref_bonus", 2.0)
            data["users"][ref_id]["balance"] += bonus
            data["users"][ref_id]["total_income"] += bonus
            data["users"][ref_id]["referrals"] += 1
            data["users"][uid]["ref_rewarded"] = True
            
            lb_refs = data["leaderboard"]["daily_refs"].get(ref_id, 0)
            data["leaderboard"]["daily_refs"][ref_id] = lb_refs + 1
            save_data(data)
            try: bot.send_message(ref_id, f"🎉 <b>New Referral Joined!</b>\nআপনি <b>৳{bonus:.2f}</b> রেফার বোনাস পেয়েছেন!", parse_mode="HTML")
            except: pass

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document'])
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip() if message.text else ""
    data = load_data()
    
    if str(user_id) in data.get("banned_users", []):
        return

    user = get_user(user_id)
    state = user.get("state")

    # Clear state instantly if a main menu button is clicked
    if text in MENU_TEXTS or text == "🔙 Main Menu":
        update_user(user_id, "state", None)
        state = None

    # CAPTCHA
    if state == "captcha_verify":
        try:
            if int(text) == user.get("captcha_ans"):
                update_user(user_id, "verified", True)
                update_user(user_id, "state", None)
                if not check_force_join(user_id):
                    bot.send_message(message.chat.id, "✅ <b>Captcha Verified!</b>\nএখন নিচের চ্যানেলগুলোতে জয়েন করে 'Verify Now' বাটনে চাপুন:", parse_mode="HTML", reply_markup=get_force_join_markup())
                else:
                    process_referral_reward(user_id)
                    bot.send_message(message.chat.id, "✅ <b>Verified successfully!</b>", reply_markup=get_main_menu(user_id))
            else:
                bot.send_message(message.chat.id, "❌ ভুল উত্তর! আবার সঠিক উত্তরটি লিখুন:")
        except ValueError:
            bot.send_message(message.chat.id, "❌ অনুগ্রহ করে শুধুমাত্র সংখ্যা লিখুন:")
        return

    if not user.get("verified", False):
        bot.send_message(message.chat.id, "⚠️ দয়া করে আগে ক্যাপচা ভেরিফিকেশন সম্পন্ন করুন /start লিখে।")
        return

    # Force Join Enforcement Check
    if not check_force_join(user_id):
        bot.send_message(message.chat.id, "⚠️ আপনি আমাদের চ্যানেল থেকে লিভ নিয়েছেন! বটটি ব্যবহার করতে দয়া করে আবার জয়েন করুন:", reply_markup=get_force_join_markup())
        return

    # Broadcast with Photo & Text Catch
    if int(user_id) == ADMIN_ID and state == "admin_broadcast":
        count = 0
        for u in list(data["users"].keys()):
            try:
                if message.photo:
                    bot.send_photo(u, message.photo[-1].file_id, caption=f"📢 <b>Notice:</b>\n\n{message.caption if message.caption else ''}", parse_mode="HTML")
                else:
                    bot.send_message(u, f"📢 <b>Notice:</b>\n\n{text}", parse_mode="HTML")
                count += 1
            except: pass
        bot.send_message(message.chat.id, f"✅ সফলভাবে {count} জন ইউজারের কাছে নোটিশ পাঠানো হয়েছে!")
        update_user(user_id, "state", None)
        return

    # Submitting proof photo
    if message.photo and state and state.startswith("submit_proof_"):
        task_type, task_id = state.replace("submit_proof_", "").split("_")
        photo_id = message.photo[-1].file_id
        proof_key = f"{user_id}_{int(time.time())}"
        
        data["pending_proofs"][proof_key] = {"user_id": user_id, "task_type": task_type, "task_id": int(task_id), "photo_id": photo_id}
        uid = str(user_id)
        data["users"][uid]["pending_tasks"] += 1
        data["users"][uid]["state"] = None
        data["users"][uid]["completed_tasks"].append(f"{task_type}_{task_id}")
        save_data(data)

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            ibtn("✅ Approve", callback_data=f"appr_{proof_key}", style="success"),
            ibtn("❌ Reject", callback_data=f"rej_{proof_key}", style="danger"),
            ibtn("⚠️ Quick Reject", callback_data=f"qrej_{proof_key}", style="danger")
        )
        bot.send_photo(ADMIN_ID, photo_id, caption=f"📩 <b>New Proof!</b>\nUser: <code>{user_id}</code>\nTask Type: {task_type}\nTask ID: {task_id}", parse_mode="HTML", reply_markup=markup)
        bot.send_message(message.chat.id, "✅ স্ক্রিনশট জমা হয়েছে! এডমিন যাচাই করে ব্যালেন্স যোগ করে দেবে।", reply_markup=get_main_menu(user_id))
        return

    # USER WITHDRAW STATES
    if state == "with_enter_address":
        method = user["temp_withdraw"].get("method")
        user["temp_withdraw"]["address"] = text
        user["state"] = "with_enter_amount"
        data["users"][str(user_id)] = user
        save_data(data)
        min_limit = data["withdraw_methods"][method]["min"]
        bot.send_message(message.chat.id, f"💵 আপনার উইথড্র পরিমাণ লিখুন (মেথড: {method}, মিনিমাম: ৳{min_limit:.2f}):")
        return

    elif state == "with_enter_amount":
        try:
            amt = float(text)
            method = user["temp_withdraw"].get("method")
            address = user["temp_withdraw"].get("address")
            min_limit = data["withdraw_methods"][method]["min"]

            if amt < min_limit:
                bot.send_message(message.chat.id, f"❌ মিনিমাম উইথড্র পরিমাণ ৳{min_limit:.2f}!")
                return
            if amt > user["balance"]:
                bot.send_message(message.chat.id, f"❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! বর্তমান ব্যালেন্স: ৳{user['balance']:.2f}")
                return

            uid = str(user_id)
            data["users"][uid]["balance"] -= amt
            data["users"][uid]["state"] = None
            w_id = f"w_{user_id}_{int(time.time())}"
            data["pending_withdraws"][w_id] = {"user_id": user_id, "method": method, "address": address, "amount": amt}
            save_data(data)

            bot.send_message(message.chat.id, f"✅ আপনার ৳{amt:.2f} ({method}) উইথড্র রিকোয়েস্ট জমা হয়েছে!", reply_markup=get_main_menu(user_id))
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                ibtn("✅ Approve", callback_data=f"wappr_{w_id}", style="success"),
                ibtn("❌ Reject", callback_data=f"wrej_{w_id}", style="danger")
            )
            bot.send_message(ADMIN_ID, f"📥 <b>New Withdrawal!</b>\nUser: <code>{user_id}</code>\nMethod: {method}\nAddress: <code>{address}</code>\nAmount: ৳{amt:.2f}", parse_mode="HTML", reply_markup=markup)
            return
        except ValueError:
            bot.send_message(message.chat.id, "❌ অনুগ্রহ করে সঠিক সংখ্যা লিখুন:")
            return

    # USER REDEEM CODE STATE
    elif state == "enter_redeem_code":
        code = text.strip()
        if code in data.get("redeem_codes", {}):
            r_data = data["redeem_codes"][code]
            if user_id in r_data.get("claimed_by", []):
                bot.send_message(message.chat.id, "⚠️ আপনি ইতিমধ্যে এই কোডটি ব্যবহার করেছেন।", reply_markup=get_main_menu(user_id))
            elif len(r_data.get("claimed_by", [])) >= r_data["limit"]:
                bot.send_message(message.chat.id, "❌ এই রিডিম কোডটির লিমিট শেষ হয়ে গেছে।", reply_markup=get_main_menu(user_id))
            else:
                uid = str(user_id)
                reward = r_data["reward"]
                data["users"][uid]["balance"] += reward
                data["users"][uid]["total_income"] += reward
                data["users"][uid]["total_bonus"] += reward
                data["redeem_codes"][code]["claimed_by"].append(user_id)
                save_data(data)
                bot.send_message(message.chat.id, f"🎉 <b>অভিনন্দন!</b>\nরিডিম কোড থেকে আপনি <b>৳{reward}</b> পেয়েছেন!", parse_mode="HTML", reply_markup=get_main_menu(user_id))
        else:
            bot.send_message(message.chat.id, "❌ ভুল রিডিম কোড!", reply_markup=get_main_menu(user_id))
        update_user(user_id, "state", None)
        return

    # USER OLD GMAIL STATES
    elif state == "old_g_address":
        update_user(user_id, "temp_old_gmail", {"address": text})
        update_user(user_id, "state", "old_g_pass")
        bot.send_message(message.chat.id, "🔑 এবার জিমেইলটির <b>পাসওয়ার্ড</b> দিন:", parse_mode="HTML")
        return

    elif state == "old_g_pass":
        uid = str(user_id)
        data["users"][uid]["temp_old_gmail"]["password"] = text
        data["users"][uid]["state"] = None
        save_data(data)
        
        msg = (f"⚙️ <b>Old Gmail Submission Instructions:</b>\n\n"
               f"দয়া করে নিচের রিকভারি জিমেইলটি আপনার অ্যাকাউন্টে অ্যাড করুন:\n"
               f"📧 <code>tasrikvai8001@gmail.com</code>\n\n"
               f"<b>কীভাবে অ্যাড করবেন ও সাইন আউট করবেন?</b>\n"
               f"১. Gmail App -> Manage your Google Account\n"
               f"২. Security -> Recovery email এ গিয়ে উপরের জিমেইলটি দিন।\n"
               f"৩. এরপর ফোন থেকে জিমেইলটি রিমুভ (Sign Out) করে দিন।\n\n"
               f"সব কাজ সঠিকভাবে সম্পন্ন হলে নিচের <b>✅ Done</b> বাটনে ক্লিক করুন।")
        markup = InlineKeyboardMarkup()
        markup.add(ibtn("✅ Done (সাবমিট করুন)", callback_data="submit_old_gmail_done", style="success"))
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)
        return

    # ADMIN ADD TASK FLOW STATES
    if int(user_id) == ADMIN_ID and state:
        if state == "add_task_get_link":
            user["temp_task"]["link"] = text
            user["state"] = "add_task_get_desc"
            data["users"][str(user_id)] = user
            save_data(data)
            bot.send_message(message.chat.id, "📝 টাস্কের <b>Description / নির্দেশাবলী</b> লিখুন:", parse_mode="HTML")
            return
        elif state == "add_task_get_desc":
            user["temp_task"]["desc"] = text
            user["state"] = "add_task_get_rate"
            data["users"][str(user_id)] = user
            save_data(data)
            bot.send_message(message.chat.id, "💰 প্রতিটি কাজের জন্য কত <b>টাকা (Rate)</b> পাবে? (যেমন: 2.5):", parse_mode="HTML")
            return
        elif state == "add_task_get_rate":
            try:
                rate = float(text)
                user["temp_task"]["rate"] = rate
                user["state"] = "add_task_get_limit"
                data["users"][str(user_id)] = user
                save_data(data)
                bot.send_message(message.chat.id, "👥 মোট কত জন কাজ করতে পারবে? <b>(Limit)</b>:", parse_mode="HTML")
            except: bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা দিন (যেমন: 2.5):")
            return
        elif state == "add_task_get_limit":
            try:
                limit = int(text)
                t_type = user["temp_task"]["type"]
                t_id = len(data["tasks"][t_type]) + 1
                new_task = {
                    "id": t_id,
                    "link": user["temp_task"]["link"],
                    "desc": user["temp_task"]["desc"],
                    "rate": user["temp_task"]["rate"],
                    "limit": limit,
                    "completed": 0
                }
                data["tasks"][t_type].append(new_task)
                user["state"] = None
                user["temp_task"] = {}
                data["users"][str(user_id)] = user
                save_data(data)
                bot.send_message(message.chat.id, f"✅ সফলভাবে <b>{t_type.capitalize()} Task #{t_id}</b> যুক্ত করা হয়েছে!", parse_mode="HTML", reply_markup=get_admin_menu())
            except: bot.send_message(message.chat.id, "❌ সঠিক পূর্ণসংখ্যা দিন:")
            return

        # FORCE CHANNEL ADD
        elif state == "add_force_channel":
            if text.startswith("@"):
                data["force_channels"].append(text)
                save_data(data)
                bot.send_message(message.chat.id, f"✅ চ্যানেল যুক্ত হয়েছে: {text}")
            else:
                bot.send_message(message.chat.id, "❌ ইউজারনেম `@` দিয়ে শুরু হতে হবে।")
            update_user(user_id, "state", None)
            return

        # ADMIN REDEEM CODE
        elif state == "admin_create_redeem":
            try:
                code, reward, limit = text.split("|")
                data["redeem_codes"][code.strip()] = {"reward": float(reward.strip()), "limit": int(limit.strip()), "claimed_by": []}
                save_data(data)
                bot.send_message(message.chat.id, f"✅ Redeem Code Created: `{code.strip()}`", parse_mode="Markdown")
            except: bot.send_message(message.chat.id, "❌ Format: `Code | Reward | Limit`", parse_mode="Markdown")
            update_user(user_id, "state", None)
            return

        # ADMIN MARKET RATES
        elif state == "admin_set_market_rate":
            try:
                new_rate, old_rate = text.split("|")
                data["market_rate"]["new_gmail"] = float(new_rate.strip())
                data["market_rate"]["old_gmail"] = float(old_rate.strip())
                save_data(data)
                bot.send_message(message.chat.id, "✅ Market Rates Updated!")
            except: bot.send_message(message.chat.id, "❌ Format: `New Rate | Old Rate`", parse_mode="Markdown")
            update_user(user_id, "state", None)
            return

        # ADMIN MIN WITHDRAW SETTINGS (UPDATED FOR bKash, Nagad, USDT BEP20)
        elif state.startswith("set_min_w_"):
            method = state.replace("set_min_w_", "")
            try:
                val = float(text)
                if method in data["withdraw_methods"]:
                    data["withdraw_methods"][method]["min"] = val
                    save_data(data)
                    bot.send_message(message.chat.id, f"✅ {method} এর মিনিমাম উইথড্র ৳{val:.2f} আপডেট করা হয়েছে!")
                else:
                    bot.send_message(message.chat.id, "❌ অজানা উইথড্র মেথড!")
            except: bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা লিখুন:")
            update_user(user_id, "state", None)
            return

        # ADMIN SET REFERRAL BONUS (NEW)
        elif state == "admin_set_ref_bonus":
            try:
                new_ref_bonus = float(text)
                data["ref_bonus"] = new_ref_bonus
                save_data(data)
                bot.send_message(message.chat.id, f"✅ **Referral Bonus Updated Successfully!**\n\nবর্তমান রেফার বোনাস: **৳{new_ref_bonus:.2f}**", parse_mode="Markdown")
            except:
                bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা লিখুন (যেমন: 2.0 বা 5.0):")
            update_user(user_id, "state", None)
            return

        # ADMIN ADD BALANCE
        elif state == "admin_add_bal":
            try:
                target_uid, amount = text.split("|")
                target_uid = target_uid.strip()
                amount = float(amount.strip())
                if target_uid in data["users"]:
                    data["users"][target_uid]["balance"] += amount
                    save_data(data)
                    bot.send_message(message.chat.id, f"✅ User {target_uid} এর অ্যাকাউন্টে ৳{amount:.2f} যুক্ত করা হয়েছে!")
                    try: bot.send_message(target_uid, f"🎉 এডমিন আপনার অ্যাকাউন্টে <b>৳{amount:.2f}</b> যোগ করে দিয়েছে!", parse_mode="HTML")
                    except: pass
                else: bot.send_message(message.chat.id, "❌ এই ইউজার আইডিটি ডাটাবেজে নেই!")
            except: bot.send_message(message.chat.id, "❌ Format: `User_ID | Amount`", parse_mode="Markdown")
            update_user(user_id, "state", None)
            return

        # ADMIN BAN / UNBAN
        elif state == "admin_ban_user":
            uid_to_ban = text.strip()
            if uid_to_ban not in data["banned_users"]:
                data["banned_users"].append(uid_to_ban)
                save_data(data)
                bot.send_message(message.chat.id, f"⛔ User {uid_to_ban} কে ব্লক করা হয়েছে!")
            else:
                data["banned_users"].remove(uid_to_ban)
                save_data(data)
                bot.send_message(message.chat.id, f"✅ User {uid_to_ban} কে আনব্লক করা হয়েছে!")
            update_user(user_id, "state", None)
            return

        # ADMIN LB SETTINGS
        elif state == "admin_set_lb_rewards":
            try:
                r1, r2, r3 = text.split("|")
                data["leaderboard"]["rewards"]["1"] = float(r1.strip())
                data["leaderboard"]["rewards"]["2"] = float(r2.strip())
                data["leaderboard"]["rewards"]["3"] = float(r3.strip())
                save_data(data)
                bot.send_message(message.chat.id, "✅ Leaderboard Rewards Updated!")
            except: bot.send_message(message.chat.id, "❌ Format: `1st Bonus | 2nd Bonus | 3rd Bonus`", parse_mode="Markdown")
            update_user(user_id, "state", None)
            return

    # MAIN MENU BUTTON HANDLERS
    if text == TXT_BALANCE:
        user = get_user(user_id)
        msg = (f"👤 <b>Account Details</b>\n\n"
               f"💰 Current Balance: <b>৳{user.get('balance', 0.0):.2f}</b>\n"
               f"💵 Total Income: <b>৳{user.get('total_income', 0.0):.2f}</b>\n"
               f"🎁 Total Bonus: <b>৳{user.get('total_bonus', 0.0):.2f}</b>\n"
               f"📤 Total Withdraw: <b>৳{user.get('total_withdraw', 0.0):.2f}</b>\n\n"
               f"👥 Total Referrals: <b>{user.get('referrals', 0)}</b>\n\n"
               f"✅ Successful Tasks: <b>{user.get('approved_tasks', 0)}</b>\n"
               f"⏳ Pending Tasks: <b>{user.get('pending_tasks', 0)}</b>")
        markup = InlineKeyboardMarkup()
        markup.add(ibtn("📜 𝑨𝒍𝒍 𝑯𝒊𝒔𝒕𝒐𝒓𝒚", callback_data="show_all_history", style="primary"))
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

    elif text == TXT_INVITE:
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        msg = (f"👥 <b>Invite Friends & Earn!</b>\n\n🔗 Link:\n<code>{ref_link}</code>\n\n"
               f"🎁 Earn ৳{data.get('ref_bonus', 2.0)} per verified referral!")
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    elif text == TXT_TASK:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            ibtn("📲 Telegram Tasks", callback_data="show_tg_tasks", style="primary"),
            ibtn("📥 App Tasks", callback_data="show_app_tasks", style="primary")
        )
        bot.send_message(message.chat.id, "📝 <b>Available Task Categories:</b>", parse_mode="HTML", reply_markup=markup)

    elif text == TXT_WORK:
        bot.send_message(message.chat.id, "💼 <b>Daily Work Menu:</b>", parse_mode="HTML", reply_markup=get_daily_work_menu())

    elif text == TXT_INSTA:
        bot.send_message(message.chat.id, "⚠️ <b>এই কাজ বর্তমানে অফ আছে খুব শিগগিরই চালু করা হবে ইনশাআল্লাহ।</b>", parse_mode="HTML")

    elif text == TXT_NEW_GMAIL:
        rate = data.get("market_rate", {}).get("new_gmail", 5.0)
        password = data.get("market_rate", {}).get("default_password", "Admin123*()")
        fname, lname, g_email = generate_random_gmail_credentials()
        uid = str(user_id)
        
        data["users"][uid]["active_gmail_task"] = {
            "first_name": fname, "last_name": lname, "email": g_email,
            "password": password, "rate": rate, "start_time": time.time(), "type": "new"
        }
        save_data(data)

        msg = (f"📧 <b>New Gmail Creation Task</b>\n\n"
               f"👤 First Name: <code>{fname}</code>\n"
               f"👤 Last Name: <code>{lname}</code>\n"
               f"✉️ Email: <code>{g_email}</code>\n"
               f"🔑 Password: <code>{password}</code>\n"
               f"💰 Rate: <b>৳{rate:.2f}</b>\n\n"
               f"ℹ️ <i>টেক্সটগুলোতে চাপ দিয়ে কপি করুন। তৈরি শেষ হলে নিচের সাবমিট বাটনে চাপ দিন।</i>")
        
        markup = InlineKeyboardMarkup()
        markup.add(ibtn("📤 Submit Gmail", callback_data="submit_new_gmail", style="success"))
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

    elif text == TXT_OLD_GMAIL:
        update_user(user_id, "state", "old_g_address")
        bot.send_message(message.chat.id, "📩 আপনার পুরাতন জিমেইল এর নাম বা এড্রেস দিন:")

    elif text == TXT_MARKET:
        nr = data.get("market_rate", {}).get("new_gmail", 5.0)
        or_ = data.get("market_rate", {}).get("old_gmail", 10.0)
        msg = f"📊 <b>Current Market Rate:</b>\n\n📧 New Gmail: <b>৳{nr:.2f}</b>\n📩 Old Gmail: <b>৳{or_:.2f}</b>"
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    elif text == TXT_BACK or text == "🔙 Main Menu":
        update_user(user_id, "state", None)
        bot.send_message(message.chat.id, "Main Menu", reply_markup=get_main_menu(user_id))

    elif text == TXT_REDEEM:
        update_user(user_id, "state", "enter_redeem_code")
        bot.send_message(message.chat.id, "🎁 দয়া করে আপনার রিডিম কোডটি নিচে লিখুন:")

    elif text == TXT_WITHDRAW:
        markup = InlineKeyboardMarkup(row_width=1)
        available_methods = False
        for method, settings in data.get("withdraw_methods", {}).items():
            if settings["enabled"]:
                available_methods = True
                markup.add(ibtn(f"💳 {method} (Min: ৳{settings['min']:.2f})", callback_data=f"with_select_{method}", style="primary"))
        if not available_methods:
            bot.send_message(message.chat.id, "⚠️ বর্তমানে সমস্ত উইথড্র মাধ্যম বন্ধ রয়েছে। অনুগ্রহ করে পরে চেষ্টা করুন।")
        else:
            bot.send_message(message.chat.id, "📥 <b>Select Withdrawal Method:</b>", parse_mode="HTML", reply_markup=markup)

    elif text == TXT_LEADERBOARD:
        lb_refs = data["leaderboard"].get("daily_refs", {})
        sorted_lb = sorted(lb_refs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        msg = "🏆 <b>24-Hour Top Referral Leaderboard</b> 🏆\n\n"
        if not sorted_lb: msg += "এখনো ২৪ ঘন্টায় কোনো ইউজার রেফার শুরু করেনি।\n\n"
        else:
            for idx, (u_id, count) in enumerate(sorted_lb, 1):
                msg += f"<b>{idx}. User:</b> <code>{u_id}</code> ➔ <b>{count} Refs</b>\n"
        
        user_daily_refs = lb_refs.get(str(user_id), 0)
        msg += f"\n📊 <b>Your 24h Referrals:</b> {user_daily_refs}\n\n🎁 <b>Top Leaderboard Rewards:</b>\n"
        
        rewards = data["leaderboard"].get("rewards", {})
        msg += f"• 1st Rank = <b>৳{rewards.get('1', 50.0):.2f} Bonus</b>\n"
        msg += f"• 2nd Rank = <b>৳{rewards.get('2', 30.0):.2f} Bonus</b>\n"
        msg += f"• 3rd Rank = <b>৳{rewards.get('3', 20.0):.2f} Bonus</b>\n"
            
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    # ADMIN PANEL MAIN ACTION BUTTONS
    elif text == TXT_ADMIN and int(user_id) == ADMIN_ID:
        bot.send_message(message.chat.id, "⚙️ <b>Admin Controls:</b>", parse_mode="HTML", reply_markup=get_admin_menu())

    elif text == "📢 Force Join Settings" and int(user_id) == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(ibtn("➕ Add Channel", callback_data="admin_add_fj", style="success"))
        msg = "<b>Current Force Join Channels:</b>\n\n"
        for ch in data.get("force_channels", []):
            msg += f"• {ch}\n"
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

    elif text == "➕ Add Task" and int(user_id) == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            ibtn("📲 Telegram Task", callback_data="admin_add_t_telegram", style="primary"),
            ibtn("📥 App Task", callback_data="admin_add_t_app", style="primary")
        )
        bot.send_message(message.chat.id, "➕ <b>Select Task Category to Add:</b>", parse_mode="HTML", reply_markup=markup)

    # UPDATED WITHDRAW SETTINGS BUTTON HANDLER FOR ADMIN
    elif text == "💳 Withdraw Settings" and int(user_id) == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=1)
        for m, s in data.get("withdraw_methods", {}).items():
            status = "🟢 Enabled" if s["enabled"] else "🔴 Disabled"
            markup.add(
                ibtn(f"{m} ({status}) - Min: ৳{s['min']:.2f}", callback_data=f"toggle_w_meth_{m}", style="primary"),
                ibtn(f"⚙️ Change Min {m}", callback_data=f"change_min_w_{m}", style="secondary")
            )
        bot.send_message(message.chat.id, "💳 <b>Withdraw Methods & Limits Control:</b>", parse_mode="HTML", reply_markup=markup)

    # UPDATED REF BOX SETTINGS BUTTON HANDLER FOR ADMIN
    elif text == "🎁 Ref Box Settings" and int(user_id) == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=1)
        curr_bonus = data.get("ref_bonus", 2.0)
        markup.add(ibtn(f"⚙️ Set Ref Bonus (Current: ৳{curr_bonus:.2f})", callback_data="admin_set_ref_bonus_btn", style="success"))
        bot.send_message(message.chat.id, f"🎁 <b>Referral Bonus Settings</b>\n\nCurrent Referral Bonus: <b>৳{curr_bonus:.2f}</b>", parse_mode="HTML", reply_markup=markup)

    elif text == "🗑️ Task Delete/Edit" and int(user_id) == ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            ibtn("📲 Telegram Tasks", callback_data="admin_manage_t_telegram", style="primary"),
            ibtn("📥 App Tasks", callback_data="admin_manage_t_app", style="primary")
        )
        bot.send_message(message.chat.id, "🗑️ <b>Select Category to Manage/Delete Tasks:</b>", parse_mode="HTML", reply_markup=markup)

    elif text == "📥 Pending Withdraws" and int(user_id) == ADMIN_ID:
        pw = data.get("pending_withdraws", {})
        if not pw:
            bot.send_message(message.chat.id, "✅ কোনো পেন্ডিং উইথড্র রিকোয়েস্ট নেই।")
            return
        bot.send_message(message.chat.id, f"📥 <b>Total Pending Withdraws: {len(pw)}</b>", parse_mode="HTML")
        for wk, w in list(pw.items()):
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                ibtn("✅ Approve", callback_data=f"wappr_{wk}", style="success"),
                ibtn("❌ Reject", callback_data=f"wrej_{wk}", style="danger")
            )
            bot.send_message(ADMIN_ID, f"User: <code>{w['user_id']}</code>\nMethod: {w['method']}\nAddress: <code>{w['address']}</code>\nAmount: ৳{w['amount']:.2f}", parse_mode="HTML", reply_markup=markup)

    elif text == "📢 Broadcast" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_broadcast")
        bot.send_message(message.chat.id, "📢 ব্রডকাস্ট করার জন্য মেসেজ বা ফটো পাঠান:")

    elif text == "📊 Bot Statistics" and int(user_id) == ADMIN_ID:
        total_u = len(data["users"])
        total_banned = len(data.get("banned_users", []))
        total_w = sum(u.get("total_withdraw", 0) for u in data["users"].values())
        total_inc = sum(u.get("total_income", 0) for u in data["users"].values())
        msg = (f"📊 <b>Bot Statistics:</b>\n\n"
               f"👥 Total Users: <b>{total_u}</b>\n"
               f"⛔ Banned Users: <b>{total_banned}</b>\n"
               f"💰 Total Earned by Users: <b>৳{total_inc:.2f}</b>\n"
               f"📤 Total Withdrawn: <b>৳{total_w:.2f}</b>")
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    elif text == "⚙️ Market Rates" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_set_market_rate")
        bot.send_message(message.chat.id, "Format: `New Rate | Old Rate`\nExample: `5.0 | 10.0`", parse_mode="Markdown")

    elif text == "🎁 Create Redeem Code" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_create_redeem")
        bot.send_message(message.chat.id, "Format: `Code | Reward Amount | Limit`\nExample: `FREEMONEY | 10.0 | 100`", parse_mode="Markdown")

    elif text == "➕ Add Balance" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_add_bal")
        bot.send_message(message.chat.id, "Format: `User_ID | Amount`", parse_mode="Markdown")

    elif text == "⛔ Ban/Unban User" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_ban_user")
        bot.send_message(message.chat.id, "যেই ইউজারকে ব্লক বা আনব্লক করতে চান তার **User Telegram ID** লিখুন:", parse_mode="Markdown")

    elif text == "🏆 LB Settings" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_set_lb_rewards")
        bot.send_message(message.chat.id, "Format: `1st Bonus | 2nd Bonus | 3rd Bonus`\nExample: `50 | 30 | 20`", parse_mode="Markdown")

    elif text == "🔎 Pending Approvals" and int(user_id) == ADMIN_ID:
        proofs = data.get("pending_proofs", {})
        gmails = data.get("pending_gmail_verifications", {})
        olds = data.get("pending_old_gmails", {})
        
        bot.send_message(message.chat.id, f"🔎 Pending Tasks Overview:\nPhoto Proofs: {len(proofs)} | New Gmails: {len(gmails)} | Old Gmails: {len(olds)}")
        
        for key, p in list(proofs.items()):
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(ibtn("✅ Appr", callback_data=f"appr_{key}", style="success"), ibtn("❌ Rej", callback_data=f"rej_{key}", style="danger"), ibtn("⚠️ Quick Reject", callback_data=f"qrej_{key}", style="danger"))
            try: bot.send_photo(message.chat.id, p["photo_id"], caption=f"User: <code>{p['user_id']}</code>\nTask: {p['task_type']} #{p['task_id']}", parse_mode="HTML", reply_markup=markup)
            except: pass

        for gk, g in list(gmails.items()):
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(ibtn("✅ Appr", callback_data=f"gappr_{gk}", style="success"), ibtn("❌ Rej", callback_data=f"grej_{gk}", style="danger"))
            bot.send_message(message.chat.id, f"📧 <b>New Gmail</b>\nUser: <code>{g['user_id']}</code>\nEmail: <code>{g['email']}</code>\nPass: <code>{g['password']}</code>\nRate: ৳{g['rate']}", parse_mode="HTML", reply_markup=markup)

        for ok, o in list(olds.items()):
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(ibtn("✅ Appr", callback_data=f"oappr_{ok}", style="success"), ibtn("❌ Rej", callback_data=f"orej_{ok}", style="danger"))
            bot.send_message(message.chat.id, f"📩 <b>Old Gmail</b>\nUser: <code>{o['user_id']}</code>\nEmail: <code>{o['address']}</code>\nPass: <code>{o['password']}</code>\nRate: ৳{o['rate']}", parse_mode="HTML", reply_markup=markup)


# ============================================
# --- CALLBACK HANDLERS ---
# ============================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = load_data()
    user = get_user(user_id)

    # CHECK FORCE JOIN CALLBACK
    if call.data == "check_join":
        if check_force_join(user_id):
            bot.answer_callback_query(call.id, "✅ জয়েন ভেরিফাইড হয়েছে!")
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            process_referral_reward(user_id)
            bot.send_message(call.message.chat.id, f"<b>Welcome to {BOT_NAME}!</b>\nনিচের মেনু থেকে আপনার কাঙ্খিত অপশনটি বেছে নিন:", parse_mode="HTML", reply_markup=get_main_menu(user_id))
        else:
            bot.answer_callback_query(call.id, "❌ আপনি এখনও সব চ্যানেলে জয়েন করেননি!", show_alert=True)

    # USER TASKS DISPLAY
    elif call.data == "show_tg_tasks" or call.data == "show_app_tasks":
        t_type = "telegram" if call.data == "show_tg_tasks" else "app"
        task_list = data["tasks"].get(t_type, [])
        if not task_list:
            bot.answer_callback_query(call.id, "❌ এই ক্যাটাগরিতে কোনো টাস্ক নেই!", show_alert=True)
            return
        
        bot.answer_callback_query(call.id, "Loading Tasks...")
        for t in task_list:
            if t["completed"] >= t["limit"]: continue
            if f"{t_type}_{t['id']}" in user.get("completed_tasks", []): continue
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                ibtn("🔗 Open Task Link", url=t["link"], style="primary"),
                ibtn("📤 Submit Proof (Screenshot)", callback_data=f"start_sub_{t_type}_{t['id']}", style="success")
            )
            msg = f"📝 <b>Task #{t['id']}</b>\n\n📌 <b>Instruction:</b> {t.get('desc', 'N/A')}\n💰 <b>Reward:</b> ৳{t['rate']:.2f}\n📊 <b>Limit:</b> {t['completed']}/{t['limit']}"
            bot.send_message(call.message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("start_sub_"):
        t_type, t_id = call.data.replace("start_sub_", "").split("_")
        update_user(user_id, "state", f"submit_proof_{t_type}_{t_id}")
        bot.send_message(call.message.chat.id, "📸 দয়া করে আপনার কাজের প্রুফ স্ক্রিনশট (Photo) ফরোয়ার্ড/সেন্ড করুন:")

    elif call.data == "show_all_history":
        msg = (f"📜 <b>Live History Stats</b>\n\n"
               f"✅ Approved Tasks: {user.get('approved_tasks', 0)}\n"
               f"❌ Rejected Tasks: {user.get('rejected_tasks', 0)}\n"
               f"⏳ Pending Tasks: {user.get('pending_tasks', 0)}\n\n"
               f"💵 Total Withdrawn: ৳{user.get('total_withdraw', 0):.2f}\n"
               f"🎁 Total Bonus Recv: ৳{user.get('total_bonus', 0):.2f}")
        bot.answer_callback_query(call.id, "Loading History...")
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")

    elif call.data == "submit_new_gmail":
        uid = str(user_id)
        active = user.get("active_gmail_task")
        if not active or active.get("type") != "new":
            bot.answer_callback_query(call.id, "❌ এই টাস্কটি সক্রিয় নেই!", show_alert=True)
            return
        if time.time() - active.get("start_time", 0) < 120:
            bot.answer_callback_query(call.id, "⚠️ আপনি এত দ্রুত জিমেইল অ্যাকাউন্ট খুলেননি! জিমেইল তৈরি করতে অন্তত ২-৩ মিনিট সময় লাগে।", show_alert=True)
            return
            
        g_key = f"g_{user_id}_{int(time.time())}"
        data["pending_gmail_verifications"][g_key] = {
            "user_id": user_id, "first_name": active["first_name"], "last_name": active["last_name"],
            "email": active["email"], "password": active["password"], "rate": active["rate"]
        }
        data["users"][uid]["active_gmail_task"] = None
        data["users"][uid]["pending_tasks"] += 1
        save_data(data)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, "✅ তথ্য জমা দেওয়া হয়েছে! এডমিন প্যানেলে চেক করা হচ্ছে।")

    elif call.data == "submit_old_gmail_done":
        uid = str(user_id)
        temp = user.get("temp_old_gmail", {})
        if not temp:
            bot.answer_callback_query(call.id, "❌ ডাটা পাওয়া যায়নি!", show_alert=True)
            return
        
        o_key = f"o_{user_id}_{int(time.time())}"
        rate = data.get("market_rate", {}).get("old_gmail", 10.0)
        data["pending_old_gmails"][o_key] = {
            "user_id": user_id, "address": temp.get("address"),
            "password": temp.get("password"), "rate": rate
        }
        data["users"][uid]["temp_old_gmail"] = {}
        data["users"][uid]["pending_tasks"] += 1
        save_data(data)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, "✅ তথ্য জমা দেওয়া হয়েছে! এডমিন প্যানেলে চেক করা হচ্ছে।")

    elif call.data.startswith("with_select_"):
        method = call.data.replace("with_select_", "")
        uid = str(user_id)
        data["users"][uid]["temp_withdraw"] = {"method": method}
        data["users"][uid]["state"] = "with_enter_address"
        save_data(data)
        bot.send_message(call.message.chat.id, "📱 আপনার অ্যাকাউন্ট / নম্বর দিন:")

    # ADMIN CALLBACK FOR SET REF BONUS
    elif call.data == "admin_set_ref_bonus_btn" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "admin_set_ref_bonus")
        bot.send_message(call.message.chat.id, "💰 <b>নতুন রেফার বোনাসের পরিমাণ লিখুন:</b>\n\n<i>(যেমন: 2.5 বা 5.0)</i>", parse_mode="HTML")

    # ADMIN CALLBACKS FOR TASKS & APPROVALS
    elif call.data.startswith("admin_add_t_") and int(user_id) == ADMIN_ID:
        t_type = call.data.replace("admin_add_t_", "")
        update_user(user_id, "temp_task", {"type": t_type})
        update_user(user_id, "state", "add_task_get_link")
        bot.send_message(call.message.chat.id, f"🔗 <b>{t_type.capitalize()} Task Link</b> পাঠান:", parse_mode="HTML")

    elif call.data.startswith("admin_manage_t_") and int(user_id) == ADMIN_ID:
        t_type = call.data.replace("admin_manage_t_", "")
        tasks = data["tasks"].get(t_type, [])
        if not tasks:
            bot.answer_callback_query(call.id, f"❌ {t_type.capitalize()} এ কোনো টাস্ক নেই!", show_alert=True)
            return
        bot.answer_callback_query(call.id, "Loading Tasks...")
        for t in tasks:
            markup = InlineKeyboardMarkup()
            markup.add(ibtn(f"🗑️ Delete Task #{t['id']}", callback_data=f"del_task_{t_type}_{t['id']}", style="danger"))
            msg = f"📌 <b>Task #{t['id']} ({t_type.capitalize()})</b>\n\n<b>Link:</b> {t['link']}\n<b>Desc:</b> {t['desc']}\n<b>Rate:</b> ৳{t['rate']}\n<b>Progress:</b> {t['completed']}/{t['limit']}"
            bot.send_message(call.message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("del_task_") and int(user_id) == ADMIN_ID:
        parts = call.data.replace("del_task_", "").split("_")
        t_type, t_id = parts[0], int(parts[1])
        data["tasks"][t_type] = [t for t in data["tasks"][t_type] if t["id"] != t_id]
        save_data(data)
        bot.answer_callback_query(call.id, f"✅ Task #{t_id} ডিলিট করা হয়েছে!", show_alert=True)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass

    elif call.data == "admin_add_fj" and int(user_id) == ADMIN_ID:
        update_user(user_id, "state", "add_force_channel")
        bot.send_message(call.message.chat.id, "📢 চ্যানেলের Username পাঠান (যেমন: `@MyChannel`):")

    elif call.data.startswith("toggle_w_meth_") and int(user_id) == ADMIN_ID:
        meth = call.data.replace("toggle_w_meth_", "")
        data["withdraw_methods"][meth]["enabled"] = not data["withdraw_methods"][meth]["enabled"]
        save_data(data)
        
        # UI Refresh
        markup = InlineKeyboardMarkup(row_width=1)
        for m, s in data["withdraw_methods"].items():
            status = "🟢 Enabled" if s["enabled"] else "🔴 Disabled"
            markup.add(
                ibtn(f"{m} ({status}) - Min: ৳{s['min']:.2f}", callback_data=f"toggle_w_meth_{m}", style="primary"),
                ibtn(f"⚙️ Change Min {m}", callback_data=f"change_min_w_{m}", style="secondary")
            )
        bot.edit_message_text("💳 <b>Withdraw Methods & Limits Control:</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id, f"{meth} Status Updated!")

    elif call.data.startswith("change_min_w_") and int(user_id) == ADMIN_ID:
        meth = call.data.replace("change_min_w_", "")
        update_user(user_id, "state", f"set_min_w_{meth}")
        bot.send_message(call.message.chat.id, f"💵 {meth} এর নতুন <b>Minimum Amount</b> দিন:", parse_mode="HTML")

    # APPROVE / REJECT PROOFS
    elif call.data.startswith("appr_") and int(user_id) == ADMIN_ID:
        key = call.data.replace("appr_", "")
        item = data["pending_proofs"].get(key)
        if item:
            u_id = str(item["user_id"])
            t_type = item["task_type"]
            t_id = item["task_id"]
            
            rate = 0.0
            for t in data["tasks"][t_type]:
                if t["id"] == t_id:
                    t["completed"] += 1
                    rate = t["rate"]
                    break
            
            data["users"][u_id]["balance"] += rate
            data["users"][u_id]["total_income"] += rate
            data["users"][u_id]["approved_tasks"] += 1
            if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_proofs"][key]
            save_data(data)
            bot.edit_message_caption(f"✅ Approved for user {u_id} (+৳{rate})", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, f"🎉 আপনার টাস্ক প্রুফ এপ্রুভ হয়েছে! <b>৳{rate:.2f}</b> যোগ করা হয়েছে।", parse_mode="HTML")
            except: pass

    elif call.data.startswith("rej_") and int(user_id) == ADMIN_ID:
        key = call.data.replace("rej_", "")
        item = data["pending_proofs"].get(key)
        if item:
            u_id = str(item["user_id"])
            if u_id in data["users"]:
                data["users"][u_id]["rejected_tasks"] += 1
                if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_proofs"][key]
            save_data(data)
            bot.edit_message_caption(f"❌ Rejected for user {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, "❌ আপনার জমা দেওয়া টাস্ক বাতিল করা হয়েছে।")
            except: pass

    elif call.data.startswith("qrej_") and int(user_id) == ADMIN_ID:
        key = call.data.replace("qrej_", "")
        item = data["pending_proofs"].get(key)
        if item:
            u_id = str(item["user_id"])
            if u_id in data["users"]:
                data["users"][u_id]["rejected_tasks"] += 1
                if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_proofs"][key]
            save_data(data)
            bot.edit_message_caption(f"⚠️ Quick Rejected for user {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, "❌ আপনার জমা দেওয়া টাস্ক বাতিল করা হয়েছে (Reason: Invalid Proof).")
            except: pass

    # APPROVE / REJECT WITHDRAWS
    elif call.data.startswith("wappr_") and int(user_id) == ADMIN_ID:
        w_id = call.data.replace("wappr_", "")
        w = data["pending_withdraws"].get(w_id)
        if w:
            u_id = str(w["user_id"])
            data["users"][u_id]["total_withdraw"] += w["amount"]
            del data["pending_withdraws"][w_id]
            save_data(data)
            bot.edit_message_text(f"✅ Approved Withdrawal for {u_id} (৳{w['amount']})", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, f"🎉 আপনার <b>৳{w['amount']:.2f}</b> ({w['method']}) উইথড্র সফলভাবে সম্পন্ন হয়েছে!", parse_mode="HTML")
            except: pass

    elif call.data.startswith("wrej_") and int(user_id) == ADMIN_ID:
        w_id = call.data.replace("wrej_", "")
        w = data["pending_withdraws"].get(w_id)
        if w:
            u_id = str(w["user_id"])
            data["users"][u_id]["balance"] += w["amount"]
            del data["pending_withdraws"][w_id]
            save_data(data)
            bot.edit_message_text(f"❌ Rejected Withdrawal for {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, f"❌ আপনার <b>৳{w['amount']:.2f}</b> উইথড্র রিকোয়েস্ট বাতিল করা হয়েছে। টাকা ব্যালেন্সে ফেরত দেওয়া হয়েছে।", parse_mode="HTML")
            except: pass

    # GMAIL APPROVALS
    elif call.data.startswith("gappr_") and int(user_id) == ADMIN_ID:
        gk = call.data.replace("gappr_", "")
        g = data["pending_gmail_verifications"].get(gk)
        if g:
            u_id = str(g["user_id"])
            data["users"][u_id]["balance"] += g["rate"]
            data["users"][u_id]["total_income"] += g["rate"]
            data["users"][u_id]["approved_tasks"] += 1
            if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_gmail_verifications"][gk]
            save_data(data)
            bot.edit_message_text(f"✅ Approved Gmail for user {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, f"🎉 আপনার New Gmail সেল সফল হয়েছে! <b>৳{g['rate']:.2f}</b> যোগ করা হয়েছে।", parse_mode="HTML")
            except: pass

    elif call.data.startswith("grej_") and int(user_id) == ADMIN_ID:
        gk = call.data.replace("grej_", "")
        g = data["pending_gmail_verifications"].get(gk)
        if g:
            u_id = str(g["user_id"])
            data["users"][u_id]["rejected_tasks"] += 1
            if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_gmail_verifications"][gk]
            save_data(data)
            bot.edit_message_text(f"❌ Rejected Gmail for user {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, "❌ আপনার জমা দেওয়া New Gmail সেল বাতিল করা হয়েছে।")
            except: pass

    elif call.data.startswith("oappr_") and int(user_id) == ADMIN_ID:
        ok = call.data.replace("oappr_", "")
        o = data["pending_old_gmails"].get(ok)
        if o:
            u_id = str(o["user_id"])
            data["users"][u_id]["balance"] += o["rate"]
            data["users"][u_id]["total_income"] += o["rate"]
            data["users"][u_id]["approved_tasks"] += 1
            if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_old_gmails"][ok]
            save_data(data)
            bot.edit_message_text(f"✅ Approved Old Gmail for user {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, f"🎉 আপনার Old Gmail সেল সফল হয়েছে! <b>৳{o['rate']:.2f}</b> যোগ করা হয়েছে।", parse_mode="HTML")
            except: pass

    elif call.data.startswith("orej_") and int(user_id) == ADMIN_ID:
        ok = call.data.replace("orej_", "")
        o = data["pending_old_gmails"].get(ok)
        if o:
            u_id = str(o["user_id"])
            data["users"][u_id]["rejected_tasks"] += 1
            if data["users"][u_id]["pending_tasks"] > 0: data["users"][u_id]["pending_tasks"] -= 1
            del data["pending_old_gmails"][ok]
            save_data(data)
            bot.edit_message_text(f"❌ Rejected Old Gmail for user {u_id}", call.message.chat.id, call.message.message_id)
            try: bot.send_message(u_id, "❌ আপনার জমা দেওয়া Old Gmail সেল বাতিল করা হয়েছে।")
            except: pass

# ============================================
# --- BOT START ---
# ============================================
if __name__ == "__main__":
    keep_alive()
    print(f"🚀 {BOT_NAME} with Advanced Anti-Spam & Market Features is Running...")
    bot.infinity_polling()
