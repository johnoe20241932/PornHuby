
import asyncio
import json
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..config import prefixs


scheduled_downloads = {}


@Client.on_message(filters.command("schedule", prefixs) & filters.private)
async def schedule_menu(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏰ Schedule Download", callback_data="schedule_download"),
                InlineKeyboardButton("📅 View Scheduled", callback_data="view_scheduled"),
            ],[
                InlineKeyboardButton("🔄 Auto Download", callback_data="auto_download"),
                InlineKeyboardButton("❌ Cancel All", callback_data="cancel_scheduled"),
            ],
        ]
    )
    
    await update.reply_text(
        "⏰ <b>Download Scheduler</b>\n\n"
        "🚀 Schedule downloads for later\n"
        "🔄 Set up automatic downloads\n"
        "📅 Manage your download queue",
        reply_markup=button
    )


@Client.on_message(filters.command("remind", prefixs) & filters.private)
async def set_reminder(_, update: Message):
    if len(update.command) < 3:
        await update.reply_text(
            "❌ Usage: /remind <minutes> <message>\n\n"
            "Example: /remind 30 Check new uploads"
        )
        return
    
    try:
        minutes = int(update.command[1])
        message = " ".join(update.command[2:])
        
        # Schedule reminder
        asyncio.create_task(send_reminder(update.from_user.id, minutes, message))
        
        await update.reply_text(
            f"⏰ <b>Reminder Set!</b>\n\n"
            f"📝 Message: {message}\n"
            f"⏱️ In: {minutes} minutes"
        )
    except ValueError:
        await update.reply_text("❌ Please provide a valid number of minutes!")


async def send_reminder(user_id, minutes, message):
    await asyncio.sleep(minutes * 60)
    # This would need the client instance to send the reminder
    # Implementation depends on your bot structure


@Client.on_message(filters.command("trending", prefixs) & filters.private)
async def auto_trending(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔥 Daily Trending", callback_data="daily_trending"),
                InlineKeyboardButton("📊 Weekly Top", callback_data="weekly_trending"),
            ],[
                InlineKeyboardButton("🌟 Categories", callback_data="trending_categories"),
                InlineKeyboardButton("⚙️ Settings", callback_data="trending_settings"),
            ],
        ]
    )
    
    await update.reply_text(
        "📈 <b>Trending Content</b>\n\n"
        "🔥 Get daily trending videos\n"
        "📊 Weekly top performers\n"
        "🌟 Category-specific trends",
        reply_markup=button
    )
