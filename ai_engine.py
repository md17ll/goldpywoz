import os
import requests

class AIEngine:
    def __init__(self):
        # جلب المفتاح السحابي المربوط في Railway
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def analyze_gold_market(self, market_data_summary, chosen_school="ICT"):
        if not self.api_key:
            return {"action": "WAIT", "reason": "OpenRouter API Key is missing"}

        # صياغة القواعد الحقيقية بناءً على اختيارك من أزرار البوت
        if chosen_school == "ICT":
            system_prompt = "You are an expert ICT (Inner Circle Trader) bot. Analyze Gold (XAUUSD) strictly using Fair Value Gaps (FVG), Liquidity Pools, and Order Blocks."
        elif chosen_school == "SMC":
            system_prompt = "You are a Smart Money Concepts (SMC) bot. Analyze Gold strictly using Break of Structure (BOS), Change of Character (CHoCH), and Premium/Discount zones."
        elif chosen_school == "Wyckoff":
            system_prompt = "You are a Wyckoff expert bot. Analyze Gold structures using Accumulation, Distribution, and Spring phases."
        else:
            system_prompt = "You are a professional Gold trading assistant focusing on market structure and trend liquidity."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3-70b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {market_data_summary}. Respond ONLY in JSON format with keys 'action' (BUY, SELL, or WAIT) and 'reason' (brief description)."}
            ]
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                # هنا يتم تحويل النص المستلم إلى قاموس برميجي
                import json
                return json.loads(content)
        except Exception:
            pass

        return {"action": "WAIT", "reason": "AI Engine temporary timeout. Monitoring continues."}
