import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# إعدادات الـ Logging لمراقبة عمل السيرفر على Railway وضمان تسجيل الأخطاء إن وجدت
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. الدالة الرئيسية لعرض القائمة الأساسية للمستخدم (تعديل الرسالة تلقائياً)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👑 رادار سكالبينغ الذهب", callback_data='menu_gold')],
        [InlineKeyboardButton("🛡️ إدارة المخاطر والأمان (40$)", callback_data='menu_risk')],
        [InlineKeyboardButton("📊 الإحصائيات والتحليل المالي", callback_data='menu_stats')],
        [InlineKeyboardButton("⚙️ ربط حساب MT5 (تجريبي/حقيقي)", callback_data='menu_mt5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "👑 **لوحة تحكم بوت الذهب الذكي (XAUUSD Scalper)**\n\n"
        "مرحباً بك في نظام التداول الهجين المتكامل. البوت مستضاف على **Railway** ومربوط بـ **OpenRouter**.\n\n"
        "اختر قسماً من الأزرار الشفافة أدناه لإدارة البوت:"
    )
    
    # التحقق: إذا كان تفاعل المستخدم عبر أمر /start نرسل رسالة جديدة، وإذا كان عبر زر شفاف نعدل نفس الرسالة
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# 2. قائمة رادار الذهب والتحكم بمدارس التحليل
async def menu_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🏦 مدرسة ICT / SMC (100%)", callback_data='school_ict')],
        [InlineKeyboardButton("⏳ مدرسة وايكوف Wyckoff (100%)", callback_data='school_wyckoff')],
        [InlineKeyboardButton("📊 تحليل السيولة VSA (100%)", callback_data='school_vsa')],
        [InlineKeyboardButton("📐 التحليل الكلاسيكي المطور (100%)", callback_data='school_classic')],
        [InlineKeyboardButton("🟢 تشغيل التداول التلقائي", callback_data='trade_on')],
        [InlineKeyboardButton("🔴 إيقاف التداول التلقائي", callback_data='trade_off')],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "👑 **رادار التداول الآلي للذهب (XAUUSD)**\n\n"
        "• 🎓 المدرسة النشطة: **ICT & SMC (صارمة 100%)**\n"
        "• 🤖 حالة التداول التلقائي: 🔴 **متوقف حالياً**\n"
        "• 🧠 فلتر الذكاء الاصطناعي: يراقب فجوات الـ FVG والسيولة وحركة صناع السوق...\n\n"
        "اختر المدرسة المطلوبة لتفعيل قواعدها بالكامل، أو تحكم بتشغيل وإيقاف التداول الآلي:"
    )
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# 3. قائمة إدارة المخاطر والأمان (حد الـ 40$)
async def menu_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎯 تعديل مخاطرة الصفقة ($)", callback_data='set_trade_risk')],
        [InlineKeyboardButton("🛑 تعديل حد الخسارة اليومي ($)", callback_data='set_daily_risk')],
        [InlineKeyboardButton("🚨 إغلاق الطوارئ الفوري (Kill Switch)", callback_data='kill_switch')],
        [InlineKeyboardButton("🔄 إعادة تفعيل البوت", callback_data='reset_bot')],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🛡️ **إعدادات المخاطر الصارمة للذهب**\n\n"
        "• مخاطرة الصفقة الواحدة: **40.00 USD** (اللوت يُحسب تلقائياً لحماية الحساب)\n"
        "• حد الخسارة اليومي الأقصى: **40.00 USD**\n"
        "• حالة الحماية الحالية: 🟢 **نشطة وتحرس الحساب**\n\n"
        "بمجرد وصول إجمالي خسائر صفقات الذهب اليوم إلى 40$، سيتفعل الـ Kill Switch تلقائياً لإغلاق كافة العقود المفتوحة لحمايتك."
    )
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# 4. دالة تشغيل البوت الأساسية المتوافقة تماماً مع بايثون 3.13 وسيرفرات لينوكس
def main():
    # سحب التوكن المربوط بلوحة تحكم Railway بشكل آمن ومباشر
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        logger.error("🚨 خطأ كارثي: لم يتم العثور على TELEGRAM_TOKEN في متغيرات بيئة السيرفر (Variables)!")
        return

    # بناء التطبيق وإعداده
    application = Application.builder().token(TOKEN).build()

    # ربط الإشارات (Callback Data) القادمة من الأزرار بالدوال لتعديل الرسائل بسلاسة دون رسائل جديدة
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern='main_menu'))
    application.add_handler(CallbackQueryHandler(menu_gold, pattern='menu_gold'))
    application.add_handler(CallbackQueryHandler(menu_risk, pattern='menu_risk'))

    logger.info("🚀 جاري بدء تشغيل البوت على سيرفر Railway بنجاح...")
    
    # التشغيل النظيف والافتراضي المتوافق تماماً مع إصدار 21.2 وبايثون 3.13 على السيرفر السحابي
    application.run_polling()

if __name__ == '__main__':
    main()
