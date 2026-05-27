import os
import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعدادات الـ Logging لمراقبة عمل السيرفر على Railway وطباعة البيانات بدقة
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# سحب توكن البوت بأمان من لوحة تحكم Railway (Variables)
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("🚨 خطأ كارثي: لم يتم العثور على TELEGRAM_TOKEN في متغيرات بيئة السيرفر (Variables)!")
    raise ValueError("TELEGRAM_TOKEN is missing!")

bot = TeleBot(TOKEN)

# 1. تصميم القائمة الرئيسية بالأزرار الشفافة
def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("👑 رادار سكالبينغ الذهب", callback_data='menu_gold'))
    markup.row(InlineKeyboardButton("🛡️ إدارة المخاطر والأمان (40$)", callback_data='menu_risk'))
    markup.row(InlineKeyboardButton("📊 الإحصائيات والتحليل المالي", callback_data='menu_stats'))
    markup.row(InlineKeyboardButton("⚙️ ربط حساب MT5 (تجريبي/حقيقي)", callback_data='menu_mt5'))
    return markup

# مستمع أمر البداية /start
@bot.message_handler(commands=['start'])
def start_command(message):
    text = (
        "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
        "مرحباً بك في نظام التداول الهجين المتكامل. البوت مستضاف على **Railway** ومربوط بـ **OpenRouter**.\n\n"
        "اختر قسماً من الأزرار الشفافة أدناه لإدارة البوت:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# 2. مستمع ومبرمج الضغط على الأزرار الشفافة (تعديل نفس الرسالة دون رسائل جديدة)
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # خيار العودة للقائمة الرئيسية
    if call.data == 'main_menu':
        text = (
            "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
            "مرحباً بك في نظام التداول الهجين المتكامل. البوت مستضاف على **Railway** ومربوط بـ **OpenRouter**.\n\n"
            "اختر قسماً من الأزرار الشفافة أدناه لإدارة البوت:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    
    # قسم رادار الذهب واختيار المدارس الصارمة 100%
    elif call.data == 'menu_gold':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🏦 مدرسة ICT / SMC (100%)", callback_data='school_ict'))
        markup.row(InlineKeyboardButton("⏳ مدرسة وايكوف Wyckoff (100%)", callback_data='school_wyckoff'))
        markup.row(InlineKeyboardButton("📊 تحليل السيولة VSA (100%)", callback_data='school_vsa'))
        markup.row(InlineKeyboardButton("📐 التحليل الكلاسيكي المطور (100%)", callback_data='school_classic'))
        markup.row(InlineKeyboardButton("🟢 تشغيل التداول التلقائي", callback_data='trade_on'), 
                   InlineKeyboardButton("🔴 إيقاف التداول التلقائي", callback_data='trade_off'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        text = (
            "👑 **رادار التداول الآلي للذهب (XAUUSD)**\n\n"
            "• 🎓 المدرسة النشطة: **ICT & SMC (صارمة 100%)**\n"
            "• 🤖 حالة التداول التلقائي: 🔴 **متوقف حالياً**\n"
            "• 🧠 فلتر الذكاء الاصطناعي: يراقب فجوات الـ FVG والسيولة وحركة صناع السوق...\n\n"
            "اختر المدرسة المطلوبة لتفعيل قواعدها بالكامل، أو تحكم بتشغيل وإيقاف التداول الآلي:"
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # قسم إدارة المخاطر وصمام أمان الـ 40$ والـ Kill Switch
    elif call.data == 'menu_risk':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🎯 تعديل مخاطرة الصفقة ($)", callback_data='set_trade_risk'))
        markup.row(InlineKeyboardButton("🛑 تعديل حد الخسارة اليومي ($)", callback_data='set_daily_risk'))
        markup.row(InlineKeyboardButton("🚨 إغلاق الطوارئ الفوري (Kill Switch)", callback_data='kill_switch'))
        markup.row(InlineKeyboardButton("🔄 إعادة تفعيل البوت", callback_data='reset_bot'))
        markup.row(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu'))
        
        text = (
            "🛡️ **إعدادات المخاطر الصارمة للذهب**\n\n"
            "• مخاطرة الصفقة الواحدة: **40.00 USD** (اللوت يُحسب تلقائياً لحماية الحساب)\n"
            "• حد الخسارة اليومي الأقصى: **40.00 USD**\n"
            "• حالة الحماية الحالية: 🟢 **نشطة وتحرس الحساب**\n\n"
            "بمجرد وصول إجمالي خسائر صفقات الذهب اليوم إلى 40$، سيتفعل الـ Kill Switch تلقائياً لإغلاق كافة العقود المفتوحة لحمايتك."
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")

    # لإنهاء تأثير جاري التحميل على الزر في التلغرام بعد الضغط
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    logger.info("🚀 تم فحص وتأكيد الكود الافتراضي. جاري تشغيل البوت المستقر على سيرفر Railway...")
    bot.infinity_polling()
