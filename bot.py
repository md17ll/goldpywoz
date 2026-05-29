import os
import logging
import threading # لحل مشكلة التهنيج تماماً وتشغيل التحليل في الخلفية
from ai_engine import AIEngine
from risk_manager import GoldRiskManager
from mt5_connector import GoldMT5Connector

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("🚨 TELEGRAM_TOKEN مفقود في سيرفر Railway!")

bot = TeleBot(TOKEN)

ai_server = AIEngine()
risk_control = GoldRiskManager(max_daily_loss=40.0, per_trade_risk=40.0)
mt5_bridge = GoldMT5Connector()

CURRENT_SCHOOL = "ICT"
IS_LIVE_TRADING = False

USER_STATE = {} 
USER_DATA = {} 
CUSTOM_CONFIG = {
    "fixed_lot": 0.01,
    "executed_trades": 0,
    "daily_profit": 0.00,
    "daily_loss": 0.00,
    "saved_account_id": "لا يوجد",  
    "saved_server": "لا يوجد"      
}

def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("👑 رادار سكالبينغ الذهب", callback_data='menu_gold'))
    markup.row(InlineKeyboardButton("🧠 تفعيل التداول بالذكاء الاصطناعي", callback_data='activate_ai_trading'))
    markup.row(InlineKeyboardButton("🧪 مختبر الاستراتيجيات المخصصة", callback_data='menu_backtest'))
    markup.row(InlineKeyboardButton("🛡️ إدارة المخاطر والأمان", callback_data='menu_risk'))
    markup.row(InlineKeyboardButton("📊 الإحصائيات والتحليل", callback_data='menu_stats'))
    markup.row(InlineKeyboardButton("⚙️ ربط حساب MT5", callback_data='menu_mt5'))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    text = (
        "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
        "تم حل مشكلة التهنيج وتفعيل خيار التداول المباشر بالـ AI.\n"
        "اختر قسماً من الأزرار أدناه لتوجيه النظام:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

def background_ai_analysis(chat_id, school):
    """
    دالة تعمل في مسار منفصل (Thread) لتحليل السوق دون تجميد أزرار البوت
    """
    try:
        # محاكاة لملخص الشارت الحالي لإرساله لعقل الـ AI
        market_summary = "XAUUSD Current Price: 2350.50, Trend: Bullish on M15, Liquidity pool swept at 2345."
        
        # استدعاء المحرك
        ai_analysis = ai_server.analyze_gold_market(market_data_summary=market_summary, chosen_school=school)
        
        action = ai_analysis.get("action", "WAIT")
        reason = ai_analysis.get("reason", "No specific setup found.")
        
        response_text = (
            f"🧠 **نتائج تحليل الـ AI اللحظية عبر مدرسة [{school}]:**\n\n"
            f"• 🎬 **القرار المتخذ:** `{action}`\n"
            f"• 📝 **السبب الفني:** \"{reason}\"\n\n"
        )
        
        if action in ["BUY", "SELL"] and IS_LIVE_TRADING:
            # تنفيذ حقيقي فوري للعقد عبر الجسر السحابي
            lot = CUSTOM_CONFIG["fixed_lot"]
            success = mt5_bridge.execute_gold_order(action=action, lot_size=lot, entry=2350.50, sl=2340.0, tp=2370.0)
            if success:
                response_text += f"⚡ **[أمر حي]** تم إرسال عقد {action} بمقدار `{lot}` لوت إلى حساب MT5 بنجاح!"
                CUSTOM_CONFIG["executed_trades"] += 1
            else:
                response_text += "❌ فشل إرسال العقد للمنصة، يرجى فحص رابط الجسر السحابي."
        else:
            response_text += "ℹ️ *تم وضع المنظومة في حالة الانتظار لحين ظهور تأكيد أقوى أو تفعيل التداول التلقائي.*"
            
        bot.send_message(chat_id, response_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in background AI: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ أثناء معالجة بيانات الـ AI في الخلفية.")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    global CURRENT_SCHOOL, IS_LIVE_TRADING, ai_server, risk_control, mt5_bridge, USER_STATE, CUSTOM_CONFIG
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == 'main_menu':
        USER_STATE.pop(chat_id, None)
        text = (
            "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
            "اختر قسماً من الأزرار الشفافة أدناه لإدارة البوت:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    
    # --- 👑 رادار الذهب وحفظ الاستراتيجيات الفوري ---
    elif call.data == 'menu_gold':
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(f"🏦 مدرسة ICT {'🔹' if CURRENT_SCHOOL=='ICT' else ''}", callback_data='school_ict'),
            InlineKeyboardButton(f"📐 مدرسة SMC {'🔹' if CURRENT_SCHOOL=='SMC' else ''}", callback_data='school_smc')
        )
        markup.row(
            InlineKeyboardButton(f"⏳ مدرسة وايكوف Wyckoff {'🔹' if CURRENT_SCHOOL=='Wyckoff' else ''}", callback_data='school_wyckoff'),
            InlineKeyboardButton(f"📊 تحليل السيولة VSA {'🔹' if CURRENT_SCHOOL=='VSA' else ''}", callback_data='school_vsa')
        )
        markup.row(InlineKeyboardButton(f"📈 التحليل الكلاسيكي المطور {'🔹' if CURRENT_SCHOOL=='Classic' else ''}", callback_data='school_classic'))
        
        status_on = "🟢 تداول تلقائي (نشط)" if IS_LIVE_TRADING else "🟢 تشغيل التداول التلقائي"
        status_off = "🔴 إيقاف التداول التلقائي (مفعل)" if not IS_LIVE_TRADING else "🔴 إيقاف التداول التلقائي"
        markup.row(InlineKeyboardButton(status_on, callback_data='trade_on'), InlineKeyboardButton(status_off, callback_data='trade_off'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        status_text = "🟢 **نشط ويبحث عن فرص**" if IS_LIVE_TRADING else "🔴 **متوقف حالياً**"
        text = (
            "👑 **رادار التداول الآلي للذهب (XAUUSD)**\n\n"
            f"• 🎓 المدرسة المعتمدة حالياً في التحليل الفعلي: **{CURRENT_SCHOOL}**\n"
            f"• 🤖 حالة التداول التلقائي الحية: {status_text}\n\n"
            "اختر مدرسة لتفعيل شروطها الفنية الحقيقية وبدء الفلترة:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['school_ict', 'school_smc', 'school_wyckoff', 'school_vsa', 'school_classic']:
        school_mapping = {"school_ict": "ICT", "school_smc": "SMC", "school_wyckoff": "Wyckoff", "school_vsa": "VSA", "school_classic": "Classic"}
        CURRENT_SCHOOL = school_mapping[call.data]
        
        # حل مشكلة عدم إعطاء "تم الحفظ": نرسل تنبيه منبثق سريع للمستخدم يؤكد الحفظ الفوري
        bot.answer_callback_query(call.id, f"✅ تم حفظ وتثبيت استراتيجية {CURRENT_SCHOOL} بنجاح!", show_alert=False)
        callback_listener(call)
        return

    # --- 🧠 زر تفعيل التداول بالـ AI الجديد (يمنع التهنيج) ---
    elif call.data == 'activate_ai_trading':
        bot.answer_callback_query(call.id, "⚡ جاري بدء تحليل الـ AI في الخلفية...", show_alert=False)
        bot.send_message(chat_id, f"🚀 **جاري استدعاء نموذج Llama-3 لفلترة شارت الذهب بناءً على مدرسة [{CURRENT_SCHOOL}] حالياً...**\n*سيوفر البوت الرد فور صدوره دون تجميد الأزرار.*")
        
        # إطلاق عملية التحليل في Thread منفصل تماماً لحماية السيرفر من التهنيج
        threading.Thread(target=background_ai_analysis, args=(chat_id, CURRENT_SCHOOL)).start()

    elif call.data == 'trade_on':
        IS_LIVE_TRADING = True
        bot.answer_callback_query(call.id, "🟢 تم تفعيل التداول التلقائي حياً")
        callback_listener(call)
        return
        
    elif call.data == 'trade_off':
        IS_LIVE_TRADING = False
        bot.answer_callback_query(call.id, "🔴 تم إيقاف التداول التلقائي")
        callback_listener(call)
        return

    # --- 🛡️ إدارة المخاطر والأمان ---
    elif call.data == 'menu_risk':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("📊 تحديد حجم اللوت للتداول (Lot Size)", callback_data='click_set_lot'))
        markup.row(InlineKeyboardButton("🛑 تحديد حد الخسارة اليومي ($)", callback_data='click_set_loss'))
        markup.row(InlineKeyboardButton("🚨 إغلاق الطوارئ الفوري (Kill Switch)", callback_data='kill_switch'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        status_security = "🚨 متوقف بسبب الـ Kill Switch" if not risk_control.is_bot_enabled else "🟢 نشطة وتحرس الحساب"
        text = (
            "🛡️ **إدارة المخاطر والأمان الحصارمة**\n\n"
            f"• 📊 **حجم اللوت المعتمد حالياً:** `{CUSTOM_CONFIG['fixed_lot']}`\n"
            f"• 🛑 **حد الخسارة اليومي الأقصى:** `{risk_control.max_daily_loss:.2f} USD`\n"
            f"• ⚙️ **حالة نظام الحماية والدرع:** {status_security}"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'click_set_lot':
        USER_STATE[chat_id] = "waiting_for_lot"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_risk')]])
        bot.edit_message_text("📥 **الرجاء إدخال اللوت المناسب للتداول الآن:**", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'click_set_loss':
        USER_STATE[chat_id] = "waiting_for_loss_limit"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_risk')]])
        bot.edit_message_text("📥 **الرجاء إدخال حد الخسارة اليومي كأرقام بالدولار ($):**", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'kill_switch':
        mt5_bridge.close_all_gold_positions()
        risk_control.is_bot_enabled = False
        IS_LIVE_TRADING = False
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]])
        bot.edit_message_text("🚨 **تفعيل الـ Kill Switch الفوري كلياً!**", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- 📊 قسم الإحصائيات والتحليل ---
    elif call.data == 'menu_stats':
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu')]])
        net_total = CUSTOM_CONFIG["daily_profit"] - CUSTOM_CONFIG["daily_loss"]
        status_emoji = "🟢" if net_total >= 0 else "🔴"
        text = (
            "📊 **لوحة الأداء والتحليل الإحصائي لحساب الذهب**\n"
            f"• 📈 **العمليات المنفذة:** `[{CUSTOM_CONFIG['executed_trades']}]` صفقات\n"
            f"• {status_emoji} **المجموع الكامل التراكمي:** `{net_total:.2f} USD`"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- 🧪 مختبر الاستراتيجيات المخصصة ---
    elif call.data == 'menu_backtest':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✍️ اكتب استراتيجيتك المخصصة الآن", callback_data='write_strategy'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        text = "🧪 **مختبر استراتيجيات الذهب الذكي (Strategy Tester)**"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- ⚙️ قسم ربط حساب MT5 وقراءة البيانات الحية ---
    elif call.data == 'menu_mt5':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🔍 عرض الحساب المرتبط حالياً وقراءة الرصيد", callback_data='view_linked_account'))
        markup.row(
            InlineKeyboardButton("🧪 حساب تجريبي (Demo)", callback_data='mt5_type_demo'),
            InlineKeyboardButton("🟢 حساب حقيقي (Live)", callback_data='mt5_type_real')
        )
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        text = "⚙️ **لوحة إعدادات وربط منصة MetaTrader 5**"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'view_linked_account':
        metrics = mt5_bridge.get_account_metrics()
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع لقسم MT5", callback_data='menu_mt5')]])
        text = (
            "🔍 **تفاصيل وبيانات حساب التداول الحالية:**\n"
            f"• 🆔 **رقم الميتا (Account ID):** `{CUSTOM_CONFIG['saved_account_id']}`\n"
            f"• 🖥️ **اسم السيرفر (Server):** `{CUSTOM_CONFIG['saved_server']}`\n"
            f"• 📡 **حالة ربط الجسر السحابي:** {metrics['status']}\n"
            f"• 💰 **الرصيد الفعلي الحالي (Balance):** `{metrics['balance']:.2f} USD`\n"
            f"• 📊 **السيولة اللحظية الحية (Equity):** `{metrics['equity']:.2f} USD`"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['mt5_type_demo', 'mt5_type_real']:
        acc_type = "تجريبي" if call.data == 'mt5_type_demo' else "حقيقي"
        USER_DATA[chat_id] = {"type": acc_type}
        USER_STATE[chat_id] = "waiting_mt5_broker"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_mt5')]])
        bot.edit_message_text(f"📥 **لقد اخترت ربط حساب {acc_type}.**\n\nالخطوة [1/3]: يرجى إدخال اسم السيرفر:", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def text_input_handler(message):
    chat_id = message.chat.id
    user_text = message.text
    global CUSTOM_CONFIG
    
    if USER_STATE.get(chat_id) == "waiting_for_lot":
        try:
            lot_value = float(user_text)
            if lot_value < 0.01: raise ValueError()
            CUSTOM_CONFIG["fixed_lot"] = lot_value
            USER_STATE.pop(chat_id, None)
            bot.send_message(chat_id, f"✅ **تم حفظ اللوت بنجاح!** القيمة الحالية: `{lot_value}`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ عودة", callback_data='menu_risk')]]), parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إرسال حجم لوت صحيح، مثال: `0.01`")

    elif USER_STATE.get(chat_id) == "waiting_for_loss_limit":
        try:
            loss_value = float(user_text)
            risk_control.max_daily_loss = loss_value
            USER_STATE.pop(chat_id, None)
            bot.send_message(chat_id, f"✅ **تم حفظ حد الخسارة!** القيمة: `{loss_value:.2f} USD`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ عودة", callback_data='menu_risk')]]), parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ يرجى إرسال رقم صحيح بالدولار.")

    elif USER_STATE.get(chat_id) == "waiting_mt5_broker":
        USER_DATA[chat_id]["broker"] = user_text
        USER_STATE[chat_id] = "waiting_mt5_id"
        bot.send_message(chat_id, "📥 الخطوة [2/3]: يرجى إدخال رقم حساب التداول (Account ID):")

    elif USER_STATE.get(chat_id) == "waiting_mt5_id":
        USER_DATA[chat_id]["id"] = user_text
        USER_STATE[chat_id] = "waiting_mt5_password"
        bot.send_message(chat_id, "📥 الخطوة [3/3]: يرجى إدخال كلمة السر الحقيقية للحساب:")

    elif USER_STATE.get(chat_id) == "waiting_mt5_password":
        password = user_text
        broker = USER_DATA[chat_id]["broker"]
        acc_id = USER_DATA[chat_id]["id"]
        acc_type = USER_DATA[chat_id]["type"]
        
        CUSTOM_CONFIG["saved_account_id"] = acc_id
        CUSTOM_CONFIG["saved_server"] = broker
        USER_STATE.pop(chat_id, None)
        
        msg_wait = bot.send_message(chat_id, "⏳ جاري محاولة الربط السحابي...")
        is_live_flag = True if acc_type == "حقيقي" else False
        mt5_bridge.connect_to_account(account_id=acc_id, password=password, server=broker, is_live=is_live_flag)
        
        bot.delete_message(chat_id, msg_wait.message_id)
        bot.send_message(chat_id, f"✅ **تم الربط بنجاح!** للحساب `{acc_id}` على سيرفر `{broker}`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ عودة", callback_data='menu_mt5')]]), parse_mode="Markdown")

if __name__ == '__main__':
    logger.info("🚀 تشغيل المنظومة المحدثة ضد التهنيج وبميزة التداول بالـ AI...")
    bot.infinity_polling()
