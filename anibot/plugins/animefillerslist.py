from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from ..utils.data_parser import search_filler, parse_filler
from ..utils.helper import check_user, control_user, rand_key
from ..utils.db import get_collection
from .. import BOT_NAME, TRIGGERS as trg

FILLERS = {}
DC = get_collection('DISABLED_CMDS')

@Client.on_message(filters.command(['fillers', f"fillers{BOT_NAME}"], prefixes=trg))
@control_user
async def fillers_cmd(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc is not None and 'watch' in find_gc['cmd_list'].split():
        return
    qry = message.text.split(" ", 1)
    if len(qry)==1:
        return await message.reply_text("Give some anime name to search fillers for\nexample: /fillers Detective Conan")
    k = search_filler(qry[1])
    if k == {}:
        await message.reply_text("No fillers found for the given anime...")
        return
    button = []
    list_ = list(k.keys())
    if len(list_)==1:
        result = parse_filler(k.get(list_[0]))
        msg = ""
        msg += f"Fillers for anime `{list_[0]}`\n\nManga Canon episodes:\n"
        msg += str(result.get("total_ep"))
        msg += "\n\nMixed/Canon fillers:\n"
        msg += str(result.get("mixed_ep"))
        msg += "\n\nFillers:\n"
        msg += str(result.get("filler_ep"))
        if result.get("ac_ep") is not None:
            msg += "\n\nAnime Canon episodes:\n"
            msg += str(result.get("ac_ep"))
        await message.reply_text(msg)
        return
    for i in list_:
        fl_js = rand_key()
        FILLERS[fl_js] = [k.get(i), i]
        button.append([InlineKeyboardButton(i, callback_data=f"fill_{fl_js}_{message.from_user.id}")])
    await message.reply_text("Pick anime you want to see fillers list for:", reply_markup=InlineKeyboardMarkup(button))


@Client.on_callback_query(filters.regex(pattern=r"fill_(.*)"))
@check_user
async def filler_btn(client: Client, cq: CallbackQuery):
    kek, req, user = cq.data.split("_")
    result = parse_filler((FILLERS.get(req))[0])
    msg = ""
    msg += f"**Fillers for anime** `{(FILLERS.get(req))[1]}`\n\n**Manga Canon episodes:**\n"
    msg += str(result.get("total_ep"))
    msg += "\n\n**Mixed/Canon fillers:**\n"
    msg += str(result.get("mixed_ep"))
    msg += "\n\n**Fillers:**\n"
    msg += str(result.get("filler_ep"))
    if result.get("ac_ep") is not None:
        msg += "\n\n**Anime Canon episodes:**\n"
        msg += str(result.get("ac_ep"))
    await cq.edit_message_text(msg)