from typing import List

API_ID: int = 26489431
API_HASH: str = "9a2fce85339bb79254a55368a61ab92f"
TOKEN: str = "7672506977:AAGcT2TIiEFGaD2lSxSAfliqBPLDfSzkuvo"

log_chat: int = None  # Set to None to disable logging or use valid chat ID
sub_chat: str = "ccfzzzs"
sudoers: List[int] = [7912527708, 1249591948]
prefixs: List[str] = ["/", "!", ".", "$", "-"]

# MongoDB Configuration
MONGO_URL: str = "mongodb+srv://pefic67072:ONtkKs5MbRzEreuJ@cluster0.8py7f.mongodb.net/?retryWrites=true&w=majority"  # Change this to your MongoDB URL

# notes

# 1. api_id & api_hash get from my.telegram.org
# 2. token fill with your bot_token get from @BotFather
# 3. log_chat fill with the chat id of a group that you should create for the bot logger
# 4. sub_chat fill with the channel username but don't include the '@' symbol
