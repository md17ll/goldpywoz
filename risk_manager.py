import logging

logger = logging.getLogger(__name__)

class GoldRiskManager:
    def __init__(self, max_daily_loss=40.0, per_trade_risk=40.0):
        self.max_daily_loss = max_daily_loss  # حد الخسارة اليومي الأقصى (40$)
        self.per_trade_risk = per_trade_risk  # حد خسارة الصفقة الواحدة (40$)
        self.current_daily_loss = 0.0         # عداد تراكم الخسائر لليوم الحالي
        self.is_bot_enabled = True            # حالة أمان البوت (مفعل/معطل)

    def calculate_gold_lot_size(self, entry_price, stop_loss):
        """
        حساب حجم اللوت (Lot Size) بدقة لزوج الذهب (XAUUSD) بناءً على قيمة الستوب لوز ومخاطرة 40$.
        معادلة الذهب في MT5: حجم العقد القياسي هو 100 أونصة لكل 1 لوت كامل.
        النقطة الواحدة (1 Pip) في الذهب تعادل تحرك السعر بمقدار 0.10 (مثال: من 2350.0 إلى 2350.1).
        """
        try:
            # حساب الفارق السعري المطلق بين الدخول والستوب لوز للأونصة
            price_difference = abs(entry_price - stop_loss)
            
            if price_difference <= 0:
                logger.warning("فارق السعر بين الدخول والستوب لوز صفر! تم تحديد أقل لوت تلقائياً.")
                return 0.01
            
            # المعادلة: اللوت = المبلغ المخاطر به / (الفارق السعري بالدولار * 100 أونصة)
            # مثال: دخول من 2300$ واستوب لوز 2298$ (الفارق 2$). اللوت = 40 / (2 * 100) = 0.20 لوت.
            lot_size = self.per_trade_risk / (price_difference * 100)
            
            # تقريب حجم اللوت لخانة عشريتين (قوانين منصة MT5)
            lot_size = round(lot_size, 2)
            
            # التأكد أن اللوت لا يقل عن الحد الأدنى في المنصة وهو 0.01
            if lot_size < 0.01:
                return 0.01
                
            logger.info(f"🛡️ حاسبة اللوت: الدخول {entry_price}، الستوب {stop_loss}، الفارق {price_difference}$. اللوت المحسوب لحماية الـ 40$: {lot_size}")
            return lot_size

        except Exception as e:
            logger.error(f"خطأ أثناء حساب حجم لوت الذهب: {e}")
            return 0.01

    def update_daily_pnl(self, closed_trade_pnl):
        """
        تحديث عداد الأرباح والخسائر اليومي فور إغلاق أي صفقة.
        إذا تساوت أو تخطت الخسائر حاجز الـ 40$ المحددة، يتم تفعيل الـ Kill Switch فوراً.
        """
        # نركز فقط على الصفقات الخاسرة (التي تكون قيمتها بالسالب)
        if closed_trade_pnl < 0:
            self.current_daily_loss += abs(closed_trade_pnl)
            logger.info(f"⚠️ صفقة خاسرة! إجمالي خسائر اليوم التراكمية حالياً: {self.current_daily_loss}$ / {self.max_daily_loss}$")
            
        # التحقق من كسر جدار الحماية اليومي
        if self.current_daily_loss >= self.max_daily_loss:
            self.is_bot_enabled = False
            logger.critical("🚨 تفعيل الـ Kill Switch! تم الوصول للحد الأقصى من الخسارة اليومية (40$). تم إيقاف البوت كلياً.")
            return "🚨 KILL_SWITCH_TRIGGERED"
            
        return "🛡️ ACCOUNT_SAFE"

    def reset_daily_tracker(self):
        """
        تصفير عداد الخسائر وإعادة السماح للبوت بالعمل مع بداية يوم تداول جديد.
        """
        self.current_daily_loss = 0.0
        self.is_bot_enabled = True
        logger.info("🔄 يوم تداول جديد: تم تصفير عداد المخاطر وإعادة تفعيل حارس الأمان بنجاح.")
