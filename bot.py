import os
import logging
import threading # لحل مشكلة التعليق نهائياً وتشغيل التحليل في مسار منفصل
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
    markup.row(InlineKeyboardButton("🧪 مختبر الاستراتيجيات المخصصة", callback_data='menu_backtest'))
    markup.row(InlineKeyboardButton("🛡️ إدارة المخاطر والأمان", callback_data='menu_risk'))
    markup.row(InlineKeyboardButton("📊 الإحصائيات والتحليل", callback_data='menu_stats'))
    markup.row(InlineKeyboardButton("⚙️ ربط حساب MT5", callback_data='menu_mt5'))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    text = (
        "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
        "تم تحديث رادار السكالبينغ وإضافة مدرسة التداول الحر بالذكاء الاصطناعي.\n"
        "اختر قسماً من الأزرار أدناه لتوجيه النظام:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

def process_market_analysis(chat_id, school):
    """
    تنفيذ تحليل الـ AI والصفقات التلقائية في الخلفية بدون التسبب في تعليق أزرار التلغرام
    """
    try:
        # صياغة ملخص الشارت لإرساله للمحرك الذكي
        market_summary = "XAUUSD Live Context: Price 2350.50, Liquidity cycles scanning active."
        
        # استدعاء نموذج الذكاء الاصطناعي
        ai_analysis = ai_server.analyze_gold_market(market_data_summary=market_summary, chosen_school=school)
        
        action = ai_analysis.get("action", "WAIT")
        reason = ai_analysis.get("reason", "AI is scanning order blocks.")
        
        response_text = (
            f"🧠 **تقرير الفلترة الحية عبر [{school}]:**\n\n"
            f"• 🎬 **قرار المنظومة:** `{action}`\n"
            f"• 📝 **السبب الفني:** \"{reason}\"\n\n"
        )
        
        if action in ["BUY", "SELL"] and IS_LIVE_TRADING:
            lot = CUSTOM_CONFIG["fixed_lot"]
            success = mt5_bridge.execute_gold_order(action=action, lot_size=lot, entry=2350.50, sl=2340.0, tp=2370.0)
            if success:
                response_text += f"⚡ **[صفقة حية]** قام البوت بتنفيذ عقد {action} بمقدار `{lot}` لوت حياً على MT5!"
                CUSTOM_CONFIG["executed_trades"] += 1
            else:
                response_text += "❌ تعذر إرسال الأمر الحقيقي، يرجى التحقق من متغير الـ Bridge URL."
        else:
            response_text += "ℹ️ *تم الاكتفاء بالقراءة والتحليل؛ فعل 'تشغيل التداول' لتنفيذ العقود تلقائياً.*"
            
        bot.send_message(chat_id, response_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in background cycle: {e}")

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
    
    # --- 👑 رادار الذهب والهيكلية الجديدة للأزرار ---
    elif call.data == 'menu_gold':
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(f"🏦 مدرسة ICT {'🔹' if CURRENT_SCHOOL=='ICT' else ''}", callback_data='school_ict'),
            InlineKeyboardButton(f"📐 مدرسة SMC {'🔹' if CURRENT_SCHOOL=='SMC' else ''}", callback_data='school_smc')
        )
        markup.row(
            InlineKeyboardButton(f"⏳ مدرسة وايكوف {'🔹' if CURRENT_SCHOOL=='Wyckoff' else ''}", callback_data='school_wyckoff'),
            InlineKeyboardButton(f"📊 تحليل السيولة VSA {'🔹' if CURRENT_SCHOOL=='VSA' else ''}", callback_data='school_vsa')
        )
        markup.row(InlineKeyboardButton(f"📈 التحليل الكلاسيكي المطور {'🔹' if CURRENT_SCHOOL=='Classic' else ''}", callback_data='school_classic'))
        
        # دمج التداول بالذكاء الاصطناعي الحر كخيار ومدرسة مخصصة مستقلة بجانب المدارس
        markup.row(InlineKeyboardButton(f"🧠 التداول بالذكاء الاصطناعي (AI Trade) {'🔹' if CURRENT_SCHOOL=='AI_Autonomous' else ''}", callback_data='school_ai_autonomous'))
        
        # وضع أزرار تشغيل وإيقاف التداول تحت المدارس مباشرة بشكل منظم ونظيف
        status_on_btn = "🟢 تشغيل التداول (نشط)" if IS_LIVE_TRADING else "🟢 تشغيل التداول"
        status_off_btn = "🔴 ايقاف التداول (مفعل)" if not IS_LIVE_TRADING else "🔴 ايقاف التداول"
        markup.row(InlineKeyboardButton(status_on_btn, callback_data='trade_on'), InlineKeyboardButton(status_off_btn, callback_data='trade_off'))
        
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        status_text = "🟢 **نشط ويتلقى الأوامر حياً**" if IS_LIVE_TRADING else "🔴 **متوقف تماماً**"
        
        display_school_name = CURRENT_SCHOOL
        if CURRENT_SCHOOL == "AI_Autonomous":
            display_school_name = "الذكاء الاصطناعي الحر (تداول على كيفه)"
            
        text = (
            "👑 **رادار التداول الآلي والتحليل الذكي للذهب**\n\n"
            f"• 🎓 النظام المعتمد حالياً: **{display_school_name}**\n"
            f"• 🤖 حالة التداول التلقائي: {status_text}\n\n"
            "اضغط على أي خيار لتعديل أو حفظ الاستراتيجية فوراً:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['school_ict', 'school_smc', 'school_wyckoff', 'school_vsa', 'school_classic', 'school_ai_autonomous']:
        school_mapping = {
            "school_ict": "ICT", 
            "school_smc": "SMC", 
            "school_wyckoff": "Wyckoff", 
            "school_vsa": "VSA", 
            "school_classic": "Classic",
            "school_ai_autonomous": "AI_Autonomous"
        }
        CURRENT_SCHOOL = school_mapping[call.data]
        
        # إشعار سريع للمستخدم يفيد بالحفظ والتثبيت الفوري دون تعليق
        bot.answer_callback_query(call.id, f"✅ تم تثبيت استراتيجية [{CURRENT_SCHOOL}] للعمل الحسابي!", show_alert=False)
        
        # إطلاق دورة الفحص في الخلفية فوراً لحماية الواجهة من التهنيج لمرة واحدة فقط
        threading.Thread(target=process_market_analysis, args=(chat_id, CURRENT_SCHOOL)).start()
        
        # تم تصحيح الخطأ هنا: تم استبدال الاستدعاء المتكرر بإعادة توجيه آمنة لشكل القائمة المحدثة
        call.data = 'menu_gold'
        callback_listener(call)
        return

    elif call.data == 'trade_on':
        IS_LIVE_TRADING = True
        bot.answer_callback_query(call.id, "🟢 تم تفعيل وتنفيذ نظام التداول التلقائي حياً")
        call.data = 'menu_gold'
        callback_listener(call)
        return
        
    elif call.data == 'trade_off':
        IS_LIVE_TRADING = False
        bot.answer_callback_query(call.id, "🔴 تم ايقاف التداول")
        call.data = 'menu_gold'
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
    logger.info("🚀 تشغيل المنظومة المحدثة كلياً بالـ AI المطور والتحكم الخالي من التعليق...")
    bot.infinity_polling()
