import asyncio
import threading
from pyrogram.errors import MessageNotModified, FloodWait


def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def edit_msg(client, message, to_edit):
    try:
        client.loop.create_task(message.edit(to_edit))
    except FloodWait as e:
        client.loop.create_task(asyncio.sleep(e.value))
    except MessageNotModified:
        pass
    except TypeError:
        pass


def download_progress_hook(d, message, client):
    if d['status'] == 'downloading':
        current = d.get("_downloaded_bytes_str") or humanbytes(int(d.get("downloaded_bytes", 1)))
        total = d.get("_total_bytes_str") or d.get("_total_bytes_estimate_str")
        file_name = d.get("filename", "Video")
        eta = d.get('_eta_str', "N/A")
        percent = d.get("_percent_str", "N/A")
        speed = d.get("_speed_str", "N/A")
        
        # Check if downloading thumbnail
        is_thumbnail = any(ext in file_name.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])
        download_type = "🖼️ Thumbnail" if is_thumbnail else "📹 Video"
        
        to_edit = f"📥 <b>Downloading {download_type}!</b>\n\n<b>Name :</b> <code>{file_name}</code>\n<b>Size :</b> <code>{total}</code>\n<b>Speed :</b> <code>{speed}</code>\n<b>ETA :</b> <code>{eta}</code>\n\n<b>Progress: </b> <code>{current}</code> / <code>{total}</code> <b>({percent})</b>"
        threading.Thread(target=edit_msg, args=(client, message, to_edit)).start()
    elif d['status'] == 'finished':
        file_name = d.get("filename", "File")
        is_thumbnail = any(ext in file_name.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])
        if is_thumbnail:
            to_edit = "🖼️ <b>Thumbnail downloaded!</b>\n\n📹 <b>Now downloading video...</b>"
            threading.Thread(target=edit_msg, args=(client, message, to_edit)).start()
