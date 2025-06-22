
import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..config import prefixs


@Client.on_message(filters.command("convert", prefixs) & filters.private)
async def media_converter(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎥 Video to GIF", callback_data="convert_gif"),
                InlineKeyboardButton("🔊 Extract Audio", callback_data="extract_audio"),
            ],[
                InlineKeyboardButton("📱 Compress Video", callback_data="compress_video"),
                InlineKeyboardButton("✂️ Trim Video", callback_data="trim_video"),
            ],[
                InlineKeyboardButton("🖼️ Extract Frames", callback_data="extract_frames"),
                InlineKeyboardButton("📊 Video Info", callback_data="video_info"),
            ],
        ]
    )
    
    await update.reply_text(
        "🛠️ <b>Media Tools</b>\n\n"
        "🎥 Convert videos to different formats\n"
        "🔊 Extract audio from videos\n"
        "📱 Compress and optimize files\n"
        "✂️ Trim and edit videos",
        reply_markup=button
    )


@Client.on_message(filters.command("compress", prefixs) & filters.private)
async def compression_options(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📱 Mobile (480p)", callback_data="compress_480"),
                InlineKeyboardButton("💻 Desktop (720p)", callback_data="compress_720"),
            ],[
                InlineKeyboardButton("🎯 Custom Quality", callback_data="compress_custom"),
                InlineKeyboardButton("📊 File Size Limit", callback_data="compress_size"),
            ],
        ]
    )
    
    await update.reply_text(
        "📱 <b>Video Compression</b>\n\n"
        "Choose compression level:\n"
        "📱 Mobile: Smaller file, good for phones\n"
        "💻 Desktop: Balanced quality and size\n"
        "🎯 Custom: Set your own parameters",
        reply_markup=button
    )


@Client.on_message(filters.command("gif", prefixs) & filters.private)
async def gif_converter(_, update: Message):
    await update.reply_text(
        "🎬 <b>GIF Converter</b>\n\n"
        "📤 Send me a video to convert to GIF!\n\n"
        "⚙️ <b>Options:</b>\n"
        "• Duration: 1-10 seconds\n"
        "• Quality: High/Medium/Low\n"
        "• Size: Optimized for Telegram"
    )


@Client.on_message(filters.video & filters.private)
async def process_uploaded_video(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎬 Convert to GIF", callback_data="process_gif"),
                InlineKeyboardButton("🔊 Extract Audio", callback_data="process_audio"),
            ],[
                InlineKeyboardButton("📱 Compress", callback_data="process_compress"),
                InlineKeyboardButton("📊 Get Info", callback_data="process_info"),
            ],
        ]
    )
    
    await update.reply_text(
        "🎥 <b>Video Received!</b>\n\nWhat would you like to do with it?",
        reply_markup=button
    )
