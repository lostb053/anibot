# The following code is exact (almost i mean) copy of 
# reverse search taken from @DeletedUser420's Userge-Plugins repo
# originally authored by
# Phyco-Ninja (https://github.com/Phyco-Ninja) (@PhycoNinja13b)
# but is in current state after DeletedUser420's edits
# which made this code shorter and more efficient

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import tracemoepy, os
from aiohttp import ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from .. import BOT_NAME, HELP_DICT, TRIGGERS as trg
from ..utils.helper import media_to_image
from ..utils.data_parser import ck_is_adult
from ..utils.db import get_collection

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
            os.remove(dls_loc)
            result = search["docs"][0]
            caption = (
                f"**Title**: {result['title_english']} (`{result['title_native']}`)\n"
                f"\n**Anilist ID:** `{result['anilist_id']}`"
                f"\n**Similarity**: `{(str(result['similarity']*100))[:5]}`"
                f"\n**Episode**: `{result['episode']}`"
            )
            preview = await tracemoe.natural_preview(search)
        if await ck_is_adult(int(result['anilist_id']))=="True" and await (SFW_GRPS.find_one({"id": message.chat.id})):
            await message.reply_text("The results parsed seems to be 18+ and not allowed in this group")
            return
        with open("preview.mp4", "wb") as f:
            f.write(preview)
            await session.close()
        await message.reply_video(
            "preview.mp4",
            caption=caption,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("More Info", url=f"https://anilist.co//anime/{result['anilist_id']}")]]))
        os.remove("preview.mp4")
    else:
        await message.reply_text("Couldn't parse results!!!")
    await x.delete()


HELP_DICT["reverse"] = """Use /reverse cmd to get reverse search via tracemoepy API

__Note: This works best on uncropped anime pic,
when used on cropped media, you may get result but it might not be too reliable__

**Usage:**
        `/reverse (reply to gif, video, photo)`
        `!reverse (reply to gif, video, photo)`"""
