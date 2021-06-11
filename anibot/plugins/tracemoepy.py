# The following code is exact (almost i mean) copy of 
# reverse search taken from @DeletedUser420's Userge-Plugins repo
# originally authored by
# Phyco-Ninja (https://github.com/Phyco-Ninja) (@PhycoNinja13b)
# but is in current state after DeletedUser420's edits
# which made this code shorter and more efficient

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto, InputMediaVideo
import tracemoepy, os, random
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from .. import BOT_NAME, HELP_DICT, TRIGGERS as trg
from ..utils.helper import check_user, media_to_image
from ..utils.data_parser import check_if_adult
from ..utils.db import get_collection
from .anilist import no_pic

SFW_GRPS = get_collection("SFW_GROUPS")


@Client.on_message(filters.command(["reverse", f"reverse{BOT_NAME}"], prefixes=trg))
async def trace_bek(client: Client, message: Message):
    """ Reverse Search Anime Clips/Photos """
    x = await message.reply_text("Reverse searching the given media")
    dls_loc = await media_to_image(client, message, x)
    if dls_loc:
        async with ClientSession() as session:
            tracemoe = tracemoepy.AsyncTrace(session=session)
            search = await tracemoe.search(dls_loc, upload_file=True)
            result = search["result"][0]
            caption_ = (
                f"**Title**: {result['anilist']['title']['english']} (`{result['anilist']['title']['native']}`)\n"
                f"\n**Anilist ID:** `{result['anilist']['id']}`"
                f"\n**Similarity**: `{(str(result['similarity']*100))[:5]}`"
                f"\n**Episode**: `{result['episode']}`"
            )
            preview = result['video']
        button = []
        nsfw = False
        if await check_if_adult(int(result['anilist']['id']))=="True" and await (SFW_GRPS.find_one({"id": message.chat.id})):
            msg = no_pic[random.randint(0, 4)]
            caption="The results parsed seems to be 18+ and not allowed in this group"
            nsfw = True
        else:
            msg = preview
            caption=caption_
            button.append([InlineKeyboardButton("More Info", url=f"https://anilist.co/anime/{result['anilist']['id']}")])
        button.append([InlineKeyboardButton("Next", callback_data=f"tracech_1_{dls_loc}_{message.from_user.id}")])
        await (message.reply_video if nsfw==False else message.reply_photo)(msg, caption=caption, reply_markup=InlineKeyboardMarkup(button))
    else:
        await message.reply_text("Couldn't parse results!!!")
    await x.delete()


@Client.on_callback_query()
@check_user
async def tracemoe_btn(client: Client, cq: CallbackQuery):
    kek, page, dls_loc, user = cq.data.split("_")
    async with ClientSession() as session:
        tracemoe = tracemoepy.AsyncTrace(session=session)
        search = await tracemoe.search(dls_loc, upload_file=True)
        result = search["result"][int(page)]
        caption = (
            f"**Title**: {result['anilist']['title']['english']} (`{result['anilist']['title']['native']}`)\n"
            f"\n**Anilist ID:** `{result['anilist']['id']}`"
            f"\n**Similarity**: `{(str(result['similarity']*100))[:5]}`"
            f"\n**Episode**: `{result['episode']}`"
        )
        preview = result['video']
    button = []
    if await check_if_adult(int(result['anilist']['id']))=="True" and await (SFW_GRPS.find_one({"id": cq.message.chat.id})):
        msg = InputMediaPhoto(no_pic[random.randint(0, 4)], caption="The results parsed seems to be 18+ and not allowed in this group")
    else:
        msg = InputMediaVideo(preview, caption=caption)
        button.append([InlineKeyboardButton("More Info", url=f"https://anilist.co/anime/{result['anilist']['id']}")])
    if int(page)==0:
        button.append([InlineKeyboardButton("Next", callback_data=f"tracech_{int(page)+1}_{dls_loc}_{user}")])
    elif int(page)==(len(search['result'])-1):
        button.append([InlineKeyboardButton("Back", callback_data=f"tracech_{int(page)-1}_{dls_loc}_{user}")])
    else:
        button.append([
            InlineKeyboardButton("Back", callback_data=f"tracech_{int(page)-1}_{dls_loc}_{user}"),
            InlineKeyboardButton("Next", callback_data=f"tracech_{int(page)+1}_{dls_loc}_{user}")
        ])
    await cq.edit_message_media(msg, reply_markup=InlineKeyboardMarkup(button))


HELP_DICT["reverse"] = """Use /reverse cmd to get reverse search via tracemoepy API

__Note: This works best on uncropped anime pic,
when used on cropped media, you may get result but it might not be too reliable__

**Usage:**
        `/reverse (reply to gif, video, photo)`
        `!reverse (reply to gif, video, photo)`"""
