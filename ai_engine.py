import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        # جلب المفتاح السحابي المربوط في لوحة تحكم Railway
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def analyze_gold_market(self, market_data_summary, chosen_school="ICT"):
        """
        تحليل شارت الذهب حقيقياً بناءً على المدرسة الفنية المختارة أو الاستراتيجية المخصصة
        """
        if not self.api_key:
            logger.error("🚨 مفتاح OPENROUTER_API_KEY غير موجود في إعدادات السيرفر!")
            return {"action": "WAIT", "reason": "OpenRouter API Key is missing"}

        # 1. صياغة القواعد الحقيقية والخاصة بكل مدرسة لفلترة الشارت عبر الـ Prompt
        if chosen_school == "ICT":
            system_prompt = (
                "You are an expert ICT (Inner Circle Trader) algorithmic bot. "
                "Analyze the Gold (XAUUSD) market data strictly looking for Fair Value Gaps (FVG), "
                "Liquidity Pools (BSL/SSL), Order Blocks, and Market Structure Shifts (MSS)."
            )
        elif chosen_school == "SMC":
            system_prompt = (
                "You are an advanced Smart Money Concepts (SMC) institutional trading bot. "
                "Analyze the Gold market strictly looking for Break of Structure (BOS), "
                "Change of Character (CHoCH), Inducement, and Premium vs Discount pricing zones."
            )
        elif chosen_school == "Wyckoff":
            system_prompt = (
                "You are a professional Wyckoff Method analysis bot. "
                "Analyze Gold market structural phases: Accumulation, Distribution, Re-Accumulation, "
                "and identify Spring, UTAD, or Sign of Strength (SOS) actions."
            )
        elif chosen_school == "VSA":
            system_prompt = (
                "You are a Volume Spread Analysis (VSA) expert bot. "
                "Analyze Gold data by correlating price spread with volume to detect "
                "Buying/Selling Climax, No Demand, No Supply, and Professional Money activity."
            )
        elif chosen_school == "Classic":
            # تخصيص هذا الجزء ليتعامل بذكاء وعمق مع الاستراتيجيات المخصصة التي تكتبها بنفسك في البوت
            system_prompt = (
                "You are a flexible custom strategy tester for Gold trading. "
                "The user will provide a specific set of custom technical rules. "
                "Evaluate the current market context strictly against the user's custom rules "
                "to find high-probability entry setups."
            )
        else:
            system_prompt = "You are a professional quantitative Gold trading assistant focusing on price action and market liquidity."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://railway.com", # مطلوب لتجنب حظر الطلبات من OpenRouter
            "X-Title": "Gold Scalper Bot"
        }

        payload = {
            "model": "meta-llama/llama-3-70b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Market Data Context:\n{market_data_summary}\n\nStrict Rule: You must respond ONLY with a valid raw JSON object. Do not include any introductory text, markdown blocks, or explanations outside the JSON. Format:\n{{\"action\": \"BUY\"/\"SELL\"/\"WAIT\", \"reason\": \"your brief analysis here\"}}"}
            ],
            "temperature": 0.2 # درجة منخفضة لضمان الالتزام الصارم بالقواعد الفنية وعدم التخريف
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # تنظيف النص المستلم في حال قيام الـ AI بإضافة علامات اقتباس البرمجة (```json) بالخطأ
                if content.startswith("
```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                elif content.startswith("```"):
                    content = content.replace("
```", "").strip()

                # تحويل النص البرمجي المستلم بأمان إلى قاموس بايثون (Dictionary)
                return json.loads(content)
            else:
                logger.error(f"🚨 فشل الطلب من OpenRouter. رمز الحالة: {response.status_code}")
        except Exception as e:
            logger.error(f"🚨 خطأ أثناء معالجة تحليل الـ AI للماركت: {e}")

        # في حال حدوث أي خطأ شبكي، يعود البوت لوضع الانتظار الآمن لحماية الـ 40$ من الدخول العشوائي
        return {"action": "WAIT", "reason": "AI Engine is analyzing live liquidity cycles. Standing by."}
