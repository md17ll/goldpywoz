import os
import requests
import json

class AIEngine:
    def __init__(self):
        # سحب مفتاح OpenRouter من إعدادات بيئة سيرفر Railway للحفاظ على أمان حسابك رصيدك
        self.api_key = os.getenv("OPENROUTER_API_KEY", "ضع_مفتاح_أوبن_راوتر_هنا")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        
        # القوانين الصارمة بنسبة 100% لمدرسة ICT و SMC المخصصة للذهب
        self.ict_prompt = (
            "You are an elite institutional trading AI specializing 100% in Inner Circle Trader (ICT) and Smart Money Concepts (SMC).\n"
            "Your sole focus is Gold (XAUUSD) Scalping. You must strictly analyze charts based on these rules with zero deviation:\n"
            "1. Market Structure: Identify HTF trend and LTF shifts. Look for Break of Structure (BOS) and Market Structure Shift (MSS/CHoCH).\n"
            "2. Liquidity: Locate Buy-side and Sell-side Liquidity pools. You ONLY enter after a Liquidity Sweep has occurred.\n"
            "3. Institutional Zones: Identify valid Order Blocks (OB) and Fair Value Gaps (FVG) on 1m and 5m charts for precise entries.\n"
            "4. Output: You must provide your final decision strictly in a structured JSON format containing: action (BUY/SELL/WAIT), entry_price, stop_loss, take_profit, and reason."
        )

        # القوانين الصارمة بنسبة 100% لمدرسة وايكوف
        self.wyckoff_prompt = (
            "You are an expert financial AI specializing 100% in the Wyckoff Method for Gold (XAUUSD) trading.\n"
            "Analyze the market structure strictly based on Accumulation, Distribution, Markup, and Markdown phases.\n"
            "Look for Springs, Upthrusts, and precise Tests before giving any entry. Output must be strictly in JSON format with: action, entry_price, stop_loss, take_profit, and reason."
        )

        # القوانين الصارمة بنسبة 100% لمدرسة التحليل الحجمي VSA
        self.vsa_prompt = (
            "You are an expert AI specializing 100% in Volume Spread Analysis (VSA) tailored for Gold (XAUUSD) scalping.\n"
            "Analyze the relationship between candlestick spread and volume to detect smart money accumulation or distribution.\n"
            "Look for No Demand, No Supply, and Effort vs Result anomalies. Output must be strictly in JSON format with: action, entry_price, stop_loss, take_profit, and reason."
        )

        # القوانين الصارمة لمدرسة التحليل الكلاسيكي المطور
        self.classic_prompt = (
            "You are an expert AI specializing 100% in Advanced Classic Technical Analysis for Gold (XAUUSD).\n"
            "Analyze strict support/resistance levels, trendlines, chart patterns (Head & Shoulders, Double Top/Bottom), and strict Price Action candlestick triggers.\n"
            "Output must be strictly in JSON format with: action, entry_price, stop_loss, take_profit, and reason."
        )

    def analyze_gold_market(self, market_data_summary, chosen_school="ICT"):
        """
        إرسال البيانات التاريخية واللحظية للذهب القادمة من MT5 إلى OpenRouter لتحليلها
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://railway.app" # مطلوب من قبل أوبن راوتر لتصنيف التطبيق
        }

        # تحديد التوجيه بناءً على المدرسة التي اخترتها أنت من الأزرار الشفافة
        if chosen_school == "ICT":
            system_prompt = self.ict_prompt
        elif chosen_school == "Wyckoff":
            system_prompt = self.wyckoff_prompt
        elif chosen_school == "VSA":
            system_prompt = self.vsa_prompt
        elif chosen_school == "Classic":
            system_prompt = self.classic_prompt
        else:
            system_prompt = self.ict_prompt # الافتراضي ICT

        # تجهيز الطلب لإرساله إلى أوبن راوتر (نستخدم هنا نموذج Claude 3.5 Sonnet لذكائه الحاد بالبرمجة والمال، ويمكنك تبديله لـ gpt-4o)
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this Gold live data and generate your strict decision:\n{market_data_summary}"}
            ],
            "response_format": {"type": "json_object"} # إجبار الـ AI على الرد بصيغة كود جيسون نظيف ليفهمه السيرفر
        }

        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                ai_reply = result['choices'][0]['message']['content']
                return json.loads(ai_reply) # إرجاع النتيجة ككود جاهز للتنفيذ
            else:
                return {"action": "WAIT", "reason": f"OpenRouter Error: {response.status_code}"}
        except Exception as e:
            return {"action": "WAIT", "reason": f"AI Engine Exception: {str(e)}"}
