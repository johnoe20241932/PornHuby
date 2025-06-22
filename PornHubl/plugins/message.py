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


sudofilter = filters.user(sudoers)

button_a1 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="✅ Agree & Continue",
                callback_data="final_page",
            )
        ],[
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="home_intro",
            ),
        ],
    ]
)


button_a2 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Search here", switch_inline_query_current_chat="",
            )
        ],[
            InlineKeyboardButton(
                text="Search in chat", switch_inline_query="",
            ),
        ],
    ]
)


@Client.on_message(filters.command(["start", "restart"], prefixs) & filters.private)
async def intro_msg(client: Client, update: Message):
    try:
        # Check if user is member of the required channel
        try:
            member = await client.get_chat_member(sub_chat, update.from_user.id)
            if member.status in ["kicked", "left"]:
                button = InlineKeyboardMarkup([
                    [InlineKeyboardButton("• Join Channel •", url=f"https://t.me/{sub_chat}")],
                    [InlineKeyboardButton("✅ Check Again", callback_data="check_membership")]
                ])
                await update.reply_text(
                    "❌ You must join our channel first to use this bot!",
                    reply_markup=button
                )
                return
        except Exception:
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("• Join Channel •", url=f"https://t.me/{sub_chat}")],
                [InlineKeyboardButton("✅ Check Again", callback_data="check_membership")]
            ])
            await update.reply_text(
                "❌ You must join our channel first to use this bot!",
                reply_markup=button
            )
            return

        # Log user
        match = str(update.chat.id)
        try:
            with open("users.txt", "a+") as file:
                file.seek(0)
                line = file.read().splitlines()
                if match in line:
                    print(f"User {match} is using the bot")
                else:
                    file.write(match + "\n")
        except Exception as e:
            print(f"Error logging user: {e}")

        # Send welcome message
        text = f"👋🏻 Hi {update.from_user.first_name}!\n\nUse this bot to download videos from PornHub and xHamster by providing video URLs or search using inline mode.\n\n🔥 <b>New:</b> xHamster support added!\n💡 <b>Tip:</b> Use 'xhamster <search term>' in inline mode\n\n💭 Join the redirected channel to use this bot!"
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Channel •", url=f"https://t.me/{sub_chat}",
                    )
                ],[
                    InlineKeyboardButton(
                        "Terms of use & Privacy", callback_data="terms",
                    ),
                ],
            ]
        )
        await update.reply_text(text, reply_markup=button)
    except Exception as e:
        await update.reply_text("❌ An error occurred. Please try again later.")
        print(f"Error in start command: {e}")


@Client.on_callback_query(filters.regex("^home_intro$"))
async def home_page(_, update: CallbackQuery):
    await update.answer("Accept the policy in order to continue!")
    method = update.edit_message_text
    text = f"👋🏻 Hi {update.from_user.first_name}!\n\nUse this bot to download videos from PornHub and xHamster by providing video URLs or search using inline mode.\n\n🔥 <b>New:</b> xHamster support added!\n💡 <b>Tip:</b> Use 'xhamster <search term>' in inline mode\n\n💭 Join the redirected channel to use this bot!"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "• Channel •", url=f"https://t.me/{sub_chat}",
                )
            ],[
                InlineKeyboardButton(
                    "Terms of use & Privacy", callback_data="terms",
                ),
            ],
        ]
    )
    await method(text, reply_markup=button)


@Client.on_callback_query(filters.regex("^terms$"))
async def terms_panel(_, q: CallbackQuery):
    await q.answer("Read the terms of use & user privacy!")
    text = """
🧸 <u><b>PornHub bot</b></u>
⚠️ <b>WARNING !</b>
This bot contains 18+ content, make sure you are an adult user to be able to use this bot!. Reporting this bot will get it blocked by Telegram, so if you're considering sticking with bots, don't do it!
🔐 <b>Privacy Policy</b>
We ensure that your search data in this bot is protected safely.  Whoever you are, whenever and wherever you use this bot to download videos from pornhub, you don't have to be afraid of spreading it to the public.
<i>You don't have to worry, because our bot staff will make sure that your data is well protected and safe.</i>
👉🏻 Press the <b>green button</b> to declare that you have <b>read and accepted these conditions</b> to use this bot, otherwise cancel.
    """
    await q.edit_message_text(text, reply_markup=button_a1)


@Client.on_callback_query(filters.regex("^final_page$"))
async def greets(_, q: CallbackQuery):
    await q.answer("Thanks for agreeing to the bot policy!")
    await q.edit_message_text(
        f"Hi {q.from_user.first_name}!\n\nYou can browse this bot now, just tap one of the button below and enter any name of the video you want to download.",
        reply_markup=button_a2,
    )


@Client.on_message(filters.command("stats", prefixs) & sudofilter)
async def bot_statistic(c: Client, u: Message):
    users = open("users.txt").readlines()
    total = len(users)
    await c.send_document(
        u.chat.id,
        "users.txt", caption=f"total: {total} users",
    )


@Client.on_message(filters.command(["gcast", "broadcast"], prefixs) & sudofilter)
async def broadcast(_, update: Message):
    if not update.reply_to_message:
        await update.reply_text("Reply to message for broadcast!")
        return
    if update.reply_to_message.text:
        await update.reply_text("✅ Broadcast success!")
        query = open("users.txt").readlines()
        for row in query:
            try:
                resp = update.reply_to_message
                await resp.copy(row)
            except Exception:
                pass
    else:
        await update.reply_text("Other message type like sticker, photo, etc; are not supported!")


@Client.on_message(filters.command("help", prefixs))
async def command_list(_, update: Message):
    text_1 = """
🛠 <b>Command list:</b>

🚀 <b>Basic Commands:</b>
» /start - start this bot
» /help  - showing this message
» /ping  - check bot status
» /search <keyword> - search for videos
» /trending - view trending videos

👤 <b>User Commands:</b>
» /history - view download history
» /clear - clear download history
» /settings - user preferences

📱 <b>Usage:</b>
• Send PornHub or xHamster video URLs to download
• Send photo/GIF URLs to download images
• Inline search: @botusername <query>
• xHamster search: @botusername xhamster <query>

🎯 <b>Supported Sites:</b>
• 📹 PornHub (Videos, Photos, GIFs)
• 🔥 xHamster (Videos, Photos)

💾 <b>Supported Formats:</b>
• 📹 Videos (MP4)
• 📸 Photos (JPG, PNG, WEBP)
• 🎬 GIFs (Animated)
    """
    text_2 = """
🛠 <b>Command list:</b>

🚀 <b>Basic Commands:</b>
» /start - start this bot
» /help  - showing this message
» /ping  - check bot status
» /search <keyword> - search for videos
» /trending - view trending videos

👤 <b>User Commands:</b>
» /history - view download history
» /clear - clear download history
» /settings - user preferences

🔐 <b>Admin Commands:</b>
» /stats - show bot statistic
» /gcast - broadcast message
» /admin - admin panel

📱 <b>Usage:</b>
• Send PornHub or xHamster video URLs to download
• Send photo/GIF URLs to download images
• Inline search: @botusername <query>
• xHamster search: @botusername xhamster <query>

🎯 <b>Supported Sites:</b>
• 📹 PornHub (Videos, Photos, GIFs)
• 🔥 xHamster (Videos, Photos)

💾 <b>Supported Formats:</b>
• 📹 Videos (MP4)
• 📸 Photos (JPG, PNG, WEBP)
• 🎬 GIFs (Animated)
    """
    if update.from_user.id in sudoers:
        await update.reply_text(text_2)
    else:
        await update.reply_text(text_1)


@Client.on_message(filters.command("ping", prefixs))
async def ping(c: Client, u: Message):
    first = datetime.now()
    sent = await u.reply_text("<b>pinging...</b>")
    second = datetime.now()
    await sent.edit_text(
       f"🏓 <b>PONG !</b>\n⏱ <code>{(second - first).microseconds / 1000}</code> ms"
    )


@Client.on_message(filters.command("history", prefixs) & filters.private)
async def download_history(_, update: Message):
    user_id = str(update.from_user.id)
    try:
        with open(f"history_{user_id}.txt", "r") as file:
            history = file.read().strip()
            if history:
                await update.reply_text(f"📚 <b>Your Download History:</b>\n\n{history}")
            else:
                await update.reply_text("📭 No download history found!")
    except FileNotFoundError:
        await update.reply_text("📭 No download history found!")


@Client.on_message(filters.command("clear", prefixs) & filters.private)
async def clear_history(_, update: Message):
    user_id = str(update.from_user.id)
    try:
        open(f"history_{user_id}.txt", "w").close()
        await update.reply_text("🗑️ Download history cleared!")
    except:
        await update.reply_text("❌ Error clearing history!")


@Client.on_message(filters.command("settings", prefixs) & filters.private)
async def user_settings(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔔 Notifications", callback_data="toggle_notif"),
                InlineKeyboardButton("📱 Quality", callback_data="set_quality"),
            ],[
                InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
                InlineKeyboardButton("❌ Close", callback_data="close_menu"),
            ],
        ]
    )
    await update.reply_text("⚙️ <b>User Settings</b>\n\nChoose an option:", reply_markup=button)


@Client.on_callback_query(filters.regex("^toggle_notif$"))
async def toggle_notifications(_, query: CallbackQuery):
    await query.answer("Notifications toggled!")
    await query.edit_message_text("🔔 Notifications have been toggled!")


@Client.on_callback_query(filters.regex("^set_quality$"))
async def set_quality(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("720p", callback_data="quality_720"),
                InlineKeyboardButton("480p", callback_data="quality_480"),
            ],[
                InlineKeyboardButton("360p", callback_data="quality_360"),
                InlineKeyboardButton("🔙 Back", callback_data="back_settings"),
            ],
        ]
    )
    await query.edit_message_text("📱 <b>Select Video Quality:</b>", reply_markup=button)


@Client.on_callback_query(filters.regex("^quality_"))
async def save_quality(_, query: CallbackQuery):
    quality = query.data.split("_")[1]
    user_id = str(query.from_user.id)
    with open(f"settings_{user_id}.txt", "w") as file:
        file.write(f"quality:{quality}")
    await query.answer(f"Quality set to {quality}p!")
    await query.edit_message_text(f"✅ Video quality set to {quality}p")


@Client.on_callback_query(filters.regex("^user_stats$"))
async def user_statistics(_, query: CallbackQuery):
    user_id = str(query.from_user.id)
    try:
        with open(f"history_{user_id}.txt", "r") as file:
            downloads = len(file.readlines())
    except:
        downloads = 0

    stats_text = f"📊 <b>Your Statistics:</b>\n\n👤 User ID: <code>{user_id}</code>\n📥 Downloads: <code>{downloads}</code>\n📅 Member since: Today"
    await query.edit_message_text(stats_text)


@Client.on_callback_query(filters.regex("^check_membership$"))
async def check_membership(client: Client, query: CallbackQuery):
    try:
        member = await client.get_chat_member(sub_chat, query.from_user.id)
        if member.status not in ["kicked", "left"]:
            text = f"👋🏻 Hi {query.from_user.first_name}!\n\nUse this bot to download videos from the pornhub.com site by providing the name of the video you want to download or you can also search for the video you want to download via inline mode.\n\n💭 Join the redirected channel in order to use this bot!"
            button = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Channel •", url=f"https://t.me/{sub_chat}",
                        )
                    ],[
                        InlineKeyboardButton(
                            "Terms of use & Privacy", callback_data="terms",
                        ),
                    ],
                ]
            )
            await query.edit_message_text(text, reply_markup=button)
        else:
            await query.answer("❌ Please join the channel first!", show_alert=True)
    except Exception:
        await query.answer("❌ Please join the channel first!", show_alert=True)


@Client.on_callback_query(filters.regex("^close_menu$|^back_settings$"))
async def close_or_back(_, query: CallbackQuery):
    if query.data == "close_menu":
        await query.message.delete()
    else:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔔 Notifications", callback_data="toggle_notif"),
                    InlineKeyboardButton("📱 Quality", callback_data="set_quality"),
                ],[
                    InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
                    InlineKeyboardButton("❌ Close", callback_data="close_menu"),
                ],
            ]
        )
        await query.edit_message_text("⚙️ <b>User Settings</b>\n\nChoose an option:", reply_markup=button)


@Client.on_message(filters.command("xhamster", prefixs) & filters.private)
async def xhamster_search(_, update: Message):
    if len(update.command) < 2:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔥 Search xHamster", switch_inline_query_current_chat="xhamster "),
                    InlineKeyboardButton("🔥 Trending", switch_inline_query_current_chat="xhamster trending"),
                ],[
                    InlineKeyboardButton("🔥 Categories", callback_data="xh_categories"),
                    InlineKeyboardButton("💡 Tips", callback_data="xh_tips"),
                ],
            ]
        )
        await update.reply_text(
            "🔥 <b>xHamster Search</b>\n\n"
            "❌ Please provide a search term!\n\n"
            "<b>Usage:</b> /xhamster <keyword>\n"
            "<b>Example:</b> /xhamster teen",
            reply_markup=button
        )
        return

    query = " ".join(update.command[1:])
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"🔥 Search: {query[:20]}{'...' if len(query) > 20 else ''}", 
                    switch_inline_query_current_chat=f"xhamster {query}"
                )
            ],[
                InlineKeyboardButton("🔄 New Search", switch_inline_query_current_chat="xhamster "),
                InlineKeyboardButton("🔥 Trending", switch_inline_query_current_chat="xhamster trending"),
            ],
        ]
    )
    await update.reply_text(f"🔥 <b>Searching xHamster for:</b> <code>{query}</code>", reply_markup=button)


@Client.on_message(filters.command("admin", prefixs) & sudofilter)
async def admin_panel(_, update: Message):
    users = open("users.txt").readlines()
    total_users = len(users)

    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📊 Bot Stats", callback_data="bot_stats"),
                InlineKeyboardButton("📢 Broadcast", callback_data="start_broadcast"),
            ],[
                InlineKeyboardButton("👥 User List", callback_data="user_list"),
                InlineKeyboardButton("🔧 Maintenance", callback_data="maintenance"),
            ],
        ]
    )
    await update.reply_text(f"🔐 <b>Admin Panel</b>\n\n👥 Total Users: {total_users}", reply_markup=button)


@Client.on_callback_query(filters.regex("^bot_stats$"))
async def bot_statistics(_, query: CallbackQuery):
    users = open("users.txt").readlines()
    total_users = len(users)

    import psutil
    import platform

    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    stats = f"""📊 <b>Bot Statistics</b>

👥 <b>Users:</b> {total_users}
🖥️ <b>System:</b> {platform.system()}
💾 <b>CPU Usage:</b> {cpu_usage}%
🗄️ <b>RAM Usage:</b> {memory.percent}%
💽 <b>Disk Usage:</b> {disk.percent}%
"""
    await query.edit_message_text(stats)


@Client.on_message(filters.command("search", prefixs) & filters.private)
async def search_videos(_, update: Message):
    if len(update.command) < 2:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📹 PornHub Search", switch_inline_query_current_chat=""),
                    InlineKeyboardButton("🔥 xHamster Search", switch_inline_query_current_chat="xhamster "),
                ],[
                    InlineKeyboardButton("🔥 Trending", switch_inline_query_current_chat="trending"),
                    InlineKeyboardButton("💡 Search Tips", callback_data="search_tips"),
                ],
            ]
        )
        await update.reply_text(
            "🔍 <b>Multi-Site Search</b>\n\n"
            "❌ Please provide a search term!\n\n"
            "<b>Usage:</b> /search <keyword>\n"
            "<b>Example:</b> /search amateur",
            reply_markup=button
        )
        return

    query = " ".join(update.command[1:])
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"📹 PornHub: {query[:15]}{'...' if len(query) > 15 else ''}", 
                                   switch_inline_query_current_chat=query),
                InlineKeyboardButton(f"🔥 xHamster: {query[:15]}{'...' if len(query) > 15 else ''}", 
                                   switch_inline_query_current_chat=f"xhamster {query}"),
            ],[
                InlineKeyboardButton("🔄 New Search", switch_inline_query_current_chat=""),
                InlineKeyboardButton("🔥 Trending", switch_inline_query_current_chat="trending"),
            ],
        ]
    )
    await update.reply_text(f"🔍 <b>Multi-Site Search for:</b> <code>{query}</code>\n\nChoose your preferred site:", reply_markup=button)


@Client.on_callback_query(filters.regex("^search_tips$"))
async def search_tips(_, query: CallbackQuery):
    tips_text = """
💡 <b>Search Tips & Tricks</b>

🌐 <b>Multi-Site Search:</b>
• 📹 PornHub - Largest collection
• 🔥 xHamster - HD quality content

🔍 <b>Search Methods:</b>
• <code>/search [keyword]</code> - Multi-site search
• <code>/xhamster [keyword]</code> - xHamster only
• <code>@botname [keyword]</code> - Inline PornHub
• <code>@botname xhamster [keyword]</code> - Inline xHamster

🎯 <b>Popular Categories:</b>
• teen, milf, amateur, mature
• anal, oral, threesome, lesbian
• hd, 4k, vr, premium

⚡ <b>Search Tips:</b>
• Use specific keywords for better results
• Try different word combinations
• Use categories for quick results
• Check trending for popular content

📱 <b>Download Features:</b>
• Multiple quality options (360p-720p)
• Photo and GIF downloads
• Download history tracking
• Batch downloads (Premium)
    """
    
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔍 Start Search", switch_inline_query_current_chat=""),
                InlineKeyboardButton("🔙 Back", callback_data="back_search_main"),
            ],
        ]
    )
    await query.edit_message_text(tips_text, reply_markup=button)


@Client.on_callback_query(filters.regex("^back_search_main$"))
async def back_to_search_main(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📹 PornHub Search", switch_inline_query_current_chat=""),
                InlineKeyboardButton("🔥 xHamster Search", switch_inline_query_current_chat="xhamster "),
            ],[
                InlineKeyboardButton("🔥 Trending", switch_inline_query_current_chat="trending"),
                InlineKeyboardButton("💡 Search Tips", callback_data="search_tips"),
            ],
        ]
    )
    await query.edit_message_text(
        "🔍 <b>Multi-Site Search</b>\n\n"
        "Choose your search method:",
        reply_markup=button
    )


@Client.on_message(filters.command("trending", prefixs) & filters.private)
async def trending_videos(_, update: Message):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📹 PornHub Trending", switch_inline_query_current_chat="trending"),
                InlineKeyboardButton("🔥 xHamster Trending", switch_inline_query_current_chat="xhamster trending"),
            ]
        ]
    )
    await update.reply_text("🔥 <b>Trending Videos</b>\n\nChoose your preferred site:", reply_markup=button)


@Client.on_callback_query(filters.regex("^xh_categories$"))
async def xhamster_categories(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👩 Teen", switch_inline_query_current_chat="xhamster teen"),
                InlineKeyboardButton("👸 MILF", switch_inline_query_current_chat="xhamster milf"),
            ],[
                InlineKeyboardButton("🔥 Hot", switch_inline_query_current_chat="xhamster hot"),
                InlineKeyboardButton("💕 Amateur", switch_inline_query_current_chat="xhamster amateur"),
            ],[
                InlineKeyboardButton("🌟 Popular", switch_inline_query_current_chat="xhamster popular"),
                InlineKeyboardButton("🆕 New", switch_inline_query_current_chat="xhamster new"),
            ],[
                InlineKeyboardButton("🔙 Back", callback_data="back_xh_main"),
            ],
        ]
    )
    await query.edit_message_text("🔥 <b>xHamster Categories</b>\n\nChoose a category:", reply_markup=button)


@Client.on_callback_query(filters.regex("^xh_tips$"))
async def xhamster_tips(_, query: CallbackQuery):
    tips_text = """
💡 <b>xHamster Search Tips</b>

🔍 <b>Search Commands:</b>
• <code>/xhamster [keyword]</code> - Search specific content
• <code>@botname xhamster [term]</code> - Inline search

🎯 <b>Popular Keywords:</b>
• teen, milf, amateur, hot
• trending, new, popular
• hd, 4k, premium

⚡ <b>Pro Tips:</b>
• Use specific keywords for better results
• Try different combinations
• Check trending for popular content
• Use categories for quick access

🔧 <b>Troubleshooting:</b>
• If search fails, try simpler keywords
• Check your internet connection
• Try again after a few seconds
    """
    
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔍 Try Search", switch_inline_query_current_chat="xhamster "),
                InlineKeyboardButton("🔙 Back", callback_data="back_xh_main"),
            ],
        ]
    )
    await query.edit_message_text(tips_text, reply_markup=button)


@Client.on_callback_query(filters.regex("^back_xh_main$"))
async def back_to_xhamster_main(_, query: CallbackQuery):
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔥 Search xHamster", switch_inline_query_current_chat="xhamster "),
                InlineKeyboardButton("🔥 Trending", switch_inline_query_current_chat="xhamster trending"),
            ],[
                InlineKeyboardButton("🔥 Categories", callback_data="xh_categories"),
                InlineKeyboardButton("💡 Tips", callback_data="xh_tips"),
            ],
        ]
    )
    await query.edit_message_text(
        "🔥 <b>xHamster Search</b>\n\n"
        "Choose an option to get started:",
        reply_markup=button
    )