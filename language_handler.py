# language_handler.py
import google.generativeai as genai
from typing import Tuple

class LanguageHandler:
    def __init__(self, api_key: str):
        """
        Initialize LanguageHandler with Gemini API key.
        
        Args:
            api_key (str): Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            prompt = f"""Detect the language of this text and respond with only the ISO 639-1 language code (2 letters):
            Text: {text}"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip().lower()[:2]  # Get first two chars of language code
        except:
            return 'en'  # Default to English on error
            
    async def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text to English if not already in English.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code
            
        Returns:
            str: English translation or original text if already English
        """
        if source_lang == 'en':
            return text
            
        try:
            prompt = f"""Translate this text to English:
            Text: {text}
            Source Language: {source_lang}
            
            Respond with only the English translation."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text
            
    async def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate text from English to target language.
        
        Args:
            text (str): English text
            target_lang (str): Target language code
            
        Returns:
            str: Translated text
        """
        if target_lang == 'en':
            return text
            
        try:
            prompt = f"""Translate this English text to {target_lang}:
            Text: {text}
            
            Respond with only the translation."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text
            
    async def process_text(self, text: str) -> Tuple[str, str, str]:
        """
        Process text: detect language, translate to English if needed.
        
        Args:
            text (str): Input text
            
        Returns:
            Tuple[str, str, str]: (English text, original language code, original text)
        """
        original_text = text
        lang_code = await self.detect_language(text)
        english_text = await self.translate_to_english(text, lang_code)
        
        return english_text, lang_code, original_text