# base code was taken from @DeletedUser420's Userge-Plugins repo
# originally authored by Phyco-Ninja (https://github.com/Phyco-Ninja) (@PhycoNinja13b)
# I've just tweaked his file a bit (maybe a lot)
# But i sticked to the result format he used which looked cool

""" Search for Anime related Info using Anilist API """


import asyncio
from types import NoneType
import requests
import time
import random
import re
import os
from pyrogram import filters, Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message
)
from pyrogram.errors import UserNotParticipant, WebpageCurlFailed, WebpageMediaEmpty
from .. import (
    ANILIST_CLIENT,
    ANILIST_REDIRECT_URL,
    ANILIST_SECRET,
    OWNER,
    TRIGGERS as trg,
    BOT_NAME,
    anibot
)
from ..utils.data_parser import (
    get_all_genres,
    get_all_tags,
    get_studio_animes,
    get_studios,
    get_top_animes,
    get_user_activity,
    get_user_favourites,
    toggle_favourites,
    get_anime,
    get_airing,
    get_anilist,
    get_character,
    get_additional_info,
    get_manga,
    browse_,
    get_featured_in_lists,
    update_anilist,
    get_user,
    ANIME_DB,
    MANGA_DB,
    CHAR_DB,
    AIRING_DB,
    STUDIO_DB,
    GUI
)
from ..utils.helper import (
    clog,
    check_user,
    get_btns,
    rand_key,
    control_user,
    get_user_from_channel as gcc,
    PIC_LS,
    AUTH_USERS
)
from ..utils.db import get_collection

GROUPS = get_collection("GROUPS")
SFW_GRPS = get_collection("SFW_GROUPS")
DC = get_collection('DISABLED_CMDS')
AG = get_collection('AIRING_GROUPS')
CG = get_collection('CRUNCHY_GROUPS')
SG = get_collection('SUBSPLEASE_GROUPS')
HD = get_collection('HEADLINES_GROUPS')
MHD = get_collection('MAL_HEADLINES_GROUPS')
CHAT_OWNER = ChatMemberStatus.OWNER
MEMBER = ChatMemberStatus.MEMBER
ADMINISTRATOR = ChatMemberStatus.ADMINISTRATOR

failed_pic = "https://telegra.ph/file/09733b49f3a9d5b147d21.png"
no_pic = [
    'https://telegra.ph/file/0d2097f442e816ba3f946.jpg',
    'https://telegra.ph/file/5a152016056308ef63226.jpg',
    'https://telegra.ph/file/d2bf913b18688c59828e9.jpg',
    'https://telegra.ph/file/d53083ea69e84e3b54735.jpg',
    'https://telegra.ph/file/b5eb1e3606b7d2f1b491f.jpg'
]


@anibot.on_message(
    filters.command(["anime", f"anime{BOT_NAME}"], prefixes=trg)
)
@control_user
async def anime_cmd(client: Client, message: Message, mdata: dict):
    """Search Anime Info"""
    text = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'anime' in find_gc['cmd_list'].split():
        return
    if len(text) == 1:
        k = await message.reply_text(
"""Please give a query to search about
example: /anime Ao Haru Ride"""
        )
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    auth = False
    vars_ = {"search": query}
    if query.isdigit():
        vars_ = {"id": int(query)}
    if (await AUTH_USERS.find_one({"id": auser})):
        auth = True
    result = await get_anime(
        vars_,
        user=auser,
        auth=auth,
        cid=gid if gid != user else None
    )
    if len(result) != 1:
        title_img, finals_ = result[0], result[1]
    else:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    buttons = get_btns("ANIME", result=result, user=user, auth=auth)
    if await (
        SFW_GRPS.find_one({"id": gid})
    ) and result[2].pop() == "True":
        await client.send_photo(
            gid,
            no_pic[random.randint(0, 4)],
            caption="This anime is marked 18+ and not allowed in this group"
        )
        return
    try:
        await client.send_photo(
            gid, title_img, caption=finals_, reply_markup=buttons
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', title_img, 'LINK', msg=message)
        await client.send_photo(
            gid, failed_pic, caption=finals_, reply_markup=buttons
        )
    if title_img not in PIC_LS:
        PIC_LS.append(title_img)


@anibot.on_message(
    filters.command(["manga", f"manga{BOT_NAME}"], prefixes=trg)
)
@control_user
async def manga_cmd(client: Client, message: Message, mdata: dict):
    """Search Manga Info"""
    text = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'manga' in find_gc['cmd_list'].split():
        return
    if len(text) == 1:
        k = await message.reply_text(
"""Please give a query to search about
example: /manga The teasing master Takagi san"""
        )
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    qdb = rand_key()
    MANGA_DB[qdb] = query
    auth = False
    if (await AUTH_USERS.find_one({"id": auser})):
        auth = True
    result = await get_manga(
        qdb, 1, auth=auth, user=auser, cid=gid if gid != user else None
    )
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, finals_ = result[0], result[1][0]
    buttons = get_btns(
        "MANGA",
        lsqry=qdb,
        lspage=1,
        user=user,
        result=result,
        auth=auth
    )
    if await (SFW_GRPS.find_one({"id": gid})) and result[2].pop() == "True":
        buttons = get_btns(
            "MANGA",
            lsqry=qdb,
            lspage=1,
            user=user,
            result=result,
            auth=auth,
            sfw="True"
        )
        await client.send_photo(
            gid,
            no_pic[random.randint(0, 4)],
            caption="This manga is marked 18+ and not allowed in this group",
            reply_markup=buttons
        )
        return
    try:
        await client.send_photo(
            gid, pic, caption=finals_, reply_markup=buttons
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=message)
        await client.send_photo(
            gid, failed_pic, caption=finals_, reply_markup=buttons
        )
    if pic not in PIC_LS:
        PIC_LS.append(pic)


@anibot.on_message(
    filters.command(["character", f"character{BOT_NAME}"], prefixes=trg)
)
@control_user
async def character_cmd(client: Client, message: Message, mdata: dict):
    """Get Info about a Character"""
    text = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'character' in find_gc['cmd_list'].split():
        return
    if len(text) == 1:
        k = await message.reply_text(
            "Please give a query to search about\nexample: /character Nezuko"
        )
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    qdb = rand_key()
    CHAR_DB[qdb] = query
    auth = False
    if (await AUTH_USERS.find_one({"id": auser})):
        auth = True
    result = await get_character(qdb, 1, auth=auth, user=auser)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    img = result[0]
    cap_text = result[1][0]
    buttons = get_btns(
        "CHARACTER",
        user=user,
        lsqry=qdb,
        lspage=1,
        result=result,
        auth=auth
    )
    try:
        await client.send_photo(
            gid, img, caption=cap_text, reply_markup=buttons
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', img, 'LINK', msg=message)
        await client.send_photo(
            gid, failed_pic, caption=cap_text, reply_markup=buttons
        )


@anibot.on_message(
    filters.command(["anilist", f"anilist{BOT_NAME}"], prefixes=trg)
)
@control_user
async def anilist_cmd(client: Client, message: Message, mdata: dict):
    text = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'anilist' in find_gc['cmd_list'].split():
        return
    if len(text) == 1:
        k = await message.reply_text(
            "Please give a query to search about\nexample: /anilist rezero"
        )
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    qdb = rand_key()
    ANIME_DB[qdb] = query
    auth = False
    if (await AUTH_USERS.find_one({"id": auser})):
        auth = True
    result = await get_anilist(
        qdb, 1, auth=auth, user=auser, cid=gid if gid != user else None
    )
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, msg = result[0], result[1][0]
    buttons = get_btns(
        "ANIME",
        lsqry=qdb,
        lspage=1,
        result=result,
        user=user,
        auth=auth
    )
    if await (SFW_GRPS.find_one({"id": gid})) and result[2].pop() == "True":
        buttons = get_btns(
            "ANIME",
            lsqry=qdb,
            lspage=1,
            result=result,
            user=user,
            auth=auth,
            sfw="True"
        )
        await client.send_photo(
            gid,
            no_pic[random.randint(0, 4)],
            caption="This anime is marked 18+ and not allowed in this group",
            reply_markup=buttons
        )
        return
    try:
        await client.send_photo(gid, pic, caption=msg, reply_markup=buttons)
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=message)
        await client.send_photo(
            gid, failed_pic, caption=msg, reply_markup=buttons
        )
    if pic not in PIC_LS:
        PIC_LS.append(pic)


@anibot.on_message(
    filters.command(
        ["flex", f"flex{BOT_NAME}", "user", f"user{BOT_NAME}"],
        prefixes=trg
    )
)
@control_user
async def flex_cmd(client: Client, message: Message, mdata: dict):
    query = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    qry = None
    find_gc = await DC.find_one({'_id': gid})
    if "user" in query[0]:
        if find_gc is not None and 'user' in find_gc['cmd_list'].split():
            return
        if not len(query) == 2:
            k = await message.reply_text(
"""Please give an anilist username to search about
example: /user Lostb053"""
)
            await asyncio.sleep(5)
            return await k.delete()
        else:
            qry = {"search": query[1]}
    if find_gc is not None and 'flex' in find_gc['cmd_list'].split():
        return
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    if not "user" in query[0] and not (
        await AUTH_USERS.find_one({"id": auser})
    ):
        return await message.reply_text(
"""Please connect your account first to use this cmd
Or connect your channel with /connect cmd if you are anonymous""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "Auth",
                    url=f"https://t.me/{BOT_NAME.replace('@', '')}/?start=auth"
                )]]
            )
        )
    result = await get_user(qry, query[0], auser, user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, msg, buttons = result
    try:
        await client.send_photo(
            gid, pic, caption=msg, reply_markup=buttons
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=message)
        await client.send_photo(
            gid, failed_pic, caption=msg, reply_markup=buttons
        )


@anibot.on_message(filters.command(["top", f"top{BOT_NAME}"], prefixes=trg))
@control_user
async def top_tags_cmd(client: Client, message: Message, mdata: dict):
    query = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'top' in find_gc['cmd_list'].split():
        return
    get_tag = "None"
    if len(query) == 2:
        get_tag = query[1]
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
    result = await get_top_animes(get_tag, 1, user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    if await (SFW_GRPS.find_one({"id": gid})) and str(result[0][1]) == "True":
        return await message.reply_text(
            'No nsfw stuff allowed in this group!!!'
        )
    msg, buttons = result
    await client.send_message(
        gid, msg[0], reply_markup=buttons if buttons != '' else None
    )


@anibot.on_message(filters.command(["studio", f"studio{BOT_NAME}"], prefixes=trg))
@control_user
async def studio_cmd(client: Client, message: Message, mdata: dict):
    text = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'studio' in find_gc['cmd_list'].split():
        return
    if len(text) == 1:
        x = await message.reply_text("Please give a query to search about!!!\nExample: /studio ufotable")
        await asyncio.sleep(5)
        await x.delete()
        return
    query = text[1]
    qdb = rand_key()
    STUDIO_DB[qdb] = query
    auth = False
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    if (await AUTH_USERS.find_one({"id": auser})):
        auth = True
    result = await get_studios(qdb, 1, user=auser, duser=user, auth=auth)
    if len(result)==1:
        x = await message.reply_text("No results found!!!")
        await asyncio.sleep(5)
        return await x.delete()
    msg, buttons = result[0], result[1]
    await client.send_message(
        gid, msg, reply_markup=buttons if buttons != '' else None
    )


@anibot.on_message(
    filters.command(["airing", f"airing{BOT_NAME}"], prefixes=trg)
)
@control_user
async def airing_cmd(client: Client, message: Message, mdata: dict):
    """Get Airing Detail of Anime"""
    text = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'airing' in find_gc['cmd_list'].split():
        return
    if len(text) == 1:
        k = await message.reply_text(
"""Please give a query to search about
example: /airing Fumetsu no Anata e""")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    qdb = rand_key()
    AIRING_DB[qdb] = query
    auth = False
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    if (await AUTH_USERS.find_one({"id": auser})):
        auth = True
    result = await get_airing(qdb, 1, auth=auth, user=auser)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    coverImg, out = result[0]
    btn = get_btns(
        "AIRING",
        user=user,
        result=result,
        auth=auth,
        lsqry=qdb,
        lspage=1
    )
    if await (SFW_GRPS.find_one({"id": gid})) and result[2].pop() == "True":
        btn = get_btns(
            "AIRING",
            user=user,
            result=result,
            auth=auth,
            lsqry=qdb,
            lspage=1,
            sfw="True"
        )
        await client.send_photo(
            gid,
            no_pic[random.randint(0, 4)],
            caption="This anime is marked 18+ and not allowed in this group",
            reply_markup=btn
        )
        return
    try:
        await client.send_photo(gid, coverImg, caption=out, reply_markup=btn)
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', coverImg, 'LINK', msg=message)
        await client.send_photo(gid, failed_pic, caption=out, reply_markup=btn)
    update = True
    for i in PIC_LS:
        if coverImg in i:
            update = False
            break
    if update:
        PIC_LS.append(coverImg)


@anibot.on_message(filters.command(["auth", f"auth{BOT_NAME}"], prefixes=trg))
@control_user
async def auth_link_cmd(client, message: Message, mdata: dict):
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = 00000000
    if mdata['chat']['id'] == user:
        text = "Click the below button to authorize yourself"
        if not os.environ.get('ANILIST_REDIRECT_URL'):
            text = """Follow the steps to complete Authorization:
1. Click the below button
2. Authorize the app and copy the authorization code
3. Send the copied code followed by the command /code'
"""
        base = "https://anilist.co/api/v2/oauth/authorize?client_id="
        ac = ANILIST_CLIENT
        aru = ANILIST_REDIRECT_URL
        await message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    text="Authorize",
                    url=f"{base}{ac}&redirect_uri={aru}&response_type=code"
                )]]
            )
        )
    else:
        await message.reply_text(
            "Go to bot pm to authorize yourself!!!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Auth",
                url=f"https://t.me/{BOT_NAME.replace('@', '')}/?start=auth")]]
            )
        )


setting_text = """
<b>This allows you to change group settings</b>
        
NSFW toggle switches on filtering of 18+ marked content

Airing notifications notifies about airing of anime in recent

Crunchyroll updates will toggle notifications about release of animes on crunchyroll site

Subsplease updates will toggle notifications about release of animes on subsplease site

Click Headlines button to enable headlines. You can choose from given sources"""


@anibot.on_message(
    ~filters.private & filters.command(
        ["settings", f"settings{BOT_NAME}"],
        prefixes=trg
    )
)
@control_user
async def settings_cmd(client: Client, message: Message, mdata: dict):
    cid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
    type_ = mdata['chat']['type']
    try:
        status = (await anibot.get_chat_member(cid, user)).status
    except UserNotParticipant:
        status = None
    if user in OWNER or status in [
        ADMINISTRATOR,
        CHAT_OWNER
    ] or type_ == ChatType.CHANNEL or user == cid:
        sfw = "NSFW: Allowed"
        if await (SFW_GRPS.find_one({"id": cid})):
            sfw = "NSFW: Not Allowed"
        notif = "Airing notifications: OFF"
        if await (AG.find_one({"_id": cid})):
            notif = "Airing notifications: ON"
        cr = "Crunchyroll Updates: OFF"
        if await (CG.find_one({"_id": cid})):
            cr = "Crunchyroll Updates: ON"
        sp = "Subsplease Updates: OFF"
        if await (SG.find_one({"_id": cid})):
            sp = "Subsplease Updates: ON"
        await message.reply_text(
            text=setting_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=sfw, callback_data=f"settogl_sfw_{cid}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=notif, callback_data=f"settogl_notif_{cid}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=cr, callback_data=f"settogl_cr_{cid}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=sp, callback_data=f"settogl_sp_{cid}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Headlines", callback_data=f"headlines_call_{cid}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Change UI", callback_data=f"cui_call_{cid}"
                        )
                    ]
                ]
            )
        )


@anibot.on_message(filters.private & filters.command("code", prefixes=trg))
@control_user
async def man_code_cmd(client: Client, message: Message, _):
    text = message.text.split(" ", 1)
    if len(text) == 1:
        return await message.reply_text(
            'Send the code you obtained from website along with the cmd'
        )
    await code_cmd(text[1], message)


async def code_cmd(code: str, message: Message):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    json = {
        'grant_type': 'authorization_code',
        'client_id': ANILIST_CLIENT,
        'client_secret': ANILIST_SECRET,
        'redirect_uri': ANILIST_REDIRECT_URL,
        'code': code
    }
    us_ = message.from_user.id
    if (await AUTH_USERS.find_one({"id": us_})):
        return await message.reply_text(
"""You have already authorized yourself
If you wish to logout send /logout"""
        )
    response: dict = requests.post(
        "https://anilist.co/api/v2/oauth/token",
        headers=headers,
        json=json
    ).json()
    if response.get("access_token"):
        await AUTH_USERS.insert_one(
            {"id": us_, "token": response.get("access_token")}
        )
        await message.reply_text("Authorization Successfull!!!")
    else:
        await message.reply_text(
"""Please retry authorization process!!!
Something unexpected happened"""
        )
    if os.environ.get('ANILIST_REDIRECT_URL'):
        await AUTH_USERS.find_one_and_delete({'code': code})


@anibot.on_message(
    filters.command(
        ["me", f"me{BOT_NAME}", "activity", f"activity{BOT_NAME}"],
        prefixes=trg
    )
)
@control_user
async def activity_cmd(client: Client, message: Message, mdata: dict):
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'me' in (
        find_gc['cmd_list'].split() and (message.text.split())[0]
    ):
        return
    if find_gc is not None and 'activity' in (
        find_gc['cmd_list'].split() and (message.text.split())[0]
    ):
        return
    if not (await AUTH_USERS.find_one({"id": auser})):
        return await message.reply_text(
"""Please connect your account first to use this cmd
Or connect your channel with /connect cmd if you are anonymous""",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Auth",
                url=f"https://t.me/{BOT_NAME.replace('@', '')}/?start=auth"
            )]])
        )
    result = await get_user(None, "flex", user)
    query = result[0].split("/").pop().split("?")[0]
    result = await get_user_activity(int(query), user=int(user))
    pic, msg, kek = result
    btns = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                "Profile",
                url=f"https://anilist.co/user/{query}"
            )
        ]]
    )
    try:
        await client.send_photo(gid, pic, caption=msg, reply_markup=btns)
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=message)
        await client.send_photo(
            gid, failed_pic, caption=msg, reply_markup=btns
        )


@anibot.on_message(
    filters.command(["favourites", f"favourites{BOT_NAME}"], prefixes=trg)
)
@control_user
async def favourites_cmd(client: Client, message: Message, mdata: dict):
    try:
        user = mdata['from_user']['id']
        auser = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
        ufc = await gcc(user)
        if ufc is not None:
            auser = ufc
        else:
            auser = user
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'favourites' in find_gc['cmd_list'].split():
        return
    if not (await AUTH_USERS.find_one({"id": auser})):
        return await message.reply_text(
"""Please connect your account first to use this cmd
Or connect your channel with /connect cmd if you are anonymous""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "Auth",
                    url=f"https://t.me/{BOT_NAME.replace('@', '')}/?start=auth"
                )]]
            )
        )
    result = await get_user(None, "flex", auser)
    query = result[0].split("/").pop().split("?")[0]
    btn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ANIME",
                    callback_data=f"myfavqry_ANIME_{query}_1_no_{user}"
                ),
                InlineKeyboardButton(
                    "CHARACTER",
                    callback_data=f"myfavqry_CHAR_{query}_1_no_{user}"
                ),
                InlineKeyboardButton(
                    "MANGA",
                    callback_data=f"myfavqry_MANGA_{query}_1_no_{user}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Profile",
                    url=f"https://anilist.co/user/{query}"
                )
            ]
        ]
    )
    try:
        await client.send_photo(
            gid,
            result[0],
            caption="Choose one of the below options",
            reply_markup=btn
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', result[0], 'LINK', msg=message)
        await client.send_photo(
            gid,
            failed_pic,
            caption="Choose one of the below options",
            reply_markup=btn
        )


@anibot.on_message(
    filters.command(["logout", f"logout{BOT_NAME}"], prefixes=trg)
)
@control_user
async def logout_cmd(client: Client, message: Message, mdata: dict):
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = 00000000
    gid = mdata['chat']['id']
    if gid == user:
        if (await AUTH_USERS.find_one({"id": user})):
            AUTH_USERS.find_one_and_delete({"id": user})
            await message.reply_text("Logged out!!!")
        else:
            await message.reply_text("You are not authorized to begin with!!!")
    else:
        await message.reply_text(
            "Send this cmd in pm!!!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Logout",
                url=f"https://t.me/{BOT_NAME.replace('@', '')}/?start=logout"
            )]])
        )


@anibot.on_message(
    filters.command(["browse", f"browse{BOT_NAME}"], prefixes=trg)
)
@control_user
async def browse_cmd(client: Client, message: Message, mdata: dict):
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'browse' in find_gc['cmd_list'].split():
        return
    up = 'Upcoming'
    tr = '• Trending •'
    pp = 'Popular'
    btns = [[
        InlineKeyboardButton(
            tr, callback_data=f'browse_{tr.lower()}_{user}'
        ),
        InlineKeyboardButton(
            pp, callback_data=f'browse_{pp.lower()}_{user}'
        ),
        InlineKeyboardButton(
            up, callback_data=f'browse_{up.lower()}_{user}'
        ),
    ]]
    msg = await browse_('trending')
    await client.send_message(
        gid, msg, reply_markup=InlineKeyboardMarkup(btns)
    )


@anibot.on_message(
    filters.command(
        ["gettags", f"gettags{BOT_NAME}", "getgenres", f"getgenres{BOT_NAME}"],
        prefixes=trg
    )
)
@control_user
async def list_tags_genres_cmd(client, message: Message, mdata: dict):
    gid = mdata['chat']['id']
    text = mdata['text']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and "gettags" in (
        text.split()[0] and find_gc['cmd_list'].split()
    ):
        return
    if find_gc is not None and "getgenres" in (
        text.split()[0] and find_gc['cmd_list'].split()
    ):
        return
    if await (SFW_GRPS.find_one({"id": gid})) and 'nsfw' in text:
        return await message.reply_text('No nsfw allowed here!!!')
    msg = (
        await get_all_tags(text)
    ) if "gettags" in text.split()[0] else (
        await get_all_genres()
    )
    await message.reply_text(msg)


@anibot.on_callback_query(filters.regex(pattern=r"page_(.*)"))
@check_user
async def page_btn(client: Client, cq: CallbackQuery, cdata: dict):
    kek, media, query, page, auth, user = cq.data.split("_")
    gid = cdata["message"]["chat"]["id"]
    if media == "ANIME":
        try:
            ANIME_DB[query]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    if media == "MANGA":
        try:
            MANGA_DB[query]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    if media == "CHARACTER":
        try:
            CHAR_DB[query]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    if media == "AIRING":
        try:
            AIRING_DB[query]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    authbool = bool(1) if auth == "True" else bool(0)
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    if media in ["ANIME", "MANGA"]:
        result = await (
            get_anilist if media == "ANIME" else get_manga
        )(
            query,
            int(page),
            auth=authbool,
            user=int(auser),
            cid=gid if gid != user else None
        )
    else:
        result = await (
            get_character if media == "CHARACTER" else get_airing
        )(
            query,
            int(page),
            auth=authbool,
            user=int(auser)
        )
    if "No results Found" in result:
        await cq.answer("No more results available!!!", show_alert=True)
        return
    pic, msg = result[0], result[1][0]
    if media == "AIRING":
        pic, msg = result[0][0], result[0][1]
    button = get_btns(media, lsqry=query, lspage=int(
        page), result=result, user=user, auth=authbool)
    if await (
        SFW_GRPS.find_one({"id": gid})
    ) and media != "CHARACTER" and result[2].pop() == "True":
        button = get_btns(
            media,
            lsqry=query,
            lspage=int(page),
            result=result,
            user=user,
            auth=authbool,
            sfw="True"
        )
        await cq.edit_message_media(
            InputMediaPhoto(
                no_pic[random.randint(0, 4)],
                caption="""
This material is marked 18+ and not allowed in this group"""
            ),
                reply_markup=button
            )
        return
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg),
            reply_markup=button
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg),
            reply_markup=button
        )
    await cq.answer()
    if media != "CHARACTER":
        if pic not in PIC_LS:
            PIC_LS.append(pic)


@anibot.on_callback_query(filters.regex(pattern=r"pgstudio_(.*)"))
@check_user
async def studio_pg_btn(client: Client, cq: CallbackQuery, cdata: dict):
    kek, page, qry, auth, user = cdata['data'].split("_")
    authbool = bool(1) if auth == "True" else bool(0)
    try:
        STUDIO_DB[qry]
    except KeyError:
        return await cq.answer(
            "Query Expired!!!\nCreate new one", show_alert=True
        )
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    result = await get_studios(qry, page=page, user=auser, duser=user, auth=authbool)
    if len(result)==1:
        return await cq.answer("No more results available!!!", show_alert=True)
    msg, buttons = result[0], result[1]
    await cq.edit_message_text(msg, reply_markup=buttons)


@anibot.on_callback_query(filters.regex(pattern=r"stuani_(.*)"))
@check_user
async def studio_ani_btn(client: Client, cq: CallbackQuery, cdata: dict):
    kek, page, id_, rp, qry, auth, user = cdata['data'].split("_")
    authbool = bool(1) if auth == "True" else bool(0)
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    result = await get_studio_animes(id_, page, qry, rp, auser, user, authbool)
    if len(result)==1:
        return await cq.answer("No results available!!!", show_alert=True)
    msg, buttons = result[0], result[1]
    await cq.edit_message_text(msg, reply_markup=buttons)


@anibot.on_callback_query(filters.regex(pattern=r"btn_(.*)"))
@check_user
async def anime_btn(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    query = cdata['data'].split("_")
    idm = query[1]
    user = int(query.pop())
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    authbool = bool(1) if query[2] == "True" else bool(0)
    vars_ = {"id": int(idm)}
    cid = cdata["message"]["chat"]["id"]
    result = await get_anime(
        vars_, auth=authbool, user=auser, cid=cid if cid != user else None
    )
    pic, msg = result[0], result[1]
    btns = get_btns("ANIME", result=result, user=user, auth=authbool)
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg), reply_markup=btns
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg), reply_markup=btns
        )
    if pic not in PIC_LS:
        PIC_LS.append(pic)


@anibot.on_callback_query(filters.regex(pattern=r"topanimu_(.*)"))
@check_user
async def top_tags_btn(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    kek, gnr, page, user = cdata['data'].split("_")
    result = await get_top_animes(gnr, page=page, user=user)
    msg, buttons = result[0][0], result[1]
    await cq.edit_message_text(msg, reply_markup=buttons)


@anibot.on_callback_query(filters.regex(pattern=r"settogl_(.*)"))
async def nsfw_toggle_btn(client: Client, cq: CallbackQuery):
    cus = cq.from_user.id
    gid = cq.data.split('_').pop()
    try:
        k = (await client.get_chat_member(gid, cus)).status
    except UserNotParticipant:
        await cq.answer()
        return
    if cus not in OWNER and k == MEMBER:
        await cq.answer(
            "You don't have enough permissions to change this!!!",
            show_alert=True
        )
        return
    query = cq.data.split("_")
    if await (SFW_GRPS.find_one({"id": int(query[2])})):
        sfw = "NSFW: Not Allowed"
    else:
        sfw = "NSFW: Allowed"
    if await (AG.find_one({"_id": int(query[2])})):
        notif = "Airing notifications: ON"
    else:
        notif = "Airing notifications: OFF"
    if await (CG.find_one({"_id": int(query[2])})):
        cr = "Crunchyroll Updates: ON"
    else:
        cr = "Crunchyroll Updates: OFF"
    if await (SG.find_one({"_id": int(query[2])})):
        sp = "Subsplease Updates: ON"
    else:
        sp = "Subsplease Updates: OFF"
    if query[1] == "sfw":
        if await (SFW_GRPS.find_one({"id": int(query[2])})):
            await SFW_GRPS.find_one_and_delete({"id": int(query[2])})
            sfw = "NSFW: Allowed"
        else:
            await SFW_GRPS.insert_one({"id": int(query[2])})
            sfw = "NSFW: Not Allowed"
    if query[1] == "notif":
        if await (AG.find_one({"_id": int(query[2])})):
            await AG.find_one_and_delete({"_id": int(query[2])})
            notif = "Airing notifications: OFF"
        else:
            await AG.insert_one({"_id": int(query[2])})
            notif = "Airing notifications: ON"
    if query[1] == "cr":
        if await (CG.find_one({"_id": int(query[2])})):
            await CG.find_one_and_delete({"_id": int(query[2])})
            cr = "Crunchyroll Updates: OFF"
        else:
            await CG.insert_one({"_id": int(query[2])})
            cr = "Crunchyroll Updates: ON"
    if query[1] == "sp":
        if await (SG.find_one({"_id": int(query[2])})):
            await SG.find_one_and_delete({"_id": int(query[2])})
            sp = "Subsplease Updates: OFF"
        else:
            await SG.insert_one({"_id": int(query[2])})
            sp = "Subsplease Updates: ON"
    btns = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=sfw, callback_data=f"settogl_sfw_{query[2]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=notif, callback_data=f"settogl_notif_{query[2]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=cr, callback_data=f"settogl_cr_{query[2]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=sp, callback_data=f"settogl_sp_{query[2]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Headlines", callback_data=f"headlines_call_{query[2]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Change UI", callback_data=f"cui_call_{query[2]}"
                )
            ]
        ]
    )
    await cq.answer()
    if query[1] == "call":
        await cq.edit_message_text(text=setting_text, reply_markup=btns)
    await cq.edit_message_reply_markup(reply_markup=btns)


@anibot.on_callback_query(filters.regex(pattern=r"myacc_(.*)"))
@check_user
async def flex_btn(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    query = cdata['data'].split("_")[1]
    user = cdata['data'].split("_").pop()
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    result = await get_user_activity(
        int(query), user=int(auser), duser=int(user)
    )
    pic, msg, btns = result
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg), reply_markup=btns
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg), reply_markup=btns
        )


@anibot.on_callback_query(filters.regex(pattern=r"myfavs_(.*)"))
@check_user
async def list_favourites_btn(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    q = cdata['data'].split("_")
    btn = [[
        InlineKeyboardButton(
            "ANIME", callback_data=f"myfavqry_ANIME_{q[1]}_1_{q[2]}_{q[3]}"
        ),
        InlineKeyboardButton(
            "CHARACTER", callback_data=f"myfavqry_CHAR_{q[1]}_1_{q[2]}_{q[3]}"
        ),
        InlineKeyboardButton(
            "MANGA", callback_data=f"myfavqry_MANGA_{q[1]}_1_{q[2]}_{q[3]}"
        )
    ]]
    if q[2] == "yes":
        btn.append(
            [InlineKeyboardButton("Back", callback_data=f"getusrbc_{q[3]}")]
        )
    else:
        btn.append(
            [
                InlineKeyboardButton(
                    "Profile",
                    url=f"https://anilist.co/user/{q[1]}"
                )
            ]
        )
    try:
        await cq.edit_message_media(
            InputMediaPhoto(
                f"https://img.anili.st/user/{q[1]}?a={time.time()}",
                caption="Choose one of the below options"
            ),
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog(
            'ANIBOT',
            f"https://img.anili.st/user/{q[1]}?a={time.time()}",
            'LINK',
            msg=cq
        )
        await cq.edit_message_media(
            InputMediaPhoto(
                failed_pic,
                caption="Choose one of the below options"
            ),
            reply_markup=InlineKeyboardMarkup(btn)
        )


@anibot.on_callback_query(filters.regex(pattern=r"myfavqry_(.*)"))
@check_user
async def favourites_btn(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    q = cdata['data'].split("_")
    if "-100" in str(q[5]):
        auser = await gcc(q[5])
    else:
        auser = q[5]
    pic, msg, btns = await get_user_favourites(
        q[2], int(auser), q[1], q[3], q[4], duser=int(q[5])
    )
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg), reply_markup=btns
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg), reply_markup=btns
        )


@anibot.on_callback_query(filters.regex(pattern=r"getusrbc_(.*)"))
@check_user
async def get_user_back_btn(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    query = cdata['data'].split("_")[1]
    if "-100" in str(query):
        auser = await gcc(query)
    else:
        auser = query
    result = await get_user(
        None, "flex", user=int(auser), display_user=query
    )
    pic, msg, btns = result
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg), reply_markup=btns
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg),creply_markup=btns
        )


@anibot.on_callback_query(filters.regex(pattern=r"fav_(.*)"))
@check_user
async def toggle_favourites_btn(
    client: Client, cq: CallbackQuery, cdata: dict
):
    query = cdata['data'].split("_")
    if query[1] == "ANIME" and len(query) > 4:
        try:
            ANIME_DB[query[3]]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    if query[1] == "MANGA":
        try:
            MANGA_DB[query[3]]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    if query[1] == "CHARACTER":
        try:
            CHAR_DB[query[3]]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    if query[1] == "STUDIO":
        try:
            STUDIO_DB[query[3]]
        except KeyError:
            return await cq.answer(
                "Query Expired!!!\nCreate new one", show_alert=True
            )
    idm = int(query[2])
    user = int(query.pop())
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    gid = cdata["message"]["chat"]["id"]
    rslt = await toggle_favourites(id_=idm, media=query[1], user=auser)
    if rslt == "ok":
        await cq.answer("Updated", show_alert=True)
    else:
        return await cq.answer("Failed to update!!!", show_alert=True)
    result = (
        (
            await get_anime(
                {"id": idm},
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[1] == "ANIME" and len(query) == 3
        else (
            await get_anilist(
                query[3],
                page=int(query[4]),
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[1] == "ANIME" and len(query) != 3
        else (
            await get_manga(
                query[3],
                page=int(query[4]),
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[1] == "MANGA"
        else (
            await get_airing(
                query[3],
                auth=True,
                user=auser,
                ind=int(query[4])
            )
        ) if query[1] == "AIRING"
        else (
            await get_character(
                query[3],
                int(query[4]),
                auth=True,
                user=auser
            )
        ) if query[1] == "CHARACTER"
        else (
            await get_studios(
                query[3],
                int(query[4]),
                user = auser,
                auth = True,
                duser = user
            )
        )
    )
    if query[1] == "STUDIO":
        return await cq.edit_message_text(
            result[0],
            reply_markup=result[1]
        )
    pic, msg = (
        (result[0], result[1]) if query[1] == "ANIME" and len(query) == 3
        else (result[0]) if query[1] == "AIRING"
        else (result[0], result[1][0])
    )
    btns = get_btns(
        query[1],
        result=result,
        user=user,
        auth=True,
        lsqry=query[3] if len(query) != 3 else None,
        lspage=int(query[4]) if len(query) != 3 else None
    )
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg), reply_markup=btns
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg), reply_markup=btns
        )


@anibot.on_callback_query(filters.regex(pattern=r"(lsadd|lsupdt)_(.*)"))
@check_user
async def list_update_anilist_btn(
    client: Client, cq: CallbackQuery, cdata: dict
):
    stts_ls = [
        "COMPLETED",
        "CURRENT",
        "PLANNING",
        "DROPPED",
        "PAUSED",
        "REPEATING"
    ]
    query = cdata['data'].split("_")
    btns = []
    row = []
    for i in stts_ls:
        row.append(
            InlineKeyboardButton(
                text=i,
                callback_data=cq.data.replace(
                    "lsadd",
                    f"lsas_{i}"
                ) if query[0] == "lsadd" else cq.data.replace(
                    "lsupdt",
                    f"lsus_{i}"
                )
            )
        )
        if len(row) == 3:
            btns.append(row)
            row = []
    if query[0] == "lsupdt":
        btns.append(
            [
                InlineKeyboardButton(
                    "Delete",
                    callback_data=cq.data.replace("lsupdt", f"dlt_{i}")
                )
            ]
        )
    await cq.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(btns)
    )


@anibot.on_callback_query(
    filters.regex(pattern=r"browse_(upcoming|trending|popular)_(.*)")
)
@check_user
async def browse_btn(client: Client, cq: CallbackQuery, cdata: dict):
    query = cdata['data'].split("_")
    if '•' in query[1]:
        return
    msg = await browse_(query[1])
    up = 'Upcoming' if query[1] != 'upcoming' else '• Upcoming •'
    tr = 'Trending' if query[1] != 'trending' else '• Trending •'
    pp = 'Popular' if query[1] != 'popular' else '• Popular •'
    btns = [[
        InlineKeyboardButton(
            tr, callback_data=f'browse_{tr.lower()}_{query[2]}'
        ),
        InlineKeyboardButton(
            pp, callback_data=f'browse_{pp.lower()}_{query[2]}'
        ),
        InlineKeyboardButton(
            up, callback_data=f'browse_{up.lower()}_{query[2]}'
        ),
    ]]
    await cq.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(btns))


@anibot.on_callback_query(filters.regex(pattern=r"(lsas|lsus|dlt)_(.*)"))
@check_user
async def update_anilist_btn(client: Client, cq: CallbackQuery, cdata: dict):
    query = cdata['data'].split("_")
    if query[2] == "ANIME":
        if len(query) == 7:
            try:
                ANIME_DB[query[4]]
            except KeyError:
                return await cq.answer(
                    "Query Expired!!!\nCreate new one", show_alert=True
                )
        if len(query) == 8:
            try:
                ANIME_DB[query[5]]
            except KeyError:
                return await cq.answer(
                    "Query Expired!!!\nCreate new one", show_alert=True
                )
    if query[2] == "MANGA":
        if len(query) == 7:
            try:
                MANGA_DB[query[4]]
            except KeyError:
                return await cq.answer(
                    "Query Expired!!!\nCreate new one", show_alert=True
                )
        if len(query) == 8:
            try:
                MANGA_DB[query[5]]
            except KeyError:
                return await cq.answer(
                    "Query Expired!!!\nCreate new one", show_alert=True
                )
    idm = int(query[3])
    user = int(query.pop())
    if "-100" in str(user):
        auser = await gcc(user)
    else:
        auser = user
    gid = cdata["message"]["chat"]["id"]
    eid = None
    if query[0] != "lsas":
        eid = int(query[4])
    rslt = await update_anilist(
        id_=idm, req=query[0], status=query[1], user=auser, eid=eid
    )
    if rslt == "ok":
        await cq.answer("Updated", show_alert=True)
    else:
        await cq.answer(
            "Something unexpected happened and operation failed successfully",
            show_alert=True
        )
        return
    result = (
        (
            await get_anime(
                {"id": idm},
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[2] == "ANIME" and (len(query) == 4 or len(query) == 5)
        else (
            await get_anilist(
                query[4],
                page=int(query[5]),
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[2] == "ANIME" and len(query) == 6
        else (
            await get_anilist(
                query[5],
                page=int(query[6]),
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[2] == "ANIME" and len(query) == 7
        else (
            await get_manga(
                query[4],
                page=int(query[5]),
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[2] == "MANGA" and len(query) == 6
        else (
            await get_manga(
                query[5],
                page=int(query[6]),
                auth=True,
                user=auser,
                cid=gid if gid != user else None
            )
        ) if query[2] == "MANGA" and len(query) == 7
        else (
            await get_airing(
                query[4] if eid is None else query[5],
                auth=True,
                user=auser,
                ind=int(query[5] if eid is None else query[6])
            )
        )
    )
    pic, msg = (
        (
            result[0], result[1]
        ) if query[2] == "ANIME" and (
            len(query) == 4 or len(query) == 5
        )
        else (result[0]) if query[2] == "AIRING"
        else (result[0], result[1][0])
    )
    btns = get_btns(
        query[2],
        result=result,
        user=user,
        auth=True,
        lsqry=query[4] if len(query) == 6
        else query[5] if len(query) == 7 
        else None,
        lspage=int(query[5]) if len(query) == 6
        else int(query[6]) if len(query) == 7
        else None
    )
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg), reply_markup=btns
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg), reply_markup=btns
        )


@anibot.on_callback_query(filters.regex(pattern=r"(desc|ls|char)_(.*)"))
@check_user
async def additional_info_btn(client: Client, cq: CallbackQuery, cdata: dict):
    q = cdata['data'].split("_")
    kek, qry, ctgry = q[0], q[1], q[2]
    info = (
        "<b>Description</b>"
        if kek == "desc"
        else "<b>Series List</b>"
        if kek == "ls"
        else "<b>Characters List</b>"
    )
    page = 0
    lsqry = f"_{q[3]}" if len(q) > 6 else ""
    lspg = f"_{q[4]}" if len(q) > 6 else ""
    if kek == 'char':
        page = q[6] if len(q) > 6 else q[4]
    rjsdata = await get_additional_info(qry, ctgry, kek, page=int(page))
    pic, result = rjsdata[0], rjsdata[1]
    button = []
    spoiler = False
    bot = BOT_NAME.replace("@", "")
    if result is None:
        await cq.answer('No description available!!!', show_alert=True)
        return
    if "~!" in result and "!~" in result:
        result = re.sub(r"~!.*!~", "[Spoiler]", result)
        spoiler = True
        button.append(
            [
                InlineKeyboardButton(
                    text="View spoiler",
                    url=f"https://t.me/{bot}/?start=des_{ctgry}_{qry}_desc"
                )
            ]
        )
    if len(result) > 1000:
        result = result[:940] + "..."
        if spoiler is False:
            result += "\n\nFor more info click below given button"
            button.append([
                InlineKeyboardButton(
                    text="More Info",
                    url=f"https://t.me/{bot}/?start=des_{ctgry}_{qry}_{kek}"
                )
            ])
    add_ = ""
    user = q.pop()
    if kek == 'char':
        btndata = rjsdata[2]
        if btndata['lastPage'] != 1:
            qs = q[5] if len(q) != 5 else q[3]
            pre = f'{kek}_{qry}_{ctgry}{lsqry}{lspg}_{qs}_{int(page)-1}_{user}'
            nex = f'{kek}_{qry}_{ctgry}{lsqry}{lspg}_{qs}_{int(page)+1}_{user}'
            if page == '1':
                button.append([
                    InlineKeyboardButton(
                        text="Next",
                        callback_data=nex
                    )
                ])
            elif btndata['lastPage'] == int(page):
                button.append([
                    InlineKeyboardButton(
                        text="Prev",
                        callback_data=pre
                    )
                ])
            else:
                button.append([
                    InlineKeyboardButton(
                        text="Prev",
                        callback_data=pre
                    ),
                    InlineKeyboardButton(
                        text="Next",
                        callback_data=nex
                    )
                ])
        add_ = f"\n\nTotal Characters: {btndata['total']}"
    msg = f"{info}:\n\n{result+add_}"
    cbd = (
        f"btn_{qry}_{q[3]}_{user}" if len(q) <= 5
        else f"page_ANIME{lsqry}{lspg}_{q[5]}_{user}" if ctgry == "ANI"
        else f"page_CHARACTER{lsqry}{lspg}_{q[5]}_{user}"
    )
    button.append([InlineKeyboardButton(text="Back", callback_data=cbd)])
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg),
            reply_markup=InlineKeyboardMarkup(button)
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg),
            reply_markup=InlineKeyboardMarkup(button)
        )
    await cq.answer()


@anibot.on_callback_query(filters.regex(pattern=r"lsc_(.*)"))
@check_user
async def featured_in_btn(client: Client, cq: CallbackQuery, cdata: dict):
    kek, idm, qry, pg, auth, usr = cdata['data'].split("_")
    result = await get_featured_in_lists(int(idm), "ANI")
    req = "lscm"
    if result[0] is False:
        result = await get_featured_in_lists(int(idm), "MAN")
        req = None
        if result[0] is False:
            await cq.answer("No Data Available!!!", show_alert=True)
            return
    [msg, total], pic = result
    button = []
    totalpg, kek = divmod(total, 15)
    if kek != 0:
        totalpg + 1
    if total > 15:
        button.append([InlineKeyboardButton(
            text="Next", callback_data=f"lsca_{idm}_1_{qry}_{pg}_{auth}_{usr}"
        )])
    if req is not None:
        button.append([InlineKeyboardButton(
            text="Manga", callback_data=f"lscm_{idm}_0_{qry}_{pg}_{auth}_{usr}"
        )])
    button.append([InlineKeyboardButton(
        text="Back", callback_data=f"page_CHARACTER_{qry}_{pg}_{auth}_{usr}"
    )])
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg),
            reply_markup=InlineKeyboardMarkup(button)
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg),
            reply_markup=InlineKeyboardMarkup(button)
        )


@anibot.on_callback_query(filters.regex(pattern=r"lsc(a|m)_(.*)"))
@check_user
async def featured_in_switch_btn(
    client: Client, cq: CallbackQuery, cdata: dict
):
    req, idm, reqpg, qry, pg, auth, user = cdata['data'].split("_")
    result = await get_featured_in_lists(
        int(idm), "MAN" if req == "lscm" else "ANI", page=int(reqpg)
    )
    reqb = "lsca" if req == "lscm" else "lscm"
    bt = "Anime" if req == "lscm" else "Manga"
    if result[0] is False:
        await cq.answer("No Data Available!!!", show_alert=True)
        return
    [msg, total], pic = result
    totalpg, kek = divmod(total, 15)
    if kek != 0:
        totalpg + 1
    button = []
    if total > 15:
        nex = f"{req}_{idm}_{int(reqpg)+1}_{qry}_{pg}_{auth}_{user}"
        bac = f"{req}_{idm}_{int(reqpg)-1}_{qry}_{pg}_{auth}_{user}"
        if int(reqpg) == 0:
            button.append([
                InlineKeyboardButton(
                    text="Next",
                    callback_data=nex
                )
            ])
        elif int(reqpg) == totalpg:
            button.append([
                InlineKeyboardButton(
                    text="Back",
                    callback_data=bac
                )
            ])
        else:
            button.append([
                InlineKeyboardButton(
                    text="Back",
                    callback_data=bac
                ),
                InlineKeyboardButton(
                    text="Next",
                    callback_data=nex
                )
            ])
    button.append([InlineKeyboardButton(
        text=f"{bt}",
        callback_data=f"{reqb}_{idm}_0_{qry}_{pg}_{auth}_{user}"
    )])
    button.append([InlineKeyboardButton(
        text="Back",
        callback_data=f"page_CHARACTER_{qry}_{pg}_{auth}_{user}"
    )])
    try:
        await cq.edit_message_media(
            InputMediaPhoto(pic, caption=msg),
            reply_markup=InlineKeyboardMarkup(button)
        )
    except (WebpageMediaEmpty, WebpageCurlFailed):
        await clog('ANIBOT', pic, 'LINK', msg=cq)
        await cq.edit_message_media(
            InputMediaPhoto(failed_pic, caption=msg),
            reply_markup=InlineKeyboardMarkup(button)
        )


headlines_text = '''
Turn LiveChart option on to get news feeds from livechart.me
Turn MyAnimeList option on to get news feeds from myanimelist.net

For Auto Pin and Auto Unpin features, give the bot "Pin Message" and "Delete Message" perms
Auto Unpin can be customized, click on the button to see available options
'''

@anibot.on_callback_query(filters.regex(pattern=r"headlines_(.*)"))
async def headlines_btn(client: Client, cq: CallbackQuery):
    cus = cq.from_user.id
    qry = cq.data.split('_')[1]
    gid = int(cq.data.split('_')[2])
    try:
        k = (await client.get_chat_member(gid, cus)).status
    except UserNotParticipant:
        await cq.answer()
        return
    if cus not in OWNER and k == MEMBER:
        await cq.answer(
            "You don't have enough permissions to change this!!!",
            show_alert=True
        )
        return
    lcdata = await HD.find_one({'_id': gid})
    maldata = await MHD.find_one({'_id': gid})
    lchd = "LiveChart: OFF"
    malhd = "MyAnimeList: OFF"
    malhdpin = lchdpin = "Auto Pin: OFF"
    malpin = lcpin = None
    if lcdata:
        lchd = "LiveChart: ON"
        try:
            lcpin = lcdata['pin']
            lchdpin = f"Auto Pin: {lcpin}"
        except KeyError:
            pass
    if maldata:
        malhd = "MyAnimeList: ON"
        try:
            malpin = maldata['pin']
            malhdpin = f"Auto Pin: {malpin}"
        except KeyError:
            pass
    if "mal" in qry:
        data = maldata
        pin = malpin
        pin_msg = malhdpin
        collection = MHD
        src_status = malhd
        srcname = "MyAnimeList"
    else:
        data = lcdata
        pin = lcpin
        pin_msg = lchdpin
        collection = HD
        src_status = lchd
        srcname = "LiveChart"
    if re.match(r"^(mal|lc)hd$", qry):
        if data:
            await collection.find_one_and_delete(data)
            src_status = f"{srcname}: OFF"
            pin_msg = f"Auto Pin: OFF"
        else:
            await collection.insert_one({"_id": gid})
            src_status = f"{srcname}: ON"
            pin_msg = f"Auto Pin: OFF"
    if re.match(r"^(mal|lc)hdpin$", qry):
        if data:
            if pin:
                switch = "ON" if pin=="OFF" else "OFF"
                await collection.find_one_and_update(data, {"$set": {"pin": switch, "unpin": None}}, upsert=True)
                pin_msg = f"Auto Pin: {switch}"
            else:
                await collection.find_one_and_update(data, {"$set": {"pin": "ON"}}, upsert=True)
                pin_msg = f"Auto Pin: ON"
        else:
            await cq.answer(f"Please enable {srcname} first!!!", show_alert=True)
    if "mal" in qry:
        malhdpin = pin_msg
        malhd = src_status
    else:
        lchdpin = pin_msg
        lchd = src_status
    btn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=lchd, callback_data=f"headlines_lchd_{gid}")
            ],
            [
                InlineKeyboardButton(text=lchdpin, callback_data=f"headlines_lchdpin_{gid}"),
                InlineKeyboardButton(text="Auto Unpin (LC)", callback_data=f"unpin_call_lc_{gid}")
            ],
            [
                InlineKeyboardButton(text=malhd, callback_data=f"headlines_malhd_{gid}")
            ],
            [
                InlineKeyboardButton(text=malhdpin, callback_data=f"headlines_malhdpin_{gid}"),
                InlineKeyboardButton(text="Auto Unpin (MAL)", callback_data=f"unpin_call_mal_{gid}")
            ],
            [
                InlineKeyboardButton(text="Back", callback_data=f"settogl_call_{gid}")
            ]
        ]
    )
    await cq.edit_message_text(headlines_text, reply_markup=btn)
    await cq.answer()


TIMES = {
    "1 day": 86400,
    "5 days": 432000,
    "1 week": 604800,
    "2 week": 1209600,
    "1 month": 2592000,
    "New Feed": 0,
    "OFF": None
}


@anibot.on_callback_query(filters.regex(pattern=r"unpin_(.*)"))
async def auto_unpin(client: Client, cq: CallbackQuery):
    cus = cq.from_user.id
    qry = cq.data.split('_')[1]
    src = cq.data.split('_')[2]
    gid = int(cq.data.split('_')[3])
    try:
        k = (await client.get_chat_member(gid, cus)).status
    except UserNotParticipant:
        await cq.answer()
        return
    if cus not in OWNER and k == MEMBER:
        await cq.answer(
            "You don't have enough permissions to change this!!!",
            show_alert=True
        )
        return
    cancel = False
    if src == "lc":
        srcname = "LiveChart"
        collection = HD
    else:
        srcname = "MyAnimeList"
        collection = MHD
    data = await collection.find_one({'_id': gid})
    if data:
        try:
            data['pin']
            try:
                unpin = data['unpin']
            except KeyError:
                unpin = None
        except KeyError:
            cancel = True
    else:
        cancel = True
    if cancel:
        return await cq.answer(f"Please enable {srcname} and Auto Pin option for them!!!", show_alert=True)
    setting = None
    if qry=="call":
        pass
    elif qry == "None":
        setting = {"unpin": None}
    elif qry.isdigit():
        if int(qry)==0:
            unpin = int(qry)
            setting = {"unpin": 0}
        else:
            now = round(time.time(), -2)
            unpin = int(qry)
            setting = {"unpin": int(qry), "next_unpin": int(qry)+int(now)}
    if setting:
        await collection.find_one_and_update(data, {"$set": setting})
    btn = []
    row = []
    count = 0
    for i in TIMES.keys():
        count = count + 1
        row.append(InlineKeyboardButton(i, callback_data=f"unpin_{TIMES[i]}_{src}_{gid}"))
        if count == 3:
            btn.append(row)
            count = 0
            row = []
    if len(row)!=0:
        btn.append(row)
    btn.append([InlineKeyboardButton("Back", callback_data=f"headlines_call_{gid}")])
    if type(unpin) is int:
        if unpin == 0:
            unpindata = "after Next Feed"
        else:
            unpindata = "after "+list(TIMES.keys())[list(TIMES.values()).index(unpin)]
    else:
        unpindata = "OFF"
    await cq.edit_message_text(
        f"Auto Unpin options for {srcname}\nCurrently set to: {unpindata}",
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await cq.answer()


BULLETS = ["➤", "•", "⚬", "▲", "▸", "△", "⋟", "»", "None"]


@anibot.on_callback_query(filters.regex(pattern=r"cui_(.*)"))
async def change_ui_btn(client: Client, cq: CallbackQuery):
    cus = cq.from_user.id
    qry = cq.data.split('_')[1]
    gid = cq.data.split('_')[2]
    try:
        k = (await client.get_chat_member(gid, cus)).status
    except UserNotParticipant:
        await cq.answer()
        return
    if cus not in OWNER and k == MEMBER:
        await cq.answer(
            "You don't have enough permissions to change this!!!",
            show_alert=True
        )
        return
    await cq.answer()
    row, btn = [], []
    for i in BULLETS:
        row.append(InlineKeyboardButton(
            text=i, callback_data=f"cui_{i}_{gid}"))
        if len(row) == 3:
            btn.append(row)
            row = []
    btn.append(row)
    btn.append([
        InlineKeyboardButton(
            text="Caps",
            callback_data=f"cui_Caps_{gid}"
        ),
        InlineKeyboardButton(
            text="UPPER",
            callback_data=f"cui_UPPER_{gid}"
        )
    ])
    btn.append([InlineKeyboardButton(
        text="Back", callback_data=f"settogl_call_{gid}")])
    if qry in ["Caps", "UPPER"]:
        if await GUI.find_one({"_id": gid}):
            await GUI.update_one({"_id": gid}, {"$set": {"cs": qry}})
        else:
            await GUI.insert_one({"_id": gid, "bl": "➤", "cs": qry})
    elif qry != "call":
        bullet = qry
        if qry == "None":
            bullet = None
        if await GUI.find_one({"_id": gid}):
            await GUI.update_one({"_id": gid}, {"$set": {"bl": bullet}})
        else:
            await GUI.insert_one({"_id": gid, "bl": bullet, "cs": "UPPER"})
    bl = "➤"
    cs = "UPPER"
    if await GUI.find_one({"_id": gid}):
        data = (await GUI.find_one({"_id": gid}))
        bl = data["bl"]
        cs = data["cs"]
    text = f"""Selected bullet in this group: {bl}
Selected text case in this group: {cs}"""
    await cq.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btn))


## For accepting commands from edited messages

@anibot.on_edited_message(
    filters.command(["anime", f"anime{BOT_NAME}"], prefixes=trg)
)
async def anime_edit_cmd(client: anibot, message: Message):
    await anime_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["manga", f"manga{BOT_NAME}"], prefixes=trg)
)
async def manga_edit_cmd(client: anibot, message: Message):
    await manga_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["character", f"character{BOT_NAME}"], prefixes=trg)
)
async def character_edit_cmd(client: anibot, message: Message):
    await character_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["anilist", f"anilist{BOT_NAME}"], prefixes=trg)
)
async def anilist_edit_cmd(client: anibot, message: Message):
    await anilist_cmd(client, message)


@anibot.on_edited_message(
    filters.command(
        ["flex", f"flex{BOT_NAME}", "user", f"user{BOT_NAME}"],
        prefixes=trg
    )
)
async def flex_edit_cmd(client: anibot, message: Message):
    await flex_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["top", f"top{BOT_NAME}"], prefixes=trg)
)
async def top_edit_cmd(client: anibot, message: Message):
    await top_tags_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["airing", f"airing{BOT_NAME}"], prefixes=trg)
)
async def airing_edit_cmd(client: anibot, message: Message):
    await airing_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["auth", f"auth{BOT_NAME}"], prefixes=trg)
)
async def auth_edit_cmd(client: anibot, message: Message):
    await auth_link_cmd(client, message)


@anibot.on_edited_message(
    ~filters.private & filters.command(
        ["settings", f"settings{BOT_NAME}"],
        prefixes=trg
    )
)
async def settings_edit_cmd(client: anibot, message: Message):
    await settings_cmd(client, message)


@anibot.on_edited_message(
    filters.private & filters.command("code", prefixes=trg)
)
async def code_edit_cmd(client: anibot, message: Message):
    await code_cmd(client, message)


@anibot.on_edited_message(
    filters.command(
        ["me", f"me{BOT_NAME}", "activity", f"activity{BOT_NAME}"],
        prefixes=trg
    )
)
async def activity_edit_cmd(client: anibot, message: Message):
    await activity_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["favourites", f"favourites{BOT_NAME}"], prefixes=trg)
)
async def favourites_edit_cmd(client: anibot, message: Message):
    await favourites_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["logout", f"logout{BOT_NAME}"], prefixes=trg)
)
async def logout_edit_cmd(client: anibot, message: Message):
    await logout_cmd(client, message)


@anibot.on_edited_message(
    filters.command(["browse", f"browse{BOT_NAME}"], prefixes=trg)
)
async def browse_edit_cmd(client: anibot, message: Message):
    await browse_cmd(client, message)


@anibot.on_edited_message(
    filters.command(
        ["gettags", f"gettags{BOT_NAME}", "getgenres", f"getgenres{BOT_NAME}"],
        prefixes=trg
    )
)
async def tags_genres_edit_cmd(client: anibot, message: Message):
    await list_tags_genres_cmd(client, message)


@anibot.on_message(
    filters.command(["studio", f"studio{BOT_NAME}"], prefixes=trg)
)
async def studio_edit_cmd(client: Client, message: Message):
    await studio_cmd(client, message)
