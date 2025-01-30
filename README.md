
# Advanced Telegram Bot with AI Capabilities

A Telegram bot that combines the power of Google's Gemini AI with various functionalities including sentiment analysis, file processing, web search, and multilingual support.

## Features

### 1. User Registration and Management
- Automatic user registration on first interaction
- Phone number verification using Telegram's contact sharing
- Secure storage of user data in MongoDB

### 2. Gemini-Powered Chat
- Regular chat mode with AI responses
- Sentiment-aware chat mode that analyses emotional context
- Complete chat history storage with timestamps
- Support for multiple languages

### 3. Web Search Functionality
- AI-powered web search using Gemini
- Summarized results with relevant URLs
- Multilingual search support
- Rate limiting and quota management

### 4. File Analysis
- Support for multiple file types (Images, PDFs, Text files)
- AI-powered content analysis
- File metadata storage
- Custom operations based on file type:
  - Images: Description, content analysis, text extraction
  - Documents: Summarization, key points extraction
  - Text files: Analysis, sentiment detection

### 5. Database Integration
- MongoDB integration for data persistence
- Stores user data, chat history, and file metadata
- Tracks all interactions and operations

## Setup

### Prerequisites
```bash
# Required Python version
Python 3.12+

# Install required packages
pip install python-telegram-bot google-generativeai pymongo Pillow
```

### Configuration
Create a `.env` file with your API keys:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_uri
```

### Project Structure
```
telegram_bot/
├── bot.py                 # Main bot file
├── web_search.py         # Web search handler
├── file_handler.py       # File processing
├── sentiment_handler.py  # Sentiment analysis
├── mongo_handler.py      # Database operations
├── language_handler.py   # Language support
└── requirements.txt      # Dependencies
```

## Usage

### Starting the Bot
```bash
python bot.py
```

### Available Commands
- `/start` - Initialize the bot and register user
- `/chat` - Toggle sentiment-aware chat mode
- `/websearch [query]` - Search the web
- Send any file for analysis

### Examples

1. Web Search:
```
/websearch latest AI developments
```

2. Sentiment Chat:
```
/chat
"I'm really excited about this project!"
```

3. File Analysis:
- Send any image, PDF, or text file
- Choose from available operations
- Get AI-powered analysis

### Language Support
- Automatically detects message language
- Responds in the same language
- Supports web search in multiple languages

## Error Handling
- Rate limiting for API calls
- Quota management
- Clear error messages
- Fallback mechanisms

## Database Schema

### Users Collection
```json
{
    "chat_id": int,
    "username": string,
    "first_name": string,
    "phone_number": string,
    "registered_at": datetime
}
```

### Chat History Collection
```json
{
    "chat_id": int,
    "user_id": int,
    "message": string,
    "type": string,
    "timestamp": datetime
}
```

### Files Collection
```json
{
    "chat_id": int,
    "file_name": string,
    "mime_type": string,
    "analysis": string,
    "uploaded_at": datetime
}
```

## Contributing
Feel free to fork, make changes, and submit pull requests. For major changes, please open an issue first.

## License
[MIT License](LICENSE)

## Acknowledgments
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- [MongoDB](https://www.mongodb.com/)
