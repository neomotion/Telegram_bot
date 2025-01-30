# file_handler.py
import google.generativeai as genai
from typing import Tuple, Dict, List, Any
import mimetypes
from PIL import Image
import io
import pypdf
import PyPDF2
import re


class FileHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.text_model = genai.GenerativeModel('gemini-1.5-pro')
        self.vision_model = genai.GenerativeModel('gemini-1.5-pro-vision')

        self.supported_operations = {
            'image': ['describe', 'analyze_content', 'extract_text', 'identify_objects'],
            'pdf': ['summarize', 'extract_key_points', 'analyze_content'],
            'text': ['summarize', 'extract_key_points', 'analyze_content'],
            'document': ['summarize', 'extract_key_points', 'analyze_content']
        }

    def get_available_operations(self, file_type: str) -> List[str]:
        return self.supported_operations.get(file_type, [])

    async def get_file_type(self, file_name: str, mime_type: str = None) -> str:
        if mime_type and mime_type.startswith('image/'):
            return 'image'
        elif mime_type and mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type and mime_type.startswith('text/'):
            return 'text'
        else:
            ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                return 'image'
            elif ext == 'pdf':
                return 'pdf'
            elif ext in ['txt', 'md', 'csv']:
                return 'text'
            elif ext in ['doc', 'docx', 'odt']:
                return 'document'
        return 'unknown'

    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text content from PDF."""
        try:
            # Create a PDF file object
            pdf_file = io.BytesIO(file_content)

            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            # Clean up the extracted text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            text = text.strip()

            return text if text else "No readable text found in PDF."

        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")

    async def analyze_file(self, file_content: bytes, file_name: str, mime_type: str = None) -> Dict[str, Any]:
        file_type = await self.get_file_type(file_name, mime_type)

        try:
            if file_type == 'image':
                image = Image.open(io.BytesIO(file_content))
                response = await self._analyze_image(image)
            elif file_type == 'pdf':
                text_content = self._extract_pdf_text(file_content)
                response = await self._analyze_text(text_content)
            else:
                text_content = file_content.decode('utf-8', errors='ignore')
                response = await self._analyze_text(text_content)

            operations = self.get_available_operations(file_type)

            return {
                'file_type': file_type,
                'initial_analysis': response,
                'available_operations': operations
            }
        except Exception as e:
            raise Exception(f"Error analyzing file: {str(e)}")

    async def _analyze_image(self, image: Image) -> str:
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            response = self.vision_model.generate_content([image, "What's in this image?"])
            return response.text
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")

    async def _analyze_text(self, text: str) -> str:
        try:
            text = text[:4000] + "..." if len(text) > 4000 else text
            prompt = "What is this text about? Give a brief overview:"
            response = self.text_model.generate_content(prompt + "\n" + text)
            return response.text
        except Exception as e:
            raise Exception(f"Error analyzing text: {str(e)}")

    async def process_operation(self, operation: str, file_content: bytes, file_type: str) -> str:
        try:
            if file_type == 'image':
                image = Image.open(io.BytesIO(file_content))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                return await self._process_image_operation(operation, image)
            elif file_type == 'pdf':
                text_content = self._extract_pdf_text(file_content)
                text_content = text_content[:4000] + "..." if len(text_content) > 4000 else text_content
                return await self._process_text_operation(operation, text_content)
            else:
                text_content = file_content.decode('utf-8', errors='ignore')
                text_content = text_content[:4000] + "..." if len(text_content) > 4000 else text_content
                return await self._process_text_operation(operation, text_content)
        except Exception as e:
            raise Exception(f"Error processing operation {operation}: {str(e)}")

    async def _process_image_operation(self, operation: str, image: Image) -> str:
        operation_prompts = {
            'describe': "What do you see in this image?",
            'analyze_content': "What's happening in this image?",
            'extract_text': "What text do you see in this image?",
            'identify_objects': "List the main objects in this image."
        }

        prompt = operation_prompts.get(operation, "Describe this image.")
        response = self.vision_model.generate_content([image, prompt])
        return response.text

    async def _process_text_operation(self, operation: str, text: str) -> str:
        operation_prompts = {
            'summarize': "What are the main points of this text?",
            'extract_key_points': "List the key points from this text:",
            'analyze_content': "What are the main ideas and themes in this text?"
        }

        prompt = operation_prompts.get(operation, "Analyze this:") + "\n" + text
        response = self.text_model.generate_content(prompt)
        return response.text