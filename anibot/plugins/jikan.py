# uses jikanpy (Jikan API)
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from .. import BOT_NAME, HELP_DICT, TRIGGERS as trg
from ..utils.data_parser import get_scheduled
from ..utils.helper import get_btns, check_user
from ..utils.db import get_collection

DC = get_collection('DISABLED_CMDS')


@Client.on_message(filters.command(["schedule", f"schedule{BOT_NAME}"], prefixes=trg))
async def get_schuled(client: Client, message: Message):
    """Get List of Scheduled Anime"""
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'schedule' in find_gc['cmd_list'].split():
        return
    x = await client.send_message(message.chat.id, "<code>Fetching Scheduled Animes</code>")
    user = message.from_user.id
    msg = await get_scheduled()
    buttons = get_btns("SCHEDULED", result=[msg[1]], user=user)
    await x.edit_text(msg[0], reply_markup=buttons)


@Client.on_callback_query(filters.regex(pattern=r"sched_(.*)"))
@check_user
async def ns_(client, cq: CallbackQuery):
    kek, day, user = cq.data.split("_")
    msg = await get_scheduled(int(day))
    buttons = get_btns("SCHEDULED", result=[int(day)], user=user)
    await cq.edit_message_text(msg[0], reply_markup=buttons)