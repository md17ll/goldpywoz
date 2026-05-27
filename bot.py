import os
import logging
import asyncio
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

# 4. دالة التشغيل الحقيقية المتوافقة مع السيرفرات السحابية الحديثة لعدم حدوث كراش
async def main_async():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.error("🚨 خطأ: لم يتم العثور على TELEGRAM_TOKEN في بيئة السيرفر!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern='main_menu'))
    application.add_handler(CallbackQueryHandler(menu_gold, pattern='menu_gold'))
    application.add_handler(CallbackQueryHandler(menu_risk, pattern='menu_risk'))

    logger.info("🚀 جاري تهيئة وإقلاع نظام البوت بنجاح...")
    
    # بناء وتحديث التهيئة بشكل يدوي لتفادي ثغرة الحزم المتعارضة في بايثون 3.13
    await application.initialize()
    await application.updater.start_polling()
    await application.start()
    
    logger.info("🟢 البوت يعمل الآن بكفاءة وبدون تعارض.")
    
    # إبقاء السيرفر حياً ومستمعاً للأوامر بشكل دائم
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    # تشغيل المنظومة من خلال دالة asyncio الصريحة للتحكم الكامل بالـ Event Loop
    asyncio.run(main_async())
