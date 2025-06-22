import os
import asyncio
import yt_dlp
import requests

from ..config import log_chat, sub_chat
from .function import download_progress_hook, humanbytes
from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from yt_dlp.utils import DownloadError
from xhamster_api import xhamster_api as XHamsterApi

from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden


if os.path.exists("downloads"):
    print("✅ File is exist")
else:
    print("✅ File has made")


active = []
queues = []


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    if kwargs:
        # For functions that don't accept **kwargs in executor
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return await loop.run_in_executor(None, func, *args)


def url(filter, client, update):
    if "www.pornhub" in update.text or "xhamster.com" in update.text:
        return True
    else:
        return False

def photo_url(filter, client, update):
    if "pornhub.com/photo/" in update.text or "pornhub.com/gif/" in update.text or "xhamster.com/photos/" in update.text:
        return True
    else:
        return False

def xhamster_url(filter, client, update):
    if "xhamster.com" in update.text:
        return True
    else:
        return False

url_filter = filters.create(url, name="url_filter")
photo_filter = filters.create(photo_url, name="photo_filter")
xhamster_filter = filters.create(xhamster_url, name="xhamster_filter")


@Client.on_message(filters.incoming & filters.private, group=-1)
@Client.on_edited_message(filters.incoming & filters.private, group=-1)
async def subscribe_channel(c: Client, u: Message):
    if not sub_chat:
        return
    try:
        try:
            await c.get_chat_member(sub_chat, u.from_user.id)
        except UserNotParticipant:
            if sub_chat.isalpha():
                url = "https://t.me/" + sub_chat
            else:
                chat_info = await c.get_chat(sub_chat)
                url = chat_info.invite_link
            try:
                await u.reply_text(
                    f"Hi {u.from_user.first_name}!\n\nYou must join the redirected channel in order to use this bot, if you've done it, please restart this bot!\n\nUse » /restart",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("• Join Channel •", url=url),
                            ],
                        ],
                    ),
                )
                await u.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        c.send_message(log_chat, "Can't manage the provided channel, make sure I'm the admin on the channel!")


@Client.on_inline_query()
async def inline_search(c: Client, q: InlineQuery):
    query = q.query
    results = []

    # Check if searching xHamster specifically
    if query.lower().startswith("xhamster "):
        search_term = query[9:]  # Remove "xhamster " prefix
        if not search_term.strip():
            results.append(
                InlineQueryResultArticle(
                    title="💡 xHamster Search",
                    description="Please provide a search term after 'xhamster'",
                    input_message_content=InputTextMessageContent(
                        message_text="💡 xHamster Search:\n\nPlease provide a search term!\nExample: xhamster teen"
                    ),
                ),
            )
        else:
            try:
                # Enhanced xHamster search with multiple attempts
                xhamster_videos = None
                attempts = 0
                max_attempts = 3

                while attempts < max_attempts and not xhamster_videos:
                    try:
                        xhamster_videos = await run_async(XHamsterApi.search, search_term, limit=25)
                        break
                    except Exception as e:
                        attempts += 1
                        if attempts < max_attempts:
                            await asyncio.sleep(1)  # Wait before retry
                        else:
                            raise e

                if not xhamster_videos:
                    raise Exception("No results found")

                for i, vid in enumerate(xhamster_videos):
                    try:
                        # Enhanced video info display
                        duration_str = f"{vid.duration//60}:{vid.duration%60:02d}" if vid.duration else "Unknown"
                        views_str = f"{vid.views:,}" if vid.views else "Unknown"

                        # Truncate long titles
                        title = vid.title if len(vid.title) <= 50 else vid.title[:47] + "..."

                        results.append(
                            InlineQueryResultArticle(
                                title=f"🔥 {title}",
                                input_message_content=InputTextMessageContent(
                                    message_text=f"🔥 <b>xHamster Video</b>\n\n📹 <b>Title:</b> {vid.title}\n⏱️ <b>Duration:</b> {duration_str}\n👁️ <b>Views:</b> {views_str}\n\n🔗 <b>URL:</b> {vid.url}",
                                    disable_web_page_preview=True,
                                ),
                                description=f"⏱️ {duration_str} | 👁️ {views_str} views | Quality: HD",
                                thumb_url=vid.thumb if vid.thumb else "https://i.postimg.cc/JhJywSMF/logo7-10-14120.png",
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [
                                            InlineKeyboardButton("🌐 Watch on xHamster", url=vid.url),
                                            InlineKeyboardButton("📥 Download", callback_data=f"xh_download_{i}"),
                                        ],
                                    ],
                                ),
                            ),
                        )
                    except Exception as e:
                        continue

            except Exception as e:
                error_msg = str(e)
                results.append(
                    InlineQueryResultArticle(
                        title="❌ xHamster search failed",
                        description=f"Error: {error_msg[:50]}..." if len(error_msg) > 50 else error_msg,
                        input_message_content=InputTextMessageContent(
                            message_text=f"❌ <b>xHamster search failed</b>\n\n🔧 <b>Error:</b> {error_msg}\n\n💡 <b>Try:</b>\n• Check your spelling\n• Use different keywords\n• Try again later"
                        ),
                    ),
                )
    else:
        # Regular PornHub search
        backend = AioHttpBackend()
        api = PornhubApi(backend=backend)
        try:
            src = await api.search.search(query)
            videos = src.videos
            await backend.close()

            for vid in videos:
                try:
                    pornstars = ", ".join(v for v in vid.pornstars)
                    categories = ", ".join(v for v in vid.categories)
                    tags = ", #".join(v for v in vid.tags)
                except:
                    pornstars = "N/A"
                    categories = "N/A"
                    tags = "N/A"

                text = f"{vid.url}"

                results.append(
                    InlineQueryResultArticle(
                        title=vid.title,
                        input_message_content=InputTextMessageContent(
                            message_text=text, disable_web_page_preview=True,
                        ),
                        description=f"Duration: {vid.duration}\nViews: {vid.views}\nRating: {vid.rating}",
                        thumb_url=vid.thumb,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("Watch in web", url=vid.url),
                                ],
                            ],
                        ),
                    ),
                )
        except ValueError as e:
            results.append(
                InlineQueryResultArticle(
                    title="I can't found it!",
                    description="The video can't be found, try again later.",
                    input_message_content=InputTextMessageContent(
                        message_text="Video not found!"
                    ),
                ),
            )

    if not results:
        results.append(
            InlineQueryResultArticle(
                title="💡 Search Tips",
                description="Use 'xhamster <term>' to search xHamster specifically",
                input_message_content=InputTextMessageContent(
                    message_text="💡 Search Tips:\n\n🔍 Regular search: Just type your keywords\n🔥 xHamster search: Type 'xhamster' followed by your search term\n\nExample: xhamster teen"
                ),
            ),
        )

    await q.answer(
        results,
        switch_pm_text="• Multi-Site Search •",
        switch_pm_parameter="start",
    )


@Client.on_message(url_filter)
async def options(c: Client, m: Message):
    site_name = "xHamster" if "xhamster.com" in m.text else "PornHub"
    emoji = "🔥" if "xhamster.com" in m.text else "📹"

    # Store URL temporarily with user ID and timestamp
    import time
    url_id = f"{m.from_user.id}_{int(time.time())}"

    # Store URL in a temporary file
    with open(f"temp_url_{url_id}.txt", "w") as f:
        f.write(m.text)

    await m.reply_text(
        f"{emoji} {site_name} video detected! Choose an action:", 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"📥 Download from {site_name}", callback_data=f"dl_{url_id}",
                    ),
                ],[
                    InlineKeyboardButton(
                        f"🌐 Watch on {site_name}", url=m.text,
                    ),
                ],
            ],
        ),
    )

@Client.on_message(photo_filter)
async def photo_options(c: Client, m: Message):
    if "/photo/" in m.text or "/photos/" in m.text:
        content_type = "Photo"
    else:
        content_type = "GIF"

    site_name = "xHamster" if "xhamster.com" in m.text else "PornHub"
    emoji = "🔥" if "xhamster.com" in m.text else "📸"

    # Store URL temporarily with user ID and timestamp
    import time
    url_id = f"{m.from_user.id}_{int(time.time())}"

    # Store URL in a temporary file
    with open(f"temp_url_{url_id}.txt", "w") as f:
        f.write(m.text)

    await m.reply_text(
        f"{emoji} {site_name} {content_type} detected! Choose an action:", 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"📥 Download {content_type}", callback_data=f"dph_{url_id}",
                    ),
                ],[
                    InlineKeyboardButton(
                        f"🌐 View on {site_name}", url=m.text,
                    ),
                ],
            ],
        ),
    )


@Client.on_callback_query(filters.regex("^dl_"))
async def get_video(c: Client, q: CallbackQuery):
    url_id = q.data.split("_", 1)[1]

    # Retrieve URL from temporary file
    try:
        with open(f"temp_url_{url_id}.txt", "r") as f:
            url = f.read().strip()
        # Clean up temp file
        import os
        os.remove(f"temp_url_{url_id}.txt")
    except FileNotFoundError:
        await q.message.edit("❌ URL expired or not found. Please send the URL again.")
        return
    msg = await q.message.edit("Downloading...")
    user_id = q.message.from_user.id

    if user_id in active:
        await q.message.edit("Sorry, you can only download one video at a time!")
        return
    else:
        active.append(user_id)

    # Get user quality preference
    quality = "720"
    try:
        with open(f"settings_{user_id}.txt", "r") as file:
            settings = file.read()
            if "quality:" in settings:
                quality = settings.split("quality:")[1].strip()
    except:
        pass

    ydl_opts = {
        "format": f"best[height<={quality}]",
        "writethumbnail": True,
        "writeinfojson": True,
        "outtmpl": "%(title)s.%(ext)s",
        "progress_hooks": [lambda d: download_progress_hook(d, q.message, c)]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract video info first
            info = await run_async(ydl.extract_info, url, False)
            video_title = info.get('title', 'Unknown')
            thumbnail_url = info.get('thumbnail', '')
            duration = info.get('duration', 0)
            view_count = info.get('view_count', 0)

            # Download video with thumbnail
            await run_async(ydl.download, [url])

            # Save to download history
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            site_emoji = "🔥" if "xhamster.com" in url else "📹"
            site_name = "xHamster" if "xhamster.com" in url else "PornHub"
            with open(f"history_{user_id}.txt", "a") as file:
                file.write(f"{site_emoji} {video_title} ({site_name})\n🔗 {url}\n⏰ {timestamp}\n\n")

        except DownloadError:
            await q.message.edit("Sorry, an error occurred during download")
            active.remove(user_id)
            return

    # Find and upload video with thumbnail
    video_file = None
    thumb_file = None

    for file in os.listdir('.'):
        if file.endswith(".mp4"):
            video_file = file
        elif file.endswith((".jpg", ".jpeg", ".png", ".webp")) and "thumbnail" not in file.lower():
            thumb_file = file

    if video_file:
        # Create custom thumbnail if available, otherwise use default
        thumbnail_path = thumb_file if thumb_file and os.path.exists(thumb_file) else "downloads/src/pornhub.jpeg"

        # Format duration for display
        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
        view_str = f"{view_count:,}" if view_count else "Unknown"

        await q.message.reply_video(
            video_file,
            thumb=thumbnail_path,
            width=1280,
            height=720,
            duration=duration if duration else None,
            caption=f"✅ <b>Download Complete!</b>\n\n📹 <b>Title:</b> {video_title}\n📱 <b>Quality:</b> {quality}p\n⏱️ <b>Duration:</b> {duration_str}\n👁️ <b>Views:</b> {view_str}\n\n💝 Enjoy your content!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("• Donate •", url="https://t.me/IamOkayy"),
                        InlineKeyboardButton("⭐ Rate Us", callback_data="rate_bot"),
                    ],
                ],
            ),
        )

        # Clean up downloaded files
        os.remove(video_file)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)

        # Clean up any additional files (info.json, etc.)
        for file in os.listdir('.'):
            if file.endswith(('.info.json', '.description')):
                try:
                    os.remove(file)
                except:
                    pass

    await msg.delete()
    active.remove(user_id)


@Client.on_callback_query(filters.regex("^rate_bot$"))
async def rate_bot(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐", callback_data="rate_1"),
                InlineKeyboardButton("⭐⭐", callback_data="rate_2"),
                InlineKeyboardButton("⭐⭐⭐", callback_data="rate_3"),
            ],[
                InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_4"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_5"),
            ],
        ]
    )
    await query.edit_message_text("⭐ <b>Rate your experience:</b>", reply_markup=button)


@Client.on_callback_query(filters.regex("^rate_"))
async def save_rating(_, query: CallbackQuery):
    rating = query.data.split("_")[1]
    await query.answer(f"Thanks for rating {rating} stars!")
    await query.edit_message_text(f"⭐ Thank you for rating us {rating} stars!")


@Client.on_callback_query(filters.regex("^dph_"))
async def download_photo_gif(c: Client, q: CallbackQuery):
    url_id = q.data.split("_", 1)[1]

    # Retrieve URL from temporary file
    try:
        with open(f"temp_url_{url_id}.txt", "r") as f:
            url = f.read().strip()
        # Clean up temp file
        import os
        os.remove(f"temp_url_{url_id}.txt")
    except FileNotFoundError:
        await q.message.edit("❌ URL expired or not found. Please send the URL again.")
        return
    user_id = q.message.from_user.id

    if user_id in active:
        await q.message.edit("Sorry, you can only download one item at a time!")
        return
    else:
        active.append(user_id)

    msg = await q.message.edit("📸 Downloading...")

    try:
        import requests
        from urllib.parse import urlparse
        import mimetypes

        # Extract image/gif URL from PornHub page
        response = requests.get(url)
        response.raise_for_status()

        content = response.text

        # Look for image/gif URLs in the page content
        import re

        if "/photo/" in url:
            # For photos, look for high-res image URLs
            img_pattern = r'<img[^>]+src="([^"]*(?:\.jpg|\.jpeg|\.png|\.webp)[^"]*)"[^>]*>'
            matches = re.findall(img_pattern, content, re.IGNORECASE)

            # Filter for actual content images (not thumbnails or UI elements)
            image_urls = [match for match in matches if 'phncdn.com' in match and 'thumb' not in match]

        else:
            # For GIFs, look for .gif URLs
            gif_pattern = r'<[^>]+(?:src|href)="([^"]*\.gif[^"]*)"[^>]*>'
            matches = re.findall(gif_pattern, content, re.IGNORECASE)
            image_urls = [match for match in matches if 'phncdn.com' in match]

        if not image_urls:
            await msg.edit("❌ Could not find downloadable content on this page!")
            active.remove(user_id)
            return

        # Download the best quality image/gif
        download_url = image_urls[0]  # Usually the first one is highest quality

        # Get file extension
        parsed_url = urlparse(download_url)
        file_extension = os.path.splitext(parsed_url.path)[1]
        if not file_extension:
            file_extension = '.jpg' if '/photo/' in url else '.gif'

        # Generate filename
        filename = f"download_{user_id}_{int(asyncio.get_event_loop().time())}{file_extension}"

        # Download the file
        await msg.edit("📥 Downloading content...")

        img_response = requests.get(download_url, stream=True)
        img_response.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in img_response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Get file size
        file_size = os.path.getsize(filename)

        # Send the downloaded content
        content_type = "Photo" if "/photo/" in url else "GIF"
        caption = f"✅ <b>{content_type} Downloaded!</b>\n\n📁 <b>Size:</b> {humanbytes(file_size)}\n🔗 <b>Source:</b> PornHub\n\n💝 Enjoy your content!"

        if file_extension.lower() in ['.gif']:
            await q.message.reply_animation(
                filename,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("• Donate •", url="https://t.me/IamOkayy"),
                            InlineKeyboardButton("⭐ Rate Us", callback_data="rate_bot"),
                        ],
                    ],
                ),
            )
        else:
            await q.message.reply_photo(
                filename,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("• Donate •", url="https://t.me/IamOkayy"),
                            InlineKeyboardButton("⭐ Rate Us", callback_data="rate_bot"),
                        ],
                    ],
                ),
            )

        # Save to download history
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        site_emoji = "🔥" if "xhamster.com" in url else "📸"
        site_name = "xHamster" if "xhamster.com" in url else "PornHub"
        with open(f"history_{user_id}.txt", "a") as file:
            file.write(f"{site_emoji} {content_type} Download ({site_name})\n🔗 {url}\n⏰ {timestamp}\n\n")

        # Clean up
        os.remove(filename)

    except Exception as e:
        await msg.edit(f"❌ Error downloading content: {str(e)}")
        print(f"Error downloading photo/gif: {e}")

    await msg.delete()
    active.remove(user_id)