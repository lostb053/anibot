import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from .. import BOT_NAME, TRIGGERS as trg
from ..utils.helper import control_user
from ..utils.db import get_collection

DC = get_collection('DISABLED_CMDS')

@Client.on_message(filters.command(["quote", f"quote{BOT_NAME}"], prefixes=trg))
@control_user
async def truth(_, message: Message):
    gid = message.chat.id
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'quote' in find_gc['cmd_list'].split():
        return
    q = requests.get("https://animechan.vercel.app/api/random").json()
    await message.reply_text('`'+q['quote']+'`\n—  '+q['character']+' (From '+q['anime']+')')