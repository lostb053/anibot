import rapidjson as json
from pyrogram import Client, filters
from .. import BOT_NAME, TRIGGERS as trg
from ..utils.helper import check_user, control_user
from ..utils.db import get_collection

DC = get_collection('DISABLED_CMDS')

@Client.on_message(filters.command(["quote", f"quote{BOT_NAME}"], prefixes=trg))
@control_user
def truth(_, message):
    quote = requests.get("https://animechan.vercel.app/api/random").json()
    quote = quote.get("quote")
    message.reply_text(quote)
