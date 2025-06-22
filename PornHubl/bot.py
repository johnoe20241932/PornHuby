import time
import logging
import pyrogram

from pyrogram import Client
from pyrogram.errors import BadRequest
from pyrogram.raw.all import layer

from . import __version__, __version_code__
from .config import API_HASH, API_ID, TOKEN, log_chat, MONGO_URL
from .database import Database


logger = logging.getLogger(__name__)


class PornHub(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            name=name,
            app_version=f"PornHub v{__version__}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=TOKEN,
            plugins=dict(root="PornHub.plugins"),
            in_memory=True,
        )
        
        # Initialize database
        self.db = Database(MONGO_URL)

    async def start(self):
        await super().start()

        self.start_time = time.time()
        
        # Initialize database
        await self.db.init_db()

        logger.info(
            "PornHub running with Pyrogram v%s (Layer %s) started on %s. Hello!",
            pyrogram.__version__,
            layer,
            self.me.username,
        )

        start_message = (
            "<b>PornHub started!</b>\n\n"
            f"<b>Version:</b> <code>v{__version__} ({__version_code__})</code>\n"
            f"<b>Pyrogram:</b> <code>v{pyrogram.__version__}</code>"
        )

        if log_chat:
            try:
                await self.send_message(chat_id=log_chat, text=start_message)
            except (BadRequest, ValueError, KeyError) as e:
                logger.warning(f"Unable to send message to log_chat: {e}")
        else:
            logger.info("Log chat disabled - startup message not sent")

    async def stop(self):
        await super().stop()
        logger.warning("PornHub stopped, Bye!")
