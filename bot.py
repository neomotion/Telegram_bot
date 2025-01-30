# bot.py
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
#from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from websearch import WebSearch
from language_handler import LanguageHandler
from file_handler import FileHandler
from sentiment_handler import SentimentHandler
from mongo_handler import MongoHandler
#import html
#from datetime import datetime
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from datetime import datetime, UTC

# Tokens
TELEGRAM_TOKEN = "7440005565:AAGPMCTaHp-ynA-6L72aghpCLVzlhjpgZzs"
GEMINI_API_KEY = "AIzaSyDeB1RgKUpmk6mdRtbeXJ8vu-Kwo3p3pTI"
MONGODB_URI = "mongodb+srv://Sahilsssingh5:Sahilsssingh5@cluster0.bilej.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0"

# Initialize clients
search_client = WebSearch(api_key=GEMINI_API_KEY)
language_client = LanguageHandler(api_key=GEMINI_API_KEY)
file_client = FileHandler(api_key=GEMINI_API_KEY)
sentiment_client = SentimentHandler(api_key=GEMINI_API_KEY)
mongo_client = MongoHandler(mongodb_uri=MONGODB_URI)

# Store chat modes and file data for users
user_chat_modes = {}
file_data = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start command and user registration."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Register user
    user_data = {
        "chat_id": chat_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

    await mongo_client.register_user(user_data)

    # Create contact button
    keyboard = [[KeyboardButton("Share Contact", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    welcome_text = """Hello! I'm a multifunctional bot. I can:
1. Chat with sentiment awareness (/chat to toggle)
2. Search the web (/websearch query)
3. Analyze files (just send them to me)
4. Support multiple languages

Please share your contact to complete registration!"""

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle sentiment-aware chat mode."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Toggle chat mode
    current_mode = user_chat_modes.get(user_id, False)
    user_chat_modes[user_id] = not current_mode

    # Check if user is registered
    user = await mongo_client.get_user(chat_id)
    if not user:
        await update.message.reply_text(
            "Please start the bot with /start and complete registration first!"
        )
        return

    mode_status = "ON" if user_chat_modes[user_id] else "OFF"

    # Store mode change in chat history
    chat_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message": f"Changed chat mode to {mode_status}",
        "type": "system_message"
    }
    await mongo_client.store_chat_message(chat_data)

    await update.message.reply_text(
        f"Sentiment-aware chat mode is now {mode_status}.\n"
        f"{'I will now consider emotional context in our conversation.' if mode_status == 'ON' else 'I will now chat normally.'}"
    )


async def websearch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /websearch command."""
    chat_id = update.effective_chat.id

    # Check if user is registered
    user = await mongo_client.get_user(chat_id)
    if not user:
        await update.message.reply_text(
            "Please start the bot with /start and complete registration first!"
        )
        return

    # Get the query from command arguments
    query = ' '.join(context.args)

    if not query:
        await update.message.reply_text(
            "Please provide a search query.\n"
            "Example: /websearch latest AI developments"
        )
        return

    try:
        # Send typing action
        await update.message.chat.send_action(action="typing")

        # Perform search (now synchronous)
        summary, urls = search_client.search(query)

        # Create response
        response_text = f"🔍 Search results for: {query}\n\n"
        response_text += f"📝 Summary:\n{summary}\n\n"
        response_text += "🔗 Top results:\n"
        for i, url in enumerate(urls[:3], 1):
            response_text += f"{i}. {url}\n"

        # Send response
        await update.message.reply_text(
            response_text,
            disable_web_page_preview=True
        )

        # Store search in chat history with proper UTC timestamp
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": update.effective_user.id,
            "message": f"/websearch {query}",
            "type": "user_command",
            "timestamp": datetime.now(UTC)
        })

        # Store bot's response
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": None,
            "message": response_text,
            "type": "bot_response",
            "timestamp": datetime.now(UTC)
        })

    except Exception as e:
        error_msg = f"Sorry, an error occurred during search: {str(e)}"
        await update.message.reply_text(error_msg)



async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contact information."""
    contact = update.effective_message.contact
    chat_id = update.effective_chat.id

    if contact:
        # Store phone number
        success = await mongo_client.update_user_phone(chat_id, contact.phone_number)
        if success:
            await update.message.reply_text(
                "Thank you! Registration complete. You can now use all features!",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "Sorry, there was an error saving your contact. Please try again later."
            )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command messages."""
    message_text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if user is registered
    user = await mongo_client.get_user(chat_id)
    if not user:
        await update.message.reply_text(
            "Please start the bot with /start and complete registration first!"
        )
        return

    try:
        # Store message in chat history
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": user_id,
            "message": message_text,
            "type": "user_message",
            "timestamp": datetime.now(UTC)
        })

        # Send typing action
        await update.message.chat.send_action(action="typing")

        if user_chat_modes.get(user_id, False):
            # Sentiment chat mode
            sentiment_response = await handle_sentiment_chat(update, message_text)
            if sentiment_response:
                await mongo_client.store_chat_message({
                    "chat_id": chat_id,
                    "user_id": None,
                    "message": sentiment_response,
                    "type": "bot_response",
                    "timestamp": datetime.now(UTC)
                })
        else:
            # Regular chat mode
            prompt = f"I am an AI assistant. The user sent this message: {message_text}\nPlease provide a helpful response."
            response = sentiment_client.model.generate_content(prompt)
            response_text = response.text.strip()

            await update.message.reply_text(response_text)

            await mongo_client.store_chat_message({
                "chat_id": chat_id,
                "user_id": None,
                "message": response_text,
                "type": "bot_response",
                "timestamp": datetime.now(UTC)
            })

    except Exception as e:
        error_msg = f"Sorry, an error occurred: {str(e)}"
        await update.message.reply_text(error_msg)


async def websearch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /websearch command."""
    chat_id = update.effective_chat.id

    # Check if user is registered
    user = await mongo_client.get_user(chat_id)
    if not user:
        await update.message.reply_text(
            "Please start the bot with /start and complete registration first!"
        )
        return

    # Get the query from command arguments
    query = ' '.join(context.args)

    if not query:
        await update.message.reply_text(
            "Please provide a search query.\n"
            "Example: /websearch latest AI developments"
        )
        return

    try:
        # Send typing action
        await update.message.chat.send_action(action="typing")

        # Perform search (synchronous call)
        summary, urls = search_client.search(query)

        # Create response
        response_text = f"🔍 Search results for: {query}\n\n"
        response_text += f"📝 Summary:\n{summary}\n\n"
        response_text += "🔗 Top results:\n"
        for i, url in enumerate(urls[:3], 1):
            response_text += f"{i}. {url}\n"

        # Send response
        await update.message.reply_text(
            response_text,
            disable_web_page_preview=True
        )

        # Store search in chat history
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": update.effective_user.id,
            "message": f"/websearch {query}",
            "type": "user_command",
            "timestamp": datetime.utcnow()
        })

        # Store bot's response
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": None,
            "message": response_text,
            "type": "bot_response",
            "timestamp": datetime.utcnow()
        })

    except Exception as e:
        error_msg = f"Sorry, an error occurred during search: {str(e)}"
        await update.message.reply_text(error_msg)


async def handle_sentiment_chat(update: Update, message_text: str):
    """Handle chat with sentiment analysis."""
    try:
        await update.message.chat.send_action(action="typing")

        # Analyze sentiment (synchronous call)
        sentiment_data = await sentiment_client.analyze_sentiment(message_text)

        # Get response considering sentiment (synchronous call)
        response = await sentiment_client.get_response_with_sentiment(message_text, sentiment_data)

        # Send response
        await update.message.reply_text(response)
        return response

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        await update.message.reply_text(error_msg)
        return error_msg


async def handle_regular_chat(update: Update, message_text: str):
    """Handle regular chat without sentiment analysis."""
    try:
        await update.message.chat.send_action(action="typing")

        # Generate response (synchronous call)
        response = sentiment_client.model.generate_content(message_text)
        # Send the response text
        response_text = response.text
        await update.message.reply_text(response_text)
        return response_text

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        await update.message.reply_text(error_msg)
        return error_msg


async def handle_operation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks for file operations."""
    query = update.callback_query
    await query.answer()

    try:
        chat_id = update.effective_chat.id

        # Check if user is registered
        user = await mongo_client.get_user(chat_id)
        if not user:
            await query.message.reply_text(
                "Please start the bot with /start and complete registration first!"
            )
            return

        if chat_id not in file_data:
            await query.message.reply_text("Sorry, I can't find the file data. Please send the file again.")
            return

        # Get operation from callback data
        operation = query.data.replace('op_', '')

        # Process operation
        result = await file_client.process_operation(
            operation,
            file_data[chat_id]['content'],
            await file_client.get_file_type(
                file_data[chat_id]['name'],
                file_data[chat_id]['mime_type']
            )
        )

        # Store operation result in chat history
        operation_data = {
            "chat_id": chat_id,
            "user_id": None,
            "message": f"File operation '{operation}' result:\n{result}",
            "type": "file_operation",
            "timestamp": datetime.utcnow()
        }
        await mongo_client.store_chat_message(operation_data)

        # Send result
        response_text = f"🔍 {operation.replace('_', ' ').title()}:\n\n{result}"
        await query.message.reply_text(response_text)

    except Exception as e:
        await query.message.reply_text(f"Sorry, an error occurred: {str(e)}")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded files."""
    try:
        chat_id = update.effective_chat.id

        # Check if user is registered
        user = await mongo_client.get_user(chat_id)
        if not user:
            await update.message.reply_text(
                "Please start the bot with /start and complete registration first!"
            )
            return

        # Get file based on message type
        if update.message.document:
            file = await update.message.document.get_file()
            file_name = update.message.document.file_name
            mime_type = update.message.document.mime_type
        elif update.message.photo:
            # For photos, get the largest size
            photo = update.message.photo[-1]
            file = await photo.get_file()
            file_name = f"photo_{file.file_id}.jpg"
            mime_type = "image/jpeg"
        else:
            await update.message.reply_text("Sorry, I can't process this type of file.")
            return

        # Download file content
        file_content = await file.download_as_bytearray()

        # Store file content temporarily
        file_data[chat_id] = {
            'content': file_content,
            'name': file_name,
            'mime_type': mime_type
        }

        # Send typing action
        await update.message.chat.send_action(action="typing")

        # Analyze file
        analysis = await file_client.analyze_file(file_content, file_name, mime_type)

        # Store file metadata in MongoDB
        file_metadata = {
            "chat_id": chat_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "file_type": analysis['file_type'],
            "initial_analysis": analysis['initial_analysis'],
            "uploaded_at": datetime.utcnow()
        }
        await mongo_client.store_file_metadata(file_metadata)

        # Create keyboard with available operations
        keyboard = []
        for operation in analysis['available_operations']:
            operation_text = operation.replace('_', ' ').title()
            keyboard.append([InlineKeyboardButton(operation_text, callback_data=f"op_{operation}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send initial analysis and operation options
        response_text = f"📄 File Type: {analysis['file_type'].upper()}\n\n"
        response_text += f"Initial Analysis:\n{analysis['initial_analysis']}\n\n"
        response_text += "Choose an operation to perform:"

        await update.message.reply_text(response_text, reply_markup=reply_markup)

        # Store file analysis in chat history
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": None,
            "message": response_text,
            "type": "file_analysis",
            "timestamp": datetime.utcnow()
        })

    except Exception as e:
        await update.message.reply_text(f"Sorry, an error occurred while processing the file: {str(e)}")


async def handle_operation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks for file operations."""
    query = update.callback_query
    await query.answer()

    try:
        chat_id = update.effective_chat.id

        # Check if user is registered
        user = await mongo_client.get_user(chat_id)
        if not user:
            await query.message.reply_text(
                "Please start the bot with /start and complete registration first!"
            )
            return

        if chat_id not in file_data:
            await query.message.reply_text("Sorry, I can't find the file data. Please send the file again.")
            return

        # Get operation from callback data
        operation = query.data.replace('op_', '')

        # Process operation
        result = await file_client.process_operation(
            operation,
            file_data[chat_id]['content'],
            await file_client.get_file_type(
                file_data[chat_id]['name'],
                file_data[chat_id]['mime_type']
            )
        )

        # Store operation result
        await mongo_client.store_chat_message({
            "chat_id": chat_id,
            "user_id": None,
            "message": f"File operation '{operation}' result:\n{result}",
            "type": "file_operation",
            "timestamp": datetime.utcnow()
        })

        # Send result
        response_text = f"🔍 {operation.replace('_', ' ').title()}:\n\n{result}"
        await query.message.reply_text(response_text)

    except Exception as e:
        await query.message.reply_text(f"Sorry, an error occurred: {str(e)}")

def main():
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("websearch", websearch_command))  # Make sure this is here

    # Add contact handler
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Add file handler
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.Document.ALL,
        handle_file
    ))

    # Add callback query handler
    application.add_handler(CallbackQueryHandler(handle_operation_callback))

    # Handle regular messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()