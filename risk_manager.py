class GoldRiskManager:
    def __init__(self, max_daily_loss=40.0, per_trade_risk=40.0):
        self.max_daily_loss = max_daily_loss
        self.per_trade_risk = per_trade_risk
        self.current_daily_loss = 0.0
        self.is_bot_enabled = True

    def calculate_gold_lot_size(self, entry_price, stop_loss):
        # حماية ضد القسمة على صفر إذا كان الستوب لوز غير صحيح
        price_risk = abs(entry_price - stop_loss)
        if price_risk == 0:
            return 0.01

        # حساب اللوت تلقائياً بحيث إذا ضربت الصفقة ستوب لوز لا تخسر أكثر من القيمة المحددة
        # نقطة الذهب (Pip) في عقد الـ Standard تساوي 10$ لكل 1 لوت كامل عند تحرك دولار واحد
        calculated_lot = round((self.per_trade_risk) / (price_risk * 10.0), 2)
        
        # التأكيد الصارم على ألا يقل اللوت عن 0.01 تحت أي ظرف
        return max(calculated_lot, 0.01)

    def check_daily_safety(self, new_loss):
        self.current_daily_loss += new_loss
        if self.current_daily_loss >= self.max_daily_loss:
            self.is_bot_enabled = False
            return False  # تفعيل الـ Kill Switch
        return True

    def reset_daily_tracker(self):
        self.current_daily_loss = 0.0
        self.is_bot_enabled = True
