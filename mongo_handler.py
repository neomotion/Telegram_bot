from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Dict, Any, Optional, List

class MongoHandler:
    def __init__(self, mongodb_uri: str):
        """Initialize MongoDB connection asynchronously."""
        self.client = AsyncIOMotorClient(mongodb_uri)
        self.db = self.client.telegram_bot

        # Collections
        self.users = self.db.users
        self.chats = self.db.chat_history
        self.files = self.db.files

    async def register_user(self, user_data: Dict[str, Any]) -> bool:
        """Register or update user asynchronously."""
        try:
            existing_user = await self.users.find_one({"chat_id": user_data["chat_id"]})
            if existing_user:
                await self.users.update_one({"chat_id": user_data["chat_id"]}, {"$set": user_data})
            else:
                user_data["registered_at"] = datetime.utcnow()
                await self.users.insert_one(user_data)
            return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    async def update_user_phone(self, chat_id: int, phone_number: str) -> bool:
        """Update user's phone number asynchronously."""
        try:
            await self.users.update_one(
                {"chat_id": chat_id},
                {
                    "$set": {
                        "phone_number": phone_number,
                        "phone_verified": True,
                        "phone_verified_at": datetime.utcnow()
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Error updating phone: {e}")
            return False

    async def store_chat_message(self, chat_data: Dict[str, Any]) -> bool:
        """Store chat message in history asynchronously."""
        try:
            chat_data["timestamp"] = datetime.utcnow()
            await self.chats.insert_one(chat_data)
            return True
        except Exception as e:
            print(f"Error storing chat: {e}")
            return False

    async def store_file_metadata(self, file_data: Dict[str, Any]) -> bool:
        """Store file metadata asynchronously."""
        try:
            file_data["uploaded_at"] = datetime.utcnow()
            await self.files.insert_one(file_data)
            return True
        except Exception as e:
            print(f"Error storing file metadata: {e}")
            return False

    async def get_user(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user data asynchronously."""
        try:
            return await self.users.find_one({"chat_id": chat_id})
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    async def get_chat_history(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent chat history asynchronously."""
        try:
            cursor = self.chats.find({"chat_id": chat_id}).sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    async def get_user_files(self, chat_id: int) -> List[Dict[str, Any]]:
        """Retrieve user-uploaded files asynchronously."""
        try:
            cursor = self.files.find({"chat_id": chat_id}).sort("uploaded_at", -1)
            return await cursor.to_list(length=100)
        except Exception as e:
            print(f"Error getting user files: {e}")
            return []
