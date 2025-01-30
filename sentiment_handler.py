# sentiment_handler.py
import google.generativeai as genai
from typing import Dict


class SentimentHandler:
    def __init__(self, api_key: str):
        """Initialize SentimentHandler with Gemini API key."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text and return sentiment scores."""
        try:
            prompt = f"""Analyze sentiment of: {text}
            Return only JSON format:
            {{
                "sentiment_scores": {{
                    "positive": <0-1>,
                    "negative": <0-1>,
                    "neutral": <0-1>
                }},
                "emotion": "<primary emotion>",
                "tone": "<tone>"
            }}"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()

            sentiment_data = eval(response_text)
            return sentiment_data

        except Exception as e:
            return {
                "sentiment_scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                "emotion": "neutral",
                "tone": "neutral"
            }

    async def get_response_with_sentiment(self, user_message: str, sentiment_data: Dict) -> str:
        """Generate a response considering both message and sentiment."""
        try:
            # Create a more focused prompt
            prompt = f"""Context: User message with {sentiment_data['emotion']} emotion and {sentiment_data['tone']} tone.
            Message: {user_message}

            Respond naturally to this message, matching the emotional tone appropriately."""

            # Generate content is synchronous
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            return "I understand you're expressing something important. Could you tell me more?"