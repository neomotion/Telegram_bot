# web_search.py
import google.generativeai as genai
from typing import Tuple, List


class WebSearch:
    def __init__(self, api_key: str):
        """Initialize WebSearch with Gemini API key."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def search(self, query: str) -> Tuple[str, List[str]]:
        """
        Perform web search using Gemini.
        Returns tuple of (summary, list of urls)
        """
        try:
            # Create a search prompt
            search_prompt = f"""Search query: {query}

                                Please provide:
                                1. A brief summary of the topic (2-3 sentences)
                                2. Three relevant URLs (only real, working URLs)
                                
                                Format exactly as:
                                SUMMARY: <your summary>
                                URLS:
                                - <url1>
                                - <url2>
                                - <url3>"""

            # Get response from Gemini
            response = self.model.generate_content(search_prompt)
            response_text = response.text.strip()

            # Parse response
            parts = response_text.split('URLS:')
            if len(parts) != 2:
                return "Couldn't parse search results properly.", []

            summary = parts[0].replace('SUMMARY:', '').strip()
            urls_text = parts[1].strip()

            # Extract URLs
            urls = [url.strip('- ').strip() for url in urls_text.split('\n') if url.strip('- ').strip()]

            return summary, urls[:3]

        except Exception as e:
            raise Exception(f"Search error: {str(e)}")

    def get_suggested_queries(self, query: str) -> List[str]:
        """Get suggested related search queries."""
        try:
            prompt = f"""For the search query "{query}", suggest 3 related search queries.
            Return only the queries, one per line."""

            response = self.model.generate_content(prompt)
            suggestions = [line.strip() for line in response.text.split('\n') if line.strip()]
            return suggestions[:3]

        except Exception:
            return []
