import requests
from pyrogram import filters
from pyrogram.types import Message
from .. import BOT_NAME, TRIGGERS as trg, anibot
from ..utils.helper import control_user
from ..utils.db import get_collection

DC = get_collection('DISABLED_CMDS')

@anibot.on_message(filters.command(["quote", f"quote{BOT_NAME}"], prefixes=trg))
@control_user
async def quote(_, message: Message, mdata: dict):
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'quote' in find_gc['cmd_list'].split():
        return
    q = requests.get("https://animechan.vercel.app/api/random").json()
    await message.reply_text('`'+q['quote']+'`\n\n—  **'+q['character']+'** (From __'+q['anime']+'__)')