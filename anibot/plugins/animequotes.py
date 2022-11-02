import requests
from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup as IKM,
    InlineKeyboardButton as IKB
)
from .. import BOT_NAME, TRIGGERS as trg, anibot
from ..utils.helper import control_user, check_user
from ..utils.db import get_collection

DC = get_collection('DISABLED_CMDS')

@anibot.on_message(
    filters.command(
        ["quote", f"quote{BOT_NAME}"],
        prefixes=trg
    )
)
@control_user
async def quote(_, message: Message, mdata: dict):
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'quote' in find_gc['cmd_list'].split():
        return
    q = requests.get("https://animechan.vercel.app/api/random").json()
    btn = IKM([[IKB("Refresh", callback_data=f"quoteref_{user}")]])
    await message.reply_text(
        '`'+q['quote']+'`\n\n—  **'+q['character']
        +'** (From __'+q['anime']+'__)',
        reply_markup=btn
    )


@anibot.on_callback_query(filters.regex(pattern=r"quoteref_(.*)"))
@check_user
async def quote_btn(client: anibot, cq: CallbackQuery, cdata: dict):
    kek, user = cdata['data'].split("_")
    await cq.answer()
    q = requests.get("https://animechan.vercel.app/api/random").json()
    btn = IKM([[IKB("Refresh", callback_data=f"quoteref_{user}")]])
    await cq.edit_message_text(
        '`'+q['quote']+'`\n\n—  **'+q['character']
        +'** (From __'+q['anime']+'__)',
        reply_markup=btn
    )


@anibot.on_message(
    filters.command(
        ["quote", f"quote{BOT_NAME}"],
        prefixes=trg
    )
)
async def quote_edit(_, message: Message):
    await quote(_, message)
