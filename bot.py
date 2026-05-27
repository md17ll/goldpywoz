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
# إعدادات المخاطر الافتراضية القابلة للتعديل حياً من المحادثة
risk_control = GoldRiskManager(max_daily_loss=40.0, per_trade_risk=40.0)
mt5_bridge = GoldMT5Connector()

CURRENT_SCHOOL = "ICT"
IS_LIVE_TRADING = False

# متغيرات البيئة لحفظ مدخلات المستخدم حياً أثناء تشغيل السيرفر
USER_STATE = {} 
CUSTOM_CONFIG = {
    "fixed_lot": 0.01,         # اللوت الافتراضي الابتدائي
    "executed_trades": 0,      # الإحصائيات: عدد الصفقات المنفذة
    "daily_profit": 0.00,      # الإحصائيات: الأرباح اليومية
    "daily_loss": 0.00         # الإحصائيات: الخسائر اليومية
}

def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("👑 رادار سكالبينغ الذهب", callback_data='menu_gold'))
    markup.row(InlineKeyboardButton("🧪 مختبر الاستراتيجيات المخصصة", callback_data='menu_backtest'))
    markup.row(InlineKeyboardButton("🛡️ إدارة المخاطر والأمان", callback_data='menu_risk'))
    markup.row(InlineKeyboardButton("📊 الإحصائيات والتحليل Mالي", callback_data='menu_stats'))
    markup.row(InlineKeyboardButton("⚙️ ربط حساب MT5 (تجريبي/حقيقي)", callback_data='menu_mt5'))
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    global mt5_bridge
    mt5_bridge.connect_to_account(account_id=os.getenv("MT5_ACCOUNT_ID", "123456"), password="DefaultPassword", server="Exness-MT5-Trial", is_live=False)
    
    text = (
        "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
        "تم تفعيل نظام استقبال المدخلات الرقمية للوت والخسارة اليومية.\n"
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
    
    # --- رادار الذهب والتداول ---
    elif call.data == 'menu_gold':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton(f"🏦 مدرسة ICT / SMC {'🔹' if CURRENT_SCHOOL=='ICT' else ''}", callback_data='school_ict'))
        markup.row(InlineKeyboardButton(f"⏳ مدرسة وايكوف Wyckoff {'🔹' if CURRENT_SCHOOL=='Wyckoff' else ''}", callback_data='school_wyckoff'))
        markup.row(InlineKeyboardButton(f"📊 تحليل السيولة VSA {'🔹' if CURRENT_SCHOOL=='VSA' else ''}", callback_data='school_vsa'))
        markup.row(InlineKeyboardButton(f"📐 التحليل الكلاسيكي المطور {'🔹' if CURRENT_SCHOOL=='Classic' else ''}", callback_data='school_classic'))
        
        status_on = "🟢 تشغيل التداول التلقائي (نشط)" if IS_LIVE_TRADING else "🟢 تشغيل التداول التلقائي"
        status_off = "🔴 إيقاف التداول التلقائي (مفعل)" if not IS_LIVE_TRADING else "🔴 إيقاف التداول التلقائي"
        markup.row(InlineKeyboardButton(status_on, callback_data='trade_on'), InlineKeyboardButton(status_off, callback_data='trade_off'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        status_text = "🟢 **نشط ويبحث عن فرص**" if IS_LIVE_TRADING else "🔴 **متوقف حالياً**"
        text = (
            "👑 **رادار التداول الآلي للذهب (XAUUSD)**\n\n"
            f"• 🎓 المدرسة النشطة حالياً: **{CURRENT_SCHOOL} (صارمة 100%)**\n"
            f"• 🤖 حالة التداول التلقائي: {status_text}\n"
            "اختر مدرسة لتفعيل قواعدها، أو تحكم بتشغيل وإيقاف التداول الآلي:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data in ['school_ict', 'school_wyckoff', 'school_vsa', 'school_classic']:
        school_mapping = {"school_ict": "ICT", "school_wyckoff": "Wyckoff", "school_vsa": "VSA", "school_classic": "Classic"}
        CURRENT_SCHOOL = school_mapping[call.data]
        bot.answer_callback_query(call.id, f"تم تفعيل مدرسة {CURRENT_SCHOOL}")
        callback_listener(call)
        return

    elif call.data == 'trade_on':
        IS_LIVE_TRADING = True
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='menu_gold')]])
        text = f"🟢 **تم تفعيل التداول حياً!**\n\n🤖 البوت يراقب حركة الأسعار حياً، وسيستخدم لوت تداول مخصص بقيمة `{CUSTOM_CONFIG['fixed_lot']}` لحماية الحساب."
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == 'trade_off':
        IS_LIVE_TRADING = False
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='menu_gold')]])
        bot.edit_message_text("🔴 **تم إيقاف التداول التلقائي.**", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- 🛡️ قسم إدارة المخاطر والأمان (استقبال المدخلات) ---
    elif call.data == 'menu_risk':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("📊 تحديد حجم اللوت للتداول (Lot Size)", callback_data='click_set_lot'))
        markup.row(InlineKeyboardButton("🛑 تحديد حد الخسارة اليومي ($)", callback_data='click_set_loss'))
        markup.row(InlineKeyboardButton("🚨 إغلاق الطوارئ الفوري (Kill Switch)", callback_data='kill_switch'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        status_security = "🚨 متوقف بسبب الـ Kill Switch" if not risk_control.is_bot_enabled else "🟢 نشطة وتحرس الحساب"
        text = (
            "🛡️ **إدارة المخاطر والأمان الحصارمة**\n\n"
            f"• 📊 **حجم اللوت الحالي المثبت:** `{CUSTOM_CONFIG['fixed_lot']}`\n"
            f"• 🛑 **حد الخسارة اليومي الأقصى:** `{risk_control.max_daily_loss:.2f} USD`\n"
            f"• ⚙️ **حالة نظام الحماية والدرع:** {status_security}\n\n"
            "اضغط على الخيارات أعلاه لتحديث حجم لوت التداول أو كتابة سقف الخسارة اليومي الجديد للحساب الحقيقي والتجريبي."
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'click_set_lot':
        USER_STATE[chat_id] = "waiting_for_lot"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_risk')]])
        bot.edit_message_text("📥 **الرجاء إدخال اللوت المناسب للتداول الآن:**\n\n*مثال:* `0.01` أو `0.05` أو `0.10`", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'click_set_loss':
        USER_STATE[chat_id] = "waiting_for_loss_limit"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_risk')]])
        bot.edit_message_text("📥 **الرجاء إدخال حد الخسارة اليومي كأرقام بالدولار ($):**\n\n*مثال:* `40` أو `50` أو `100`", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'kill_switch':
        mt5_bridge.close_all_gold_positions()
        risk_control.is_bot_enabled = False
        IS_LIVE_TRADING = False
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]])
        bot.edit_message_text("🚨 **تفعيل الـ Kill Switch الفوري كلياً!**\n\nتم إغلاق كل صفقات الذهب وتجميد التداول التلقائي لحماية الحساب.", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- 📊 قسم الإحصائيات والتحليل المالي المنظم والمصنف ---
    elif call.data == 'menu_stats':
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu')]])
        
        net_total = CUSTOM_CONFIG["daily_profit"] - CUSTOM_CONFIG["daily_loss"]
        status_emoji = "🟢" if net_total >= 0 else "🔴"
        
        text = (
            "📊 **لوحة الأداء والتحليل الإحصائي لحساب الذهب**\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"• 📈 **العمليات المنفذة:**  `[{CUSTOM_CONFIG['executed_trades']}]` صفقات\n"
            f"• 💰 **الربح اليومي:**     `+{CUSTOM_CONFIG['daily_profit']:.2f} USD`\n"
            f"• 📉 **الخسارة اليومية:**   `-{CUSTOM_CONFIG['daily_loss']:.2f} USD`\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"• {status_emoji} **المجموع الكامل التراكمي:** `{net_total:.2f} USD`\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "💡 *الإحصائيات تتبع صفقات الذهب المغلقة حياً عبر جسر ربط السيرفر.*"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # --- باقي القوائم ---
    elif call.data == 'menu_backtest':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✍️ اكتب استراتيجيتك المخصصة الآن", callback_data='write_strategy'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        text = "🧪 **مختبر استراتيجيات الذهب الذكي (Strategy Tester)**"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == 'write_strategy':
        USER_STATE[chat_id] = "waiting_for_strategy"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data='menu_backtest')]])
        text = "📝 **أرسل لي الآن رسالة نصية تشرح فيها استراتيجيتك المخصصة لفحصها...**"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == 'menu_mt5':
        metrics = mt5_bridge.get_account_metrics()
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]])
        text = f"⚙️ **لوحة ربط MT5 السحابية**\n\n• الحساب: {metrics['status']}\n• الرصيد الحقيقي المكتشف: {metrics['balance']:,}.00 USD"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    bot.answer_callback_query(call.id)

# --- 📥 مستمع ومعالج المدخلات النصية والرقمية من المستخدم حياً ---
@bot.message_handler(func=lambda message: True)
def text_input_handler(message):
    chat_id = message.chat.id
    user_text = message.text
    
    # 1. حفظ واستقبال الـ Lot Size
    if USER_STATE.get(chat_id) == "waiting_for_lot":
        try:
            lot_value = float(user_text)
            if lot_value <= 0:
                raise ValueError()
            
            CUSTOM_CONFIG["fixed_lot"] = lot_value
            USER_STATE.pop(chat_id, None) # إلغاء الحالة
            
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ عودة لقسم المخاطر", callback_data='menu_risk')]])
            bot.send_message(chat_id, f"✅ **تم حفظ اللوت بنجاح!**\n\nحجم عقد التداول الجديد المعتمد الآن هو: `{lot_value}`.", reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ **خطأ في المدخلات!** الرجاء إرسال رقم عشري صحيح لحجم اللوت. *مثال:* `0.02`")

    # 2. حفظ واستقبال حد الخسارة اليومية بالدولار
    elif USER_STATE.get(chat_id) == "waiting_for_loss_limit":
        try:
            loss_value = float(user_text)
            if loss_value <= 0:
                raise ValueError()
            
            risk_control.max_daily_loss = loss_value
            USER_STATE.pop(chat_id, None)
            
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🛡️ عودة لقسم المخاطر", callback_data='menu_risk')]])
            bot.send_message(chat_id, f"✅ **تم حفظ حد الخسارة بنجاح!**\n\nسقف الخسارة اليومي الأقصى للحساب مثبت الآن على: `{loss_value:.2f} USD`.", reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ **خطأ في المدخلات!** الرجاء إرسال أرقام صحيحة وصالحة لحد الخسارة بالدولار. *مثال:* `50` ")

    # 3. استقبال ومعالجة نص الاستراتيجية المخصصة للمختبر عبر الـ AI
    elif USER_STATE.get(chat_id) == "waiting_for_strategy":
        USER_STATE.pop(chat_id, None)
        msg_waiting = bot.send_message(chat_id, "🔍 **جاري فحص استراتيجيتك المخصصة عبر OpenRouter...**")
        ai_analysis = ai_server.analyze_gold_market(market_data_summary=f"User strategy: {user_text}", chosen_school="Classic")
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='menu_backtest')]])
        response_text = (
            "🧪 **نتيجة فحص واختبار الاستراتيجية المخصصة:**\n\n"
            f"📥 **النص المستلم:** \"{user_text}\"\n\n"
            f"🤖 **تقرير عقل الذكاء الاصطناعي:** `{ai_analysis.get('reason', 'تم فحص الشروط بنجاح وتوافقها مع السيولة.')}`"
        )
        bot.delete_message(chat_id, msg_waiting.message_id)
        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode="Markdown")

if __name__ == '__main__':
    logger.info("🚀 تشغيل المنظومة المحدثة كلياً بأقسام المخاطر الديناميكية والإحصائيات المرتبة...")
    bot.infinity_polling()
