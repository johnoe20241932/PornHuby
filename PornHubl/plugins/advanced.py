
import logging
from typing import Union
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from ..config import prefixs, sub_chat, sudoers

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("premium", prefixs) & filters.private)
async def premium_features(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐ Get Premium", callback_data="get_premium"),
                InlineKeyboardButton("💎 Features", callback_data="premium_features"),
            ],[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
            ],
        ]
    )
    
    text = """
⭐ <b>Premium Features</b>

🚀 <b>Unlock exclusive features:</b>
• 🎥 HD Quality downloads
• ⚡ Faster download speeds
• 📱 Multiple format support
• 🔄 Batch downloads
• 🎯 Priority support
• 📊 Advanced statistics
• 🔔 Custom notifications

💰 <b>Subscription:</b>
Monthly: $4.99
Yearly: $39.99 (Save 33%)
    """
    
    await update.reply_text(text, reply_markup=button)


@Client.on_callback_query(filters.regex("^get_premium$"))
async def get_premium_callback(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💳 Monthly - $4.99", callback_data="sub_monthly"),
                InlineKeyboardButton("💎 Yearly - $39.99", callback_data="sub_yearly"),
            ],[
                InlineKeyboardButton("🔙 Back", callback_data="premium_back"),
            ],
        ]
    )
    
    await query.edit_message_text(
        "💰 <b>Choose your subscription plan:</b>\n\n"
        "🔥 <b>Monthly:</b> $4.99/month\n"
        "💎 <b>Yearly:</b> $39.99/year (Save 33%!)\n\n"
        "Select a plan to continue:",
        reply_markup=button
    )


@Client.on_message(filters.command("analytics", prefixs) & filters.private)
async def user_analytics(_, update: Message):
    user_id = str(update.from_user.id)
    
    try:
        with open(f"history_{user_id}.txt", "r") as file:
            history_lines = file.readlines()
            total_downloads = len([line for line in history_lines if line.startswith("📹")])
    except:
        total_downloads = 0
    
    # Calculate some basic stats
    today_downloads = 0  # You can implement date-based filtering
    week_downloads = 0   # You can implement week-based filtering
    
    stats_text = f"""
📊 <b>Your Analytics</b>

📈 <b>Download Statistics:</b>
• Total Downloads: {total_downloads}
• This Week: {week_downloads}
• Today: {today_downloads}

🎯 <b>Usage Patterns:</b>
• Most Active Time: Evening
• Favorite Category: HD Videos
• Average per Day: {total_downloads // 30 if total_downloads > 0 else 0}

🏆 <b>Your Rank:</b> 
{get_user_rank(total_downloads)}
    """
    
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏆 Achievements", callback_data="achievements"),
                InlineKeyboardButton("📊 Detailed Stats", callback_data="detailed_stats"),
            ],[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
            ]
        ]
    )
    
    await update.reply_text(stats_text, reply_markup=button)


def get_user_rank(downloads):
    if downloads >= 100:
        return "👑 Download Master"
    elif downloads >= 50:
        return "💎 Power User"
    elif downloads >= 10:
        return "🔥 Regular User"
    elif downloads >= 1:
        return "🌟 Beginner"
    else:
        return "🎯 New User"


@Client.on_callback_query(filters.regex("^achievements$"))
async def user_achievements(_, query: CallbackQuery):
    user_id = str(query.from_user.id)
    
    try:
        with open(f"history_{user_id}.txt", "r") as file:
            downloads = len([line for line in file.readlines() if line.startswith("📹")])
    except:
        downloads = 0
    
    achievements = []
    
    if downloads >= 1:
        achievements.append("🎉 First Download")
    if downloads >= 10:
        achievements.append("🔥 Download Enthusiast")
    if downloads >= 50:
        achievements.append("💎 Power User")
    if downloads >= 100:
        achievements.append("👑 Download Master")
    
    if not achievements:
        achievements = ["🎯 Start downloading to unlock achievements!"]
    
    achievement_text = "🏆 <b>Your Achievements</b>\n\n" + "\n".join([f"• {ach}" for ach in achievements])
    
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_analytics")]
    ])
    
    await query.edit_message_text(achievement_text, reply_markup=button)


@Client.on_callback_query(filters.regex("^detailed_stats$"))
async def detailed_statistics(_, query: CallbackQuery):
    user_id = str(query.from_user.id)
    
    stats_text = f"""
📊 <b>Detailed Statistics</b>

👤 <b>User Info:</b>
• User ID: <code>{user_id}</code>
• Member Since: Today
• Status: Active

📈 <b>Download Breakdown:</b>
• HD Downloads: 0
• Standard Downloads: 0
• Mobile Downloads: 0

⏱️ <b>Usage Times:</b>
• Morning (6-12): 0%
• Afternoon (12-18): 0%
• Evening (18-24): 0%
• Night (24-6): 0%
    """
    
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_analytics")]
    ])
    
    await query.edit_message_text(stats_text, reply_markup=button)


@Client.on_callback_query(filters.regex("^back_analytics$"))
async def back_to_analytics(_, query: CallbackQuery):
    # Redirect back to analytics
    await user_analytics(_, query.message)


@Client.on_message(filters.command("feedback", prefixs) & filters.private)
async def user_feedback(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐ Rate Bot", callback_data="rate_bot"),
                InlineKeyboardButton("💬 Send Feedback", callback_data="send_feedback"),
            ],[
                InlineKeyboardButton("🐛 Report Bug", callback_data="report_bug"),
            ],
        ]
    )
    
    await update.reply_text(
        "📝 <b>Feedback & Support</b>\n\n"
        "Help us improve! Your feedback is valuable to us.",
        reply_markup=button
    )


@Client.on_callback_query(filters.regex("^rate_bot$"))
async def rate_bot_callback(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐", callback_data="rate_1"),
                InlineKeyboardButton("⭐⭐", callback_data="rate_2"),
                InlineKeyboardButton("⭐⭐⭐", callback_data="rate_3"),
            ],[
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_4"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_5"),
            ],[
                InlineKeyboardButton("🔙 Back", callback_data="back_feedback"),
            ],
        ]
    )
    
    await query.edit_message_text(
        "⭐ <b>Rate our bot</b>\n\nHow many stars would you give us?",
        reply_markup=button
    )


@Client.on_callback_query(filters.regex("^rate_"))
async def save_rating(_, query: CallbackQuery):
    rating = query.data.split("_")[1]
    user_id = str(query.from_user.id)
    
    # Save rating to file
    try:
        with open(f"rating_{user_id}.txt", "w") as file:
            file.write(f"rating:{rating}\ndate:{datetime.now()}")
    except:
        pass
    
    await query.answer(f"Thanks for rating us {rating} stars!", show_alert=True)
    await query.edit_message_text(f"⭐ Thank you for your {rating}-star rating!")
