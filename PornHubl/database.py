
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, mongo_url: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client.pornhub_bot
        self.users = self.db.users
        self.downloads = self.db.downloads
        self.settings = self.db.settings
        
    async def init_db(self):
        """Initialize database with indexes"""
        try:
            # Create indexes for better performance
            await self.users.create_index("user_id", unique=True)
            await self.downloads.create_index("user_id")
            await self.settings.create_index("user_id", unique=True)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add a new user to database"""
        try:
            user_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "join_date": asyncio.get_event_loop().time(),
                "total_downloads": 0,
                "is_active": True
            }
            await self.users.update_one(
                {"user_id": user_id},
                {"$setOnInsert": user_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        try:
            return await self.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            cursor = self.users.find({"is_active": True})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_user_count(self) -> int:
        """Get total user count"""
        try:
            return await self.users.count_documents({"is_active": True})
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def add_download(self, user_id: int, video_url: str, video_title: str, quality: str = "720"):
        """Add download record"""
        try:
            download_data = {
                "user_id": user_id,
                "video_url": video_url,
                "video_title": video_title,
                "quality": quality,
                "download_date": asyncio.get_event_loop().time(),
            }
            await self.downloads.insert_one(download_data)
            # Update user download count
            await self.users.update_one(
                {"user_id": user_id},
                {"$inc": {"total_downloads": 1}}
            )
            return True
        except Exception as e:
            logger.error(f"Error adding download for user {user_id}: {e}")
            return False
    
    async def get_user_downloads(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user download history"""
        try:
            cursor = self.downloads.find({"user_id": user_id}).sort("download_date", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting downloads for user {user_id}: {e}")
            return []
    
    async def get_download_count(self, user_id: int) -> int:
        """Get user download count"""
        try:
            return await self.downloads.count_documents({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting download count for user {user_id}: {e}")
            return 0
    
    async def clear_user_history(self, user_id: int) -> bool:
        """Clear user download history"""
        try:
            await self.downloads.delete_many({"user_id": user_id})
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"total_downloads": 0}}
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing history for user {user_id}: {e}")
            return False
    
    async def save_user_settings(self, user_id: int, settings: Dict) -> bool:
        """Save user settings"""
        try:
            await self.settings.update_one(
                {"user_id": user_id},
                {"$set": {**settings, "user_id": user_id}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving settings for user {user_id}: {e}")
            return False
    
    async def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        try:
            settings = await self.settings.find_one({"user_id": user_id})
            if settings:
                return settings
            return {"user_id": user_id, "quality": "720", "notifications": True}
        except Exception as e:
            logger.error(f"Error getting settings for user {user_id}: {e}")
            return {"user_id": user_id, "quality": "720", "notifications": True}
    
    async def get_total_downloads(self) -> int:
        """Get total downloads across all users"""
        try:
            return await self.downloads.count_documents({})
        except Exception as e:
            logger.error(f"Error getting total downloads: {e}")
            return 0
    
    async def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Get top users by download count"""
        try:
            cursor = self.users.find({"is_active": True}).sort("total_downloads", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []
