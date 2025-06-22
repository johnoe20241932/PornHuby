
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..config import prefixs, sudoers


@Client.on_message(filters.command("share", prefixs) & filters.private)
async def sharing_options(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📋 Share Playlist", callback_data="share_playlist"),
                InlineKeyboardButton("⭐ Share Favorites", callback_data="share_favorites"),
            ],[
                InlineKeyboardButton("🎯 Quick Share", callback_data="quick_share"),
                InlineKeyboardButton("📊 Share Stats", callback_data="share_stats"),
            ],
        ]
    )
    
    await update.reply_text(
        "📤 <b>Sharing Center</b>\n\n"
        "📋 Share your playlists with friends\n"
        "⭐ Export your favorite videos\n"
        "🎯 Quick share individual videos",
        reply_markup=button
    )


@Client.on_message(filters.command("favorites", prefixs) & filters.private)
async def favorites_menu(_, update: Message):
    user_id = str(update.from_user.id)
    
    try:
        with open(f"favorites_{user_id}.json", "r") as f:
            favorites = json.load(f)
            fav_count = len(favorites.get("videos", []))
    except FileNotFoundError:
        fav_count = 0
    
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐ View Favorites", callback_data="view_favorites"),
                InlineKeyboardButton("➕ Add Current", callback_data="add_favorite"),
            ],[
                InlineKeyboardButton("🗑️ Remove", callback_data="remove_favorite"),
                InlineKeyboardButton("📤 Export", callback_data="export_favorites"),
            ],
        ]
    )
    
    await update.reply_text(
        f"⭐ <b>Your Favorites</b>\n\n"
        f"📹 Saved Videos: <code>{fav_count}</code>\n\n"
        f"💡 Save your best finds for later!",
        reply_markup=button
    )


@Client.on_message(filters.command("leaderboard", prefixs) & filters.private)
async def show_leaderboard(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👑 Top Downloaders", callback_data="top_downloaders"),
                InlineKeyboardButton("🔥 Most Active", callback_data="most_active"),
            ],[
                InlineKeyboardButton("📊 My Rank", callback_data="my_rank"),
                InlineKeyboardButton("🏆 Achievements", callback_data="global_achievements"),
            ],
        ]
    )
    
    await update.reply_text(
        "🏆 <b>Global Leaderboard</b>\n\n"
        "👑 See top users\n"
        "🔥 Most active members\n"
        "📊 Check your ranking\n"
        "🏆 View achievements",
        reply_markup=button
    )


@Client.on_message(filters.command("recommend", prefixs) & filters.private)
async def recommendation_system(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎯 For You", callback_data="recommendations_personal"),
                InlineKeyboardButton("🔥 Trending Now", callback_data="recommendations_trending"),
            ],[
                InlineKeyboardButton("⭐ Top Rated", callback_data="recommendations_rated"),
                InlineKeyboardButton("🆕 New Uploads", callback_data="recommendations_new"),
            ],[
                InlineKeyboardButton("⚙️ Preferences", callback_data="recommendation_settings"),
            ],
        ]
    )
    
    await update.reply_text(
        "🎯 <b>Smart Recommendations</b>\n\n"
        "🤖 AI-powered suggestions based on your activity\n"
        "🔥 Trending content you might like\n"
        "⭐ Top-rated videos in your categories",
        reply_markup=button
    )


@Client.on_message(filters.command("collections", prefixs) & filters.private)
async def collections_menu(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📁 My Collections", callback_data="view_collections"),
                InlineKeyboardButton("➕ New Collection", callback_data="new_collection"),
            ],[
                InlineKeyboardButton("🏷️ By Tags", callback_data="collections_tags"),
                InlineKeyboardButton("👥 Shared", callback_data="shared_collections"),
            ],
        ]
    )
    
    await update.reply_text(
        "📁 <b>Collections Manager</b>\n\n"
        "🗂️ Organize videos into collections\n"
        "🏷️ Tag and categorize content\n"
        "👥 Share collections with others",
        reply_markup=button
    )
