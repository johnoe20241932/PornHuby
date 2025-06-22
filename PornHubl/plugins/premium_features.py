
import json
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..config import prefixs


premium_users = set()  # In production, use database


def is_premium_user(user_id):
    return str(user_id) in premium_users


@Client.on_message(filters.command("premium", prefixs) & filters.private)
async def premium_menu(_, update: Message):
    user_id = str(update.from_user.id)
    is_premium = is_premium_user(user_id)
    
    if is_premium:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚡ HD Downloads", callback_data="premium_hd"),
                    InlineKeyboardButton("📦 Batch Download", callback_data="premium_batch"),
                ],[
                    InlineKeyboardButton("🔍 Advanced Search", callback_data="premium_search"),
                    InlineKeyboardButton("📊 Analytics Pro", callback_data="premium_analytics"),
                ],[
                    InlineKeyboardButton("🎵 Playlist Pro", callback_data="premium_playlist"),
                    InlineKeyboardButton("⚙️ Premium Settings", callback_data="premium_settings"),
                ],
            ]
        )
        
        text = "💎 <b>Premium Dashboard</b>\n\n✅ Premium Active\n\n🚀 Access all premium features!"
    else:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("💎 Get Premium", callback_data="get_premium"),
                    InlineKeyboardButton("🎁 Free Trial", callback_data="free_trial"),
                ],[
                    InlineKeyboardButton("💰 Pricing", callback_data="premium_pricing"),
                    InlineKeyboardButton("🔥 Features", callback_data="premium_features_list"),
                ],
            ]
        )
        
        text = "⭐ <b>Upgrade to Premium</b>\n\n🚀 Unlock exclusive features:\n• ⚡ 4K HD Downloads\n• 📦 Unlimited Batch Downloads\n• 🔍 Advanced Search Filters\n• 📊 Detailed Analytics\n• 🎵 Unlimited Playlists\n• ⚡ Priority Support"
    
    await update.reply_text(text, reply_markup=button)


@Client.on_message(filters.command("vip", prefixs) & filters.private)
async def vip_features(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👑 VIP Status", callback_data="vip_status"),
                InlineKeyboardButton("🎯 Custom AI", callback_data="vip_ai"),
            ],[
                InlineKeyboardButton("📱 Mobile App", callback_data="vip_app"),
                InlineKeyboardButton("🎨 Custom Themes", callback_data="vip_themes"),
            ],[
                InlineKeyboardButton("💬 Priority Support", callback_data="vip_support"),
            ],
        ]
    )
    
    await update.reply_text(
        "👑 <b>VIP Membership</b>\n\n"
        "🌟 The ultimate experience:\n"
        "• 🤖 Personal AI Assistant\n"
        "• 📱 Exclusive Mobile App\n"
        "• 🎨 Custom Themes & UI\n"
        "• 💬 24/7 Priority Support\n"
        "• 🔒 Enhanced Privacy Features",
        reply_markup=button
    )


@Client.on_callback_query(filters.regex("^get_premium$"))
async def initiate_premium_purchase(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💳 Monthly $4.99", callback_data="buy_monthly"),
                InlineKeyboardButton("💎 Yearly $39.99", callback_data="buy_yearly"),
            ],[
                InlineKeyboardButton("🎁 Try Free", callback_data="start_trial"),
                InlineKeyboardButton("🔙 Back", callback_data="back_premium"),
            ],
        ]
    )
    
    await query.edit_message_text(
        "💰 <b>Choose Your Plan</b>\n\n"
        "💳 <b>Monthly:</b> $4.99/month\n"
        "• Cancel anytime\n"
        "• All premium features\n\n"
        "💎 <b>Yearly:</b> $39.99/year\n"
        "• Save 33%! ($59.88 → $39.99)\n"
        "• All premium features\n"
        "• Priority support",
        reply_markup=button
    )


@Client.on_message(filters.command("trial", prefixs) & filters.private)
async def free_trial_info(_, update: Message):
    user_id = str(update.from_user.id)
    
    # Check if user already used trial
    try:
        with open(f"trial_{user_id}.json", "r") as f:
            trial_data = json.load(f)
            await update.reply_text("❌ You've already used your free trial!")
            return
    except FileNotFoundError:
        pass
    
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎁 Start 7-Day Trial", callback_data="start_free_trial"),
            ],[
                InlineKeyboardButton("📋 Terms", callback_data="trial_terms"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_trial"),
            ],
        ]
    )
    
    await update.reply_text(
        "🎁 <b>Free 7-Day Trial</b>\n\n"
        "✅ All premium features\n"
        "✅ No credit card required\n"
        "✅ Cancel anytime\n\n"
        "🚀 Start your trial now!",
        reply_markup=button
    )
