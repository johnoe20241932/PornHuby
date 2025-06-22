
import os
import json
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..config import prefixs


# Playlist management functions
def load_playlist(user_id):
    try:
        with open(f"playlist_{user_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"videos": [], "created": datetime.now().isoformat()}


def save_playlist(user_id, playlist):
    with open(f"playlist_{user_id}.json", "w") as f:
        json.dump(playlist, f, indent=2)


@Client.on_message(filters.command("playlist", prefixs) & filters.private)
async def playlist_menu(_, update: Message):
    user_id = str(update.from_user.id)
    playlist = load_playlist(user_id)
    video_count = len(playlist["videos"])
    
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📋 View Playlist", callback_data="view_playlist"),
                InlineKeyboardButton("➕ Add Video", callback_data="add_to_playlist"),
            ],[
                InlineKeyboardButton("🗑️ Clear Playlist", callback_data="clear_playlist"),
                InlineKeyboardButton("📤 Share Playlist", callback_data="share_playlist"),
            ],[
                InlineKeyboardButton("📥 Download All", callback_data="download_all_playlist"),
            ],
        ]
    )
    
    await update.reply_text(
        f"🎵 <b>Your Playlist</b>\n\n"
        f"📹 Videos: <code>{video_count}</code>\n"
        f"📅 Created: <code>{playlist['created'][:10]}</code>\n\n"
        f"💡 Add videos by sending URLs or use /add_playlist <url>",
        reply_markup=button
    )


@Client.on_callback_query(filters.regex("^view_playlist$"))
async def view_playlist(_, query: CallbackQuery):
    user_id = str(query.from_user.id)
    playlist = load_playlist(user_id)
    
    if not playlist["videos"]:
        await query.edit_message_text("📭 Your playlist is empty!\n\nSend video URLs to add them.")
        return
    
    playlist_text = "🎵 <b>Your Playlist</b>\n\n"
    for i, video in enumerate(playlist["videos"][:10], 1):
        title = video["title"][:30] + "..." if len(video["title"]) > 30 else video["title"]
        playlist_text += f"{i}. 📹 {title}\n"
    
    if len(playlist["videos"]) > 10:
        playlist_text += f"\n... and {len(playlist['videos']) - 10} more videos"
    
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_playlist_menu")]
    ])
    
    await query.edit_message_text(playlist_text, reply_markup=button)


@Client.on_message(filters.command("add_playlist", prefixs) & filters.private)
async def add_to_playlist_cmd(_, update: Message):
    if len(update.command) < 2:
        await update.reply_text("❌ Usage: /add_playlist <video_url>")
        return
    
    url = update.command[1]
    user_id = str(update.from_user.id)
    playlist = load_playlist(user_id)
    
    # Simple title extraction (you can enhance this)
    title = f"Video {len(playlist['videos']) + 1}"
    
    video_data = {
        "url": url,
        "title": title,
        "added_date": datetime.now().isoformat(),
        "site": "xHamster" if "xhamster.com" in url else "PornHub"
    }
    
    playlist["videos"].append(video_data)
    save_playlist(user_id, playlist)
    
    await update.reply_text(f"✅ Added to playlist!\n\n📹 <b>Title:</b> {title}\n🔗 <b>URL:</b> {url}")


@Client.on_message(filters.command("batch", prefixs) & filters.private)
async def batch_download(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📋 From Playlist", callback_data="batch_playlist"),
                InlineKeyboardButton("📝 From List", callback_data="batch_list"),
            ],[
                InlineKeyboardButton("📊 Batch Status", callback_data="batch_status"),
            ],
        ]
    )
    
    await update.reply_text(
        "⚡ <b>Batch Download</b>\n\n"
        "🚀 Download multiple videos at once!\n\n"
        "📋 From Playlist: Download your saved playlist\n"
        "📝 From List: Send multiple URLs",
        reply_markup=button
    )
