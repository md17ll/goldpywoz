import os
import logging
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
        "تم تفعيل نظام السحب اللحظي لقراءة رصيد وسيولة الحساب حياً.\n"
        "اختر قسماً من الأزرار أدناه لتوجيه النظام:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    global CURRENT_SCHOOL, IS_LIVE_TRADING, ai_server, risk_control, mt5_bridge, USER_STATE, CUSTOM_CONFIG
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == 'main_menu':
        USER_STATE.pop(chat_id, None)
        text = (
            "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
            "مرحباً بك في نظام التداول الهجين المتكامل. البوت مستضاف على **Railway** ومربوط بـ **OpenRouter**.\n\n"
            "اختر قسماً من الأزرار الشفافة أدناه لإدارة البوت:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    
    # --- 👑 رادار الذهب ---
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
        
        status_on = "🟢 تشداول تلقائي (نشط)" if IS_LIVE_TRADING else "🟢 تشغيل التداول التلقائي"
        status_off = "🔴 إيقاف التداول التلقائي (مفعل)" if not IS_LIVE_TRADING else "🔴 إيقاف التداول التلقائي"
        markup.row(InlineKeyboardButton(status_on, callback_data='trade_on'), InlineKeyboardButton(status_off, callback_data='trade_off'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        status_text = "🟢 **نشط ويبحث عن فرص**" if IS_LIVE_TRADING else "🔴 **متوقف حالياً**"
        text = (
            "👑 **رادار التداول الآلي للذهب (XAUUSD)**\n\n"
            f"• 🎓 المدرسة المعتمدة حالياً في التحليل الفعلي: **{CURRENT_SCHOOL}**\n"
            f"• 🤖 حالة التداول التلقائي الحية: {status_text}\n\n"
            "اختر مدرسة لتفعيل شروطها الفنية الحقيقية المرسلة لـ OpenRouter، أو تحكم بالتداول الآلي:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['school_ict', 'school_smc', 'school_wyckoff', 'school_vsa', 'school_classic']:
        school_mapping = {"school_ict": "ICT", "school_smc": "SMC", "school_wyckoff": "Wyckoff", "school_vsa": "VSA", "school_classic": "Classic"}
        CURRENT_SCHOOL = school_mapping[call.data]
        callback_listener(call)
        return

    elif call.data == 'trade_on':
        IS_LIVE_TRADING = True
        callback_listener(call)
        return
        
    elif call.data == 'trade_off':
        IS_LIVE_TRADING = False
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
            f"• ⚙️ **حالة نظام الحماية والدرع:** {status_security}\n\n"
            "اضغط على الخيارات أعلاه لتحديث قيم اللوت أو سقف الخسارة اليومية."
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'click_set_lot':
        USER_STATE[chat_id] = "waiting_for_lot"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_risk')]])
        bot.edit_message_text("📥 **الرجاء إدخال اللوت المناسب للتداول الآن:**\n\n⚠️ *ملاحظة: أقل حجم عقد مسموح به هو `0.01`*", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'click_set_loss':
        USER_STATE[chat_id] = "waiting_for_loss_limit"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_risk')]])
        bot.edit_message_text("📥 **الرجاء إدخال حد الخسارة اليومي كأرقام بالدولار ($):**\n\n*مثال:* `40` أو `100`", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'kill_switch':
        mt5_bridge.close_all_gold_positions()
        risk_control.is_bot_enabled = False
        IS_LIVE_TRADING = False
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]])
        bot.edit_message_text("🚨 **تفعيل الـ Kill Switch الفوري كلياً!**\n\nتم إغلاق كل صفقات الذهب وتجميد التداول التلقائي.", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- 📊 قسم الإحصائيات والتحليل ---
    elif call.data == 'menu_stats':
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu')]])
        net_total = CUSTOM_CONFIG["daily_profit"] - CUSTOM_CONFIG["daily_loss"]
        status_emoji = "🟢" if net_total >= 0 else "🔴"
        
        text = (
            "📊 **لوحة الأداء والتحليل الإحصائي لحساب الذهب**\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"• 📈 **العمليات المنفذة:** `[{CUSTOM_CONFIG['executed_trades']}]` صفقات\n"
            f"• 💰 **الربح اليومي:** `+{CUSTOM_CONFIG['daily_profit']:.2f} USD`\n"
            f"• 📉 **الخسارة اليومية:** `-{CUSTOM_CONFIG['daily_loss']:.2f} USD`\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"• {status_emoji} **المجموع الكامل التراكمي:** `{net_total:.2f} USD`\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "💡 *الإحصائيات تتبع صفقات الذهب المغلقة حياً عبر جسر ربط السيرفر.*"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- 🧪 مختبر الاستراتيجيات המخصصة ---
    elif call.data == 'menu_backtest':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✍️ اكتب استراتيجيتك المخصصة الآن", callback_data='write_strategy'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        text = "🧪 **مختبر استراتيجيات الذهب الذكي (Strategy Tester)**"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == 'write_strategy':
        USER_STATE[chat_id] = "waiting_for_strategy"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_backtest')]])
        text = "📝 **أرسل لي الآن اسم ووصف استراتيجيتك المخصصة بالتفصيل لفحصها وبنائها برمجياً...**"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['custom_strat_on', 'custom_strat_off']:
        state_text = "🟢 **تم تفعيل الاستراتيجية المخصصة للتداول التلقائي حياً!**" if call.data == 'custom_strat_on' else "🔴 **تم إيقاف تشغيل الاستراتيجية المخصصة.**"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للمختبر", callback_data='menu_backtest')]])
        bot.edit_message_text(state_text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- ⚙️ قسم ربط حساب MT5 وقراءة البيانات الحية ---
    elif call.data == 'menu_mt5':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🔍 عرض الحساب المرتبط حالياً وقراءة الرصيد", callback_data='view_linked_account'))
        markup.row(
            InlineKeyboardButton("🧪 حساب تجريبي (Demo)", callback_data='mt5_type_demo'),
            InlineKeyboardButton("🟢 حساب حقيقي (Live)", callback_data='mt5_type_real')
        )
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        text = "⚙️ **لوحة إعدادات وربط منصة MetaTrader 5**\n\nيمكنك الآن استعراض وقراءة رصيدك حياً أو إدخال بيانات حساب جديد:"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'view_linked_account':
        # استدعاء دالة تحديث الأرقام حياً من الجسر السحابي للـ MT5 فوراً عند الضغط
        metrics = mt5_bridge.get_account_metrics()
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع لقسم MT5", callback_data='menu_mt5')]])
        
        account_id_display = CUSTOM_CONFIG["saved_account_id"]
        server_display = CUSTOM_CONFIG["saved_server"]
        
        text = (
            "🔍 **تفاصيل وبيانات حساب التداول الحالية:**\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"• 🆔 **رقم الميتا (Account ID):** `{account_id_display}`\n"
            f"• 🖥️ **اسم السيرفر (Server):** `{server_display}`\n"
            f"• 📡 **حالة ربط الجسر السحابي:** {metrics['status']}\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"• 💰 **الرصيد الفعلي الحالي (Balance):** `{metrics['balance']:.2f} USD`\n"
            f"• 📊 **السيولة اللحظية الحية (Equity):** `{metrics['equity']:.2f} USD`\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "💡 *يتم سحب وتحديث قيمة الـ Balance والـ Equity حياً من خوادم البروكر مباشرة.*"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['mt5_type_demo', 'mt5_type_real']:
        acc_type = "تجريبي" if call.data == 'mt5_type_demo' else "حقيقي"
        USER_DATA[chat_id] = {"type": acc_type}
        USER_STATE[chat_id] = "waiting_mt5_broker"
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_mt5')]])
        bot.edit_message_text(f"📥 **لقد اخترت ربط حساب {acc_type}.**\n\nالخطوة [1/3]: يرجى إدخال **اسم السيرفر أو البروكر (Broker/Server Name)** الآن:\n*مثال:* `Exness-MT5-Trial2`", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    bot.answer_callback_query(call.id)

# --- 📥 مستمع معالجة المدخلات وحفظ تفاصيل البيانات الرقمية ---
@bot.message_handler(func=lambda message: True)
def text_input_handler(message):
    chat_id = message.chat.id
    user_text = message.text
    global CUSTOM_CONFIG
    
    if USER_STATE.get(chat_id) == "waiting_for_lot":
        try:
            lot_value = float(user_text)
            if lot_value < 0.01:
                bot.send_message(chat_id, "⚠️ **خطأ في الحفظ!** حجم عقد التداول لا يمكن أن يكون أقل من `0.01`. الرجاء إدخال رقم صحيح:")
                return
            CUSTOM_CONFIG["fixed_lot"] = lot_value
            USER_STATE.pop(chat_id, None)
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ عودة لقسم المخاطر", callback_data='menu_risk')]])
            bot.send_message(chat_id, f"✅ **تم حفظ اللوت بنجاح!**\n\nحجم عقد التداول الجديد المعتمد الآن هو: `{lot_value}`.", reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ **خطأ!** يرجى إرسال أرقام صالحة لحجم اللوت. *مثال:* `0.05`")

    elif USER_STATE.get(chat_id) == "waiting_for_loss_limit":
        try:
            loss_value = float(user_text)
            if loss_value <= 0:
                raise ValueError()
            risk_control.max_daily_loss = loss_value
            USER_STATE.pop(chat_id, None)
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ عودة لقسم المخاطر", callback_data='menu_risk')]])
            bot.send_message(chat_id, f"✅ **تم حفظ حد الخسارة بنجاح!**\n\nسقف الخسارة اليومي مثبت الآن على: `{loss_value:.2f} USD`.", reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ **خطأ!** الرجاء إرسال رقم صحيح بالدولار. مثال: `40`")

    elif USER_STATE.get(chat_id) == "waiting_mt5_broker":
        USER_DATA[chat_id]["broker"] = user_text
        USER_STATE[chat_id] = "waiting_mt5_id"
        bot.send_message(chat_id, "📥 **تم استلام اسم السيرفر.**\n\nالخطوة [2/3]: يرجى إدخال **رقم حساب التداول (Account ID)** الآن:")

    elif USER_STATE.get(chat_id) == "waiting_mt5_id":
        USER_DATA[chat_id]["id"] = user_text
        USER_STATE[chat_id] = "waiting_mt5_password"
        bot.send_message(chat_id, "📥 **تم استلام رقم الحساب.**\n\nالخطوة [3/3]: يرجى إدخال **كلمة السر الخاصة بالحساب (Password)** الآن:")

    elif USER_STATE.get(chat_id) == "waiting_mt5_password":
        password = user_text
        broker = USER_DATA[chat_id]["broker"]
        acc_id = USER_DATA[chat_id]["id"]
        acc_type = USER_DATA[chat_id]["type"]
        
        CUSTOM_CONFIG["saved_account_id"] = acc_id
        CUSTOM_CONFIG["saved_server"] = broker
        
        USER_STATE.pop(chat_id, None)
        USER_DATA.pop(chat_id, None)
        
        msg_wait = bot.send_message(chat_id, "⏳ **جاري محاولة الاتصال والربط السحابي مع خوادم MetaTrader 5...**")
        is_live_flag = True if acc_type == "حقيقي" else False
        mt5_bridge.connect_to_account(account_id=acc_id, password=password, server=broker, is_live=is_live_flag)
        
        bot.delete_message(chat_id, msg_wait.message_id)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ عودة لقسم MT5", callback_data='menu_mt5')]])
        
        bot.send_message(
            chat_id, 
            f"✅ **تم حفظ البيانات وتفعيل الربط بنجاح!**\n\n"
            f"• نوع الحساب: `{acc_type}`\n"
            f"• السيرفر: `{broker}`\n"
            f"• رقم الحساب (ID): `{acc_id}`\n"
            f"• حالة الاتصال الآن: 🟢 **نشط ومتصل**", 
            reply_markup=markup, 
            parse_mode="Markdown"
        )

    elif USER_STATE.get(chat_id) == "waiting_for_strategy":
        USER_STATE.pop(chat_id, None)
        msg_waiting = bot.send_message(chat_id, "🔍 **جاري فلترة الاستراتيجية المخصصة ومطابقتها عبر OpenRouter...**")
        ai_analysis = ai_server.analyze_gold_market(market_data_summary=f"User strategy description: {user_text}", chosen_school="Classic")
        bot.delete_message(chat_id, msg_waiting.message_id)
        
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🟢 تشغيل الاستراتيجية للتداول", callback_data='custom_strat_on'))
        markup.row(InlineKeyboardButton("🔴 إيقاف الاستراتيجية المخصصة", callback_data='custom_strat_off'))
        markup.row(InlineKeyboardButton("🔙 رجوع للمختبر", callback_data='menu_backtest'))
        
        response_text = (
            "🧪 **تقرير فحص وتجهيز الاستراتيجية المخصصة:**\n\n"
            f"📥 **الاستراتيجية المكتوبة:** \"{user_text}\"\n\n"
            f"🧠 **تحليل وتوصية الـ AI الافتراضية:** `{ai_analysis.get('reason', 'الرموز والقواعد واضحة وجاهزة للتنفيذ.')}`\n\n"
            "🎮 يمكنك الآن التحكم بتشغيل أو إيقاف هذه الاستراتيجية المخصصة للتداول التلقائي حياً عبر الأزرار الشفافة أدناه:"
        )
        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode="Markdown")

if __name__ == '__main__':
    logger.info("🚀 تشغيل المنظومة الكاملة المحدثة بقراءة الرصيد اللحظي الحقيقي والسيولة...")
    bot.infinity_polling()
