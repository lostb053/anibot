# base code was taken from @DeletedUser420's Userge-Plugins repo
# originally authored by Phyco-Ninja (https://github.com/Phyco-Ninja) (@PhycoNinja13b)
# I've just tweaked his file a bit (maybe a lot)
# But i sticked to the format he used which looked cool

""" Search for Anime related Info using Anilist API """


import asyncio, requests, time, random, re
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message
from .. import ANILIST_CLIENT, ANILIST_REDIRECT_URL, ANILIST_SECRET, HELP_DICT, OWNER, TRIGGERS as trg, BOT_NAME
from ..utils.data_parser import (
    get_all_genres, get_all_tags, get_top_animes, get_user_activity, get_user_favourites, toggle_favourites,
    get_anime, get_airing, get_anilist, get_character, get_additional_info, get_manga,
    get_featured_in_lists, update_anilist, get_user, ANIME_DB, MANGA_DB
)
from ..utils.helper import check_user, get_btns, AUTH_USERS, rand_key, clog
from ..utils.db import get_collection

GROUPS = get_collection("GROUPS")
SFW_GRPS = get_collection("SFW_GROUPS")
DC = get_collection('DISABLED_CMDS')
AG = get_collection('AIRING_GROUPS')

no_pic = [
    'https://telegra.ph/file/0d2097f442e816ba3f946.jpg',
    'https://telegra.ph/file/5a152016056308ef63226.jpg',
    'https://telegra.ph/file/d2bf913b18688c59828e9.jpg',
    'https://telegra.ph/file/d53083ea69e84e3b54735.jpg',
    'https://telegra.ph/file/b5eb1e3606b7d2f1b491f.jpg'
]


@Client.on_message(filters.command(["anime", f"anime{BOT_NAME}"], prefixes=trg))
async def anime_cmd(client: Client, message: Message):
    """Search Anime Info"""
    text = message.text.split(" ", 1)
    gid = message.chat
    if gid.type in ["supergroup", "group"] and not await (GROUPS.find_one({"id": gid.id})):
        await asyncio.gather(GROUPS.insert_one({"id": gid.id, "grp": gid.title}))
        await clog("ANIBOT", f"Bot added to a new group\n\n{gid.username or gid.title}\nID: `{gid.id}`", "NEW_GROUP")
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'anime' in find_gc['cmd_list'].split():
        return
    if len(text)==1:
        k = await message.reply_text("Please give a query to search about\nexample: /anime Ao Haru Ride")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    auth = False
    vars_ = {"search": query}
    if query.isdigit():
        vars_ = {"id": int(query)}
    user = message.from_user.id
    if (await AUTH_USERS.find_one({"id": user})):
        auth = True
    result = await get_anime(vars_, user=user, auth=auth)
    if len(result) != 1:
        title_img, finals_ = result[0], result[1]
    else:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    buttons = get_btns("ANIME", result=result, user=user, auth=auth)
    if await (SFW_GRPS.find_one({"id": gid.id})) and result[2].pop()=="True":
        await client.send_photo(message.chat.id, no_pic[random.randint(0, 4)], caption="This anime is marked 18+ and not allowed in this group")
        return
    await client.send_photo(message.chat.id, title_img, caption=finals_, reply_markup=buttons)


@Client.on_message(filters.command(["manga", f"manga{BOT_NAME}"], prefixes=trg))
async def manga_cmd(client: Client, message: Message):
    """Search Manga Info"""
    text = message.text.split(" ", 1)
    gid = message.chat
    if gid.type in ["supergroup", "group"] and not await (GROUPS.find_one({"id": gid.id})):
        await asyncio.gather(GROUPS.insert_one({"id": gid.id, "grp": gid.title}))
        await clog("ANIBOT", f"Bot added to a new group\n\n{gid.username or gid.title}\nID: `{gid.id}`", "NEW_GROUP")
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'manga' in find_gc['cmd_list'].split():
        return
    if len(text)==1:
        k = await message.reply_text("Please give a query to search about\nexample: /manga The teasing master Takagi san")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    qdb = rand_key()
    MANGA_DB[qdb] = query
    auth = False
    user = message.from_user.id
    if (await AUTH_USERS.find_one({"id": user})):
        auth = True
    result = await get_manga(qdb, 1, auth=auth, user=user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, finals_ = result[0], result[1][0]
    buttons = get_btns("MANGA", lsqry=qdb, lspage=1, user=user, result=result, auth=auth)
    if await (SFW_GRPS.find_one({"id": message.chat.id})) and result[2].pop()=="True":
        buttons = get_btns("MANGA", lsqry=qdb, lspage=1, user=user, result=result, auth=auth, sfw="True")
        await client.send_photo(message.chat.id, no_pic[random.randint(0, 4)], caption="This manga is marked 18+ and not allowed in this group", reply_markup=buttons)
        return
    await client.send_photo(message.chat.id, pic, caption=finals_, reply_markup=buttons)


@Client.on_message(filters.command(["character", f"character{BOT_NAME}"], prefixes=trg))
async def character_cmd(client: Client, message: Message):
    """Get Info about a Character"""
    text = message.text.split(" ", 1)
    gid = message.chat
    if gid.type in ["supergroup", "group"] and not await (GROUPS.find_one({"id": gid.id})):
        await asyncio.gather(GROUPS.insert_one({"id": gid.id, "grp": gid.title}))
        await clog("ANIBOT", f"Bot added to a new group\n\n{gid.username or gid.title}\nID: `{gid.id}`", "NEW_GROUP")
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'character' in find_gc['cmd_list'].split():
        return
    if len(text)==1:
        k = await message.reply_text("Please give a query to search about\nexample: /character Nezuko")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    var = {"search": query}
    auth = False
    user = message.from_user.id
    if (await AUTH_USERS.find_one({"id": user})):
        auth = True
    result = await get_character(var, auth=auth, user=user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    img = result[0]
    cap_text = result[1][0]
    buttons = get_btns("CHARACTER", user=user, lsqry=query, lspage=1, result=result, auth=auth)
    await client.send_photo(message.chat.id, img, caption=cap_text, reply_markup=buttons)


@Client.on_message(filters.command(["anilist", f"anilist{BOT_NAME}"], prefixes=trg))
async def anilist_cmd(client: Client, message: Message):
    text = message.text.split(" ", 1)
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'anilist' in find_gc['cmd_list'].split():
        return
    if len(text)==1:
        k = await message.reply_text("Please give a query to search about\nexample: /anilist rezero")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    qdb = rand_key()
    ANIME_DB[qdb] = query
    auth = False
    user = message.from_user.id
    if (await AUTH_USERS.find_one({"id": user})):
        auth = True
    result = await get_anilist(qdb, 1, auth=auth, user=user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, msg = result[0], result[1][0]
    buttons = get_btns("ANIME", lsqry=qdb, lspage=1, result=result, user=user, auth=auth)
    if await (SFW_GRPS.find_one({"id": message.chat.id})) and result[2].pop()=="True":
        buttons = get_btns("ANIME", lsqry=qdb, lspage=1, result=result, user=user, auth=auth, sfw="True")
        await client.send_photo(message.chat.id, no_pic[random.randint(0, 4)], caption="This anime is marked 18+ and not allowed in this group", reply_markup=buttons)
        return
    await client.send_photo(message.chat.id, pic, caption=msg, reply_markup=buttons)


@Client.on_message(filters.command(["flex", f"flex{BOT_NAME}", "user", f"user{BOT_NAME}"], prefixes=trg))
async def flex_cmd(client: Client, message: Message):
    query = message.text.split(" ", 1)
    qry = None
    find_gc = await DC.find_one({'_id': message.chat.id})
    if "user" in query[0]:
        if find_gc!=None and 'user' in find_gc['cmd_list'].split():
            return
        if not len(query)==2:
            k = await message.reply_text("Please give an anilist username to search about\nexample: /user Lostb053")
            await asyncio.sleep(5)
            return await k.delete()
        else:
            qry = {"search": query[1]}
    if find_gc!=None and 'flex' in find_gc['cmd_list'].split():
        return
    user = message.from_user.id
    if not "user" in query[0] and not (await AUTH_USERS.find_one({"id": user})):
        bot_us = (await client.get_me()).username
        return await message.reply_text(
            "Please connect your account first to use this cmd",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Auth", url=f"https://t.me/{bot_us}/?start=auth")]])
        )
    result = await get_user(qry, query[0], user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, msg, buttons = result
    await client.send_photo(message.chat.id, pic, caption=msg, reply_markup=buttons)


@Client.on_message(filters.command(["top", f"top{BOT_NAME}"], prefixes=trg))
async def top_tags_cmd(client: Client, message: Message):
    query = message.text.split(" ", 1)
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'top' in find_gc['cmd_list'].split():
        return
    get_tag = "None"
    if len(query)==2:
        get_tag = query[1]
    user = message.from_user.id
    result = await get_top_animes(get_tag, 1, user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    msg, buttons = result
    await client.send_message(message.chat.id, msg, reply_markup=buttons)


@Client.on_message(filters.command(["airing", f"airing{BOT_NAME}"], prefixes=trg))
async def airing_cmd(client: Client, message: Message):
    """Get Airing Detail of Anime"""
    text = message.text.split(" ", 1)
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'airing' in find_gc['cmd_list'].split():
        return
    if len(text)==1:
        k = await message.reply_text("Please give a query to search about\nexample: /airing Fumetsu no Anata e")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    vars_ = {"search": query}
    if query.isdigit():
        vars_ = {"id": int(query), "asHtml": True}
    auth = False
    user = message.from_user.id
    if (await AUTH_USERS.find_one({"id": user})):
        auth = True
    result = await get_airing(vars_, auth=auth, user=user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    coverImg, out = result[0]
    btn = get_btns("AIRING", user=user, result=result, auth=auth)
    if await (SFW_GRPS.find_one({"id": message.chat.id})) and result[2].pop()=="True":
        await client.send_photo(message.chat.id, no_pic[random.randint(0, 4)], caption="This anime is marked 18+ and not allowed in this group")
        return
    await client.send_photo(message.chat.id, coverImg, caption=out, reply_markup=btn)


@Client.on_message(filters.private & filters.command("auth", prefixes=trg))
async def auth_link_cmd(client, message: Message):
    await message.reply_text(
        text = """Follow the steps to complete Authorization:
1. Click the below button
2. Authorize the app and copy the authorization code
3. Send the code along with cmd /code like '/code <u>auth code from website</u>'""",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
            text="Authorize",
            url=f"https://anilist.co/api/v2/oauth/authorize?client_id={ANILIST_CLIENT}&redirect_uri={ANILIST_REDIRECT_URL}&response_type=code"
        )]])
    )


@Client.on_message(~filters.private & filters.command(["settings", f"settings{BOT_NAME}"], prefixes=trg))
async def sfw_cmd(client: Client, message: Message):
    if message.from_user.id in OWNER or (await client.get_chat_member(message.chat.id, message.from_user.id)).status!='member':
        text = "This allows you to change group settings\n\nNSFW toggle switches on filtering of 18+ marked content\nAiring notifications notifies about airing of anime in recent"
        sfw = "NSFW: Allowed"
        if await (SFW_GRPS.find_one({"id": message.chat.id})):
            sfw = "NSFW: Not Allowed"
        notif = "Airing notifications: OFF"
        if await (AG.find_one({"_id": message.chat.id})):
            notif = "Airing notifications: ON"
        await message.reply_text(
            text = text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=sfw, callback_data=f"settogl_sfw_{message.chat.id}")],
                [InlineKeyboardButton(text=notif, callback_data=f"settogl_notif_{message.chat.id}")]
            ])
        )


@Client.on_message(filters.private & filters.command("code", prefixes=trg))
async def code_cmd(client, message: Message):
    text = message.text.split(" ", 1)
    if len(text)==1:
        k = await message.reply_text("Needs code!!!")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    json = {
        'grant_type': 'authorization_code',
        'client_id': ANILIST_CLIENT,
        'client_secret': ANILIST_SECRET,
        'redirect_uri': ANILIST_REDIRECT_URL,
        'code': query
    }
    if (await AUTH_USERS.find_one({"id": message.from_user.id})):
        return await message.reply_text("You have already yourself\nIf you wish to logout send /logout")
    response: dict = requests.post("https://anilist.co/api/v2/oauth/token", headers=headers, json=json).json()
    if response.get("access_token"):
        await asyncio.gather(AUTH_USERS.insert_one({"id": message.from_user.id, "token": response.get("access_token")}))
        await message.reply_text("Authorization Successfull!!!" )
    else:
        await message.reply_text("Please verify code, or get new one from website!!!")


@Client.on_message(filters.command(["me", f"me{BOT_NAME}", "activity", f"activity{BOT_NAME}"], prefixes=trg))
async def activity_cmd(client: Client, message: Message):
    user = message.from_user.id
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and ('me' or 'activity') in find_gc['cmd_list'].split():
        return
    if not (await AUTH_USERS.find_one({"id": user})):
        bot_us = (await client.get_me()).username
        return await message.reply_text(
            "Please connect your account first to use this cmd",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Auth", url=f"https://t.me/{bot_us}/?start=auth")]])
        )
    result = await get_user(None, "flex", user)
    query = result[0].split("/").pop().split("?")[0]
    result = await get_user_activity(int(query), user=int(user))
    pic, msg, kek = result
    btns = InlineKeyboardMarkup([[InlineKeyboardButton("Profile", url=f"https://anilist.co/user/{query}")]])
    await client.send_photo(message.chat.id, pic, caption=msg, reply_markup=btns)


@Client.on_message(filters.command(["favourites", f"favourites{BOT_NAME}"], prefixes=trg))
async def favourites_cmd(client: Client, message: Message):
    user = message.from_user.id
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'favourites' in find_gc['cmd_list'].split():
        return
    if not (await AUTH_USERS.find_one({"id": user})):
        bot_us = (await client.get_me()).username
        return await message.reply_text(
            "Please connect your account first to use this cmd",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Auth", url=f"https://t.me/{bot_us}/?start=auth")]])
        )
    q = message.from_user.id
    result = await get_user(None, "flex", user)
    query = result[0].split("/").pop().split("?")[0]
    btn = InlineKeyboardMarkup(
        [   
            [
                InlineKeyboardButton("ANIME", callback_data=f"myfavqry_ANIME_{query}_1_no_{q}"),
                InlineKeyboardButton("CHARACTER", callback_data=f"myfavqry_CHAR_{query}_1_no_{q}"),
                InlineKeyboardButton("MANGA", callback_data=f"myfavqry_MANGA_{query}_1_no_{q}")
            ],
            [
                InlineKeyboardButton("Profile", url=f"https://anilist.co/user/{query}")
            ]
        ]
    )
    await client.send_photo(message.chat.id, result[0], caption="Choose one of the below options", reply_markup=btn)


@Client.on_message(filters.private & filters.command("logout", prefixes=trg))
async def logout_cmd(client, message: Message):
    if (await AUTH_USERS.find_one({"id": message.from_user.id})):
        asyncio.gather(AUTH_USERS.find_one_and_delete({"id": message.from_user.id}))
        await message.reply_text("Logged out!!!")
    else:
        await message.reply_text("You are not authorized to begin with!!!")


@Client.on_message(filters.command(["gettags", f"gettags{BOT_NAME}", "getgenres", f"getgenres{BOT_NAME}"], prefixes=trg))
async def list_tags_genres_cmd(client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and "gettags" in message.text.split()[0] and 'gettags' in find_gc['cmd_list'].split():
        return
    if find_gc!=None and "getgenres" in message.text.split()[0] and 'getgenres' in find_gc['cmd_list'].split():
        return
    msg = (await get_all_tags()) if "gettags" in message.text.split()[0] else (await get_all_genres())
    await message.reply_text(msg)


@Client.on_callback_query(filters.regex(pattern=r"page_(.*)"))
@check_user
async def page_btn(client, cq: CallbackQuery):
    kek, media, query, page, auth, user = cq.data.split("_")
    if media=="ANIME":
        try:
            ANIME_DB[query]
        except KeyError:
            return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
    if media=="MANGA":
        try:
            MANGA_DB[query]
        except KeyError:
            return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
    await cq.answer()
    get_pg = {"search": query, "page": int(page)}
    authbool = bool(1) if auth=="True" else bool(0)
    result = (
        (await get_anilist(query, int(page), auth=authbool, user=int(user)))
        if media == "ANIME"
        else (await get_character(get_pg, auth=authbool, user=int(user)))
        if media == "CHARACTER"
        else (await get_manga(query, int(page), auth=authbool, user=int(user)))
    )
    pic, msg = result[0], result[1][0]
    button = get_btns(media, lsqry=query, lspage=int(page), result=result, user=user, auth=authbool)
    if await (SFW_GRPS.find_one({"id": cq.message.chat.id})) and media!="CHARACTER" and result[2].pop()=="True":
        button = get_btns(media, lsqry=query, lspage=int(page), result=result, user=user, auth=authbool, sfw="True")
        await cq.edit_message_media(InputMediaPhoto(no_pic[random.randint(0, 4)], caption="This material is marked 18+ and not allowed in this group"), reply_markup=button)
        return
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=button)


@Client.on_callback_query(filters.regex(pattern=r"btn_(.*)"))
@check_user
async def anime_btn(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")
    idm = query[1]
    user = int(cq.data.split("_").pop())
    authbool = bool(1) if query[2]=="True" else bool(0)
    vars_ = {"id": int(idm)}
    result = await get_anime(vars_, auth=authbool, user=user)
    pic, msg = result[0], result[1]
    btns = get_btns("ANIME", result=result, user=user, auth=authbool)
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"topanimu_(.*)"))
@check_user
async def top_tags_btn(client, cq: CallbackQuery):
    await cq.answer()
    kek, gnr, page, user = cq.data.split("_")
    result = await get_top_animes(gnr, page=page, user=user)
    msg, buttons = result[0], result[1]
    await cq.edit_message_text(msg, reply_markup=buttons)


@Client.on_callback_query(filters.regex(pattern=r"settogl_(.*)"))
async def nsfw_toggle_btn(client, cq: CallbackQuery):
    k = await cq.message.chat.get_member(cq.from_user.id)
    if cq.from_user.id not in OWNER and str(k.status)!="administrator":
        await cq.answer("You don't have enough permissions to change this!!!", show_alert=True)
        return
    await cq.answer()
    query = cq.data.split("_")
    if await (SFW_GRPS.find_one({"id": int(query[2])})):
        sfw = "NSFW: Not Allowed"
    else:
        sfw = "NSFW: Allowed"
    if await (AG.find_one({"_id": int(query[2])})):
        notif = "Airing notifications: ON"
    else:
        notif = "Airing notifications: OFF"
    if query[1]=="sfw":
        if await (SFW_GRPS.find_one({"id": int(query[2])})):
            await asyncio.gather(SFW_GRPS.find_one_and_delete({"id": int(query[2])}))
            sfw = "NSFW: Allowed"
        else:
            await asyncio.gather(SFW_GRPS.insert_one({"id": int(query[2])}))
            sfw = "NSFW: Not Allowed"
    if query[1]=="notif":
        if await (AG.find_one({"_id": int(query[2])})):
            await asyncio.gather(AG.find_one_and_delete({"_id": int(query[2])}))
            notif = "Airing notifications: OFF"
        else:
            await asyncio.gather(AG.insert_one({"_id": int(query[2])}))
            notif = "Airing notifications: ON"
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=sfw, callback_data=f"settogl_sfw_{query[2]}")],
        [InlineKeyboardButton(text=notif, callback_data=f"settogl_notif_{query[2]}")]
    ])
    await cq.edit_message_reply_markup(reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"myacc_(.*)"))
@check_user
async def flex_btn(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")[1]
    user = cq.data.split("_").pop()
    result = await get_user_activity(int(query), user=int(user))
    pic, msg, btns = result
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"myfavs_(.*)"))
@check_user
async def list_favourites_btn(client, cq: CallbackQuery):
    await cq.answer()
    q = cq.data.split("_")
    btn = [[
        InlineKeyboardButton("ANIME", callback_data=f"myfavqry_ANIME_{q[1]}_1_{q[2]}_{q[3]}"),
        InlineKeyboardButton("CHARACTER", callback_data=f"myfavqry_CHAR_{q[1]}_1_{q[2]}_{q[3]}"),
        InlineKeyboardButton("MANGA", callback_data=f"myfavqry_MANGA_{q[1]}_1_{q[2]}_{q[3]}")
    ]]
    if q[2] == "yes":
        btn.append([InlineKeyboardButton("Back", callback_data=f"getusrbc_{q[3]}")])
    else:
        btn.append([InlineKeyboardButton("Profile", url=f"https://anilist.co/user/{q[1]}")])
    await cq.edit_message_media(
        InputMediaPhoto(f"https://img.anili.st/user/{q[1]}?a={time.time()}", caption="Choose one of the below options"),
        reply_markup=InlineKeyboardMarkup(btn)
    )


@Client.on_callback_query(filters.regex(pattern=r"myfavqry_(.*)"))
@check_user
async def favourites_btn(client, cq: CallbackQuery):
    await cq.answer()
    q = cq.data.split("_")
    pic, msg, btns = await get_user_favourites(q[2], int(q[5]), q[1], q[3], q[4])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"getusrbc_(.*)"))
@check_user
async def get_user_back_btn(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")[1]
    result = await get_user(None, "flex", user=int(query))
    pic, msg, btns = result
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"fav_(.*)"))
@check_user
async def toggle_favourites_btn(client, cq: CallbackQuery):
    query = cq.data.split("_")
    if query[1]=="ANIME" and len(query)>4:
        try:
            ANIME_DB[query[3]]
        except KeyError:
            return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
    if query[1]=="MANGA":
        try:
            MANGA_DB[query[3]]
        except KeyError:
            return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
    idm = int(query[2])
    user = int(cq.data.split("_").pop())
    rslt = await toggle_favourites(id_=idm, media=query[1], user=user)
    if rslt=="ok":
        await cq.answer("Updated")
    else:
        return
    result = (
        (await get_anime({"id": idm}, auth=True, user=user)) if query[1]=="ANIME" and len(query)==4
        else (await get_anilist(query[3], page = int(query[4]), auth=True, user=user)) if query[1]=="ANIME" and len(query)!=4
        else (await get_manga(query[3], page = int(query[4]), auth=True, user=user)) if query[1]=="MANGA"
        else (await get_airing({"id": idm}, auth=True, user=user)) if query[1]=="AIRING"
        else (await get_character({"search": query[3], "page": int(query[4])}, auth=True, user=user))
    )
    pic, msg = (
        (result[0], result[1]) if query[1]=="ANIME" and len(query)==4
        else (result[0]) if query[1]=="AIRING"
        else (result[0], result[1][0])
    )
    btns = get_btns(
        query[1],
        result=result,
        user=user,
        auth=True,
        lsqry=query[3] if len(query)!=4 else None,
        lspage=int(query[4]) if len(query)!=4 else None
    )
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"(lsadd|lsupdt)_(.*)"))
@check_user
async def list_update_anilist_btn(client, cq: CallbackQuery):
    stts_ls = ["COMPLETED", "CURRENT", "PLANNING", "DROPPED", "PAUSED", "REPEATING"]
    query = cq.data.split("_")
    btns = []
    row = []
    for i in stts_ls:
        row.append(
            InlineKeyboardButton(
                text=i,
                callback_data=cq.data.replace("lsadd", f"lsas_{i}") if query[0]=="lsadd" else cq.data.replace("lsupdt", f"lsus_{i}")
            )
        )
        if len(row)==3:
            btns.append(row)
            row = []
    if query[0]=="lsupdt":
        btns.append([InlineKeyboardButton("Delete", callback_data=cq.data.replace("lsupdt", f"dlt_{i}"))])
    await cq.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))


@Client.on_callback_query(filters.regex(pattern=r"(lsas|lsus|dlt)_(.*)"))
@check_user
async def update_anilist_btn(client, cq: CallbackQuery):
    query = cq.data.split("_")
    if query[2]=="ANIME":
        if len(query)==7:
            try:
                ANIME_DB[query[4]]
            except KeyError:
                return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
        if len(query)==8:
            try:
                ANIME_DB[query[5]]
            except KeyError:
                return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
    if query[2]=="MANGA":
        if len(query)==7:
            try:
                MANGA_DB[query[4]]
            except KeyError:
                return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
        if len(query)==8:
            try:
                MANGA_DB[query[5]]
            except KeyError:
                return await cq.answer("Query Expired!!!\nCreate new one", show_alert=True)
    idm = int(query[3])
    user = int(cq.data.split("_").pop())
    eid = None
    if query[0]!="lsas":
        eid = int(query[4])
    rslt = await update_anilist(id=idm, req=query[0], status=query[1], user=user, eid=eid)
    if rslt=="ok":
        await cq.answer("Updated")
    else:
        return
    result = (
        (await get_anime({"id": idm}, auth=True, user=user)) if query[2]=="ANIME" and (len(query)==5 or len(query)==6)
        else (await get_anilist(query[4], page = int(query[5]), auth=True, user=user)) if query[2]=="ANIME" and len(query)==7
        else (await get_anilist(query[5], page = int(query[6]), auth=True, user=user)) if query[2]=="ANIME" and len(query)==8
        else (await get_manga(query[4], page = int(query[5]), auth=True, user=user)) if query[2]=="MANGA" and len(query)==7
        else (await get_manga(query[5], page = int(query[6]), auth=True, user=user)) if query[2]=="MANGA" and len(query)==8
        else (await get_airing({"id": idm}, auth=True, user=user))
    )
    pic, msg = (
        (result[0], result[1]) if query[2]=="ANIME" and len(query)==5 or len(query)==6
        else (result[0]) if query[2]=="AIRING"
        else (result[0], result[1][0])
    )
    btns = get_btns(
        query[2],
        result=result,
        user=user,
        auth=True,
        lsqry=query[4] if len(query)==7 else query[5] if len(query)==8 else None,
        lspage=int(query[5]) if len(query)==7 else int(query[6]) if len(query)==8 else None
    )
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"(desc|ls|char)_(.*)"))
@check_user
async def additional_info_btn(client: Client, cq: CallbackQuery):
    await cq.answer()
    q = cq.data.split("_")
    kek, query, ctgry = q[0], q[1], q[2]
    info = (
        "<b>Description</b>"
        if kek == "desc"
        else "<b>Series List</b>"
        if kek == "ls"
        else "<b>Characters List</b>"
    )
    lsqry = f"_{q[3]}" if len(q) > 4 else ""
    lspg = f"_{q[4]}" if len(q) > 4 else ""
    pic, result = await get_additional_info(query, kek, ctgry)
    button = []
    spoiler = False
    bot = (await client.get_me()).username
    if "~!" in result and "!~" in result:
        result = re.sub(r"~!.*!~", "[Spoiler]", result)
        spoiler = True
        button.append([InlineKeyboardButton(text="View spoiler", url=f"https://t.me/{bot}/?start=des_{ctgry}_{query}")])
    if len(result) > 1000:
        result = result[:940] + "..."
        if spoiler==False:
            result += "\n\nFor more info click below given button"
            button.append([InlineKeyboardButton(text="More Info", url=f"https://t.me/{bot}/?start=des_{ctgry}_{query}")])
    msg = f"{info}:\n\n{result}"
    user = cq.data.split("_").pop()
    cbd = (
        f"btn_{query}_{q[3]}_{user}" if len(q) == 5
        else f"page_ANIME{lsqry}{lspg}_{q[5]}_{user}" if ctgry=="ANI"
        else f"page_CHARACTER{lsqry}{lspg}_{q[5]}_{user}"
    )
    button.append([InlineKeyboardButton(text="Back", callback_data=cbd)])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=InlineKeyboardMarkup(button))


@Client.on_callback_query(filters.regex(pattern=r"lsc_(.*)"))
@check_user
async def featured_in_btn(client, cq: CallbackQuery):
    kek, idm, qry, pg, auth, user = cq.data.split("_")
    result = await get_featured_in_lists(int(idm), "ANI")
    req = "lscm"
    if result[0]==False:
        result = await get_featured_in_lists(int(idm), "MAN")
        req = None
        if result[0]==False:
            await cq.answer("No Data Available!!!")
            return
    [msg, total], pic = result
    button = []
    totalpg, kek = divmod(total, 15)
    if kek!=0:
        totalpg + 1
    if total>15:
        button.append([InlineKeyboardButton(text="Next", callback_data=f"lsca_{idm}_1_{qry}_{pg}_{auth}_{user}")])
    if req!=None:
        button.append([InlineKeyboardButton(text="Manga", callback_data=f"lscm_{idm}_0_{qry}_{pg}_{auth}_{user}")])
    button.append([InlineKeyboardButton(text="Back", callback_data=f"page_CHARACTER_{qry}_{pg}_{auth}_{user}")])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=InlineKeyboardMarkup(button))


@Client.on_callback_query(filters.regex(pattern=r"lsc(a|m)_(.*)"))
@check_user
async def featured_in_switch_btn(client, cq: CallbackQuery):
    req, idm, reqpg, qry, pg, auth, user = cq.data.split("_")
    result = await get_featured_in_lists(int(idm), "MAN" if req=="lscm" else "ANI", page=int(reqpg))
    reqb = "lsca" if req=="lscm" else "lscm"
    bt = "Anime"  if req=="lscm" else "Manga"
    if result[0]==False:
        await cq.answer("No Data Available!!!")
        return
    [msg, total], pic = result
    totalpg, kek = divmod(total, 15)
    if kek!=0:
        totalpg + 1
    button = []
    if total>15:
        if int(reqpg)==0:
            button.append([InlineKeyboardButton(text="Next", callback_data=f"{req}_{idm}_{int(reqpg)+1}_{qry}_{pg}_{auth}_{user}")])
        elif int(reqpg)==totalpg:
            button.append([InlineKeyboardButton(text="Back", callback_data=f"{req}_{idm}_{int(reqpg)-1}_{qry}_{pg}_{auth}_{user}")])
        else:
            button.append(
                [
                    InlineKeyboardButton(text="Back", callback_data=f"{req}_{idm}_{int(reqpg)-1}_{qry}_{pg}_{auth}_{user}"),
                    InlineKeyboardButton(text="Next", callback_data=f"{req}_{idm}_{int(reqpg)+1}_{qry}_{pg}_{auth}_{user}")
                ]
            )
    button.append([InlineKeyboardButton(text=f"{bt}", callback_data=f"{reqb}_{idm}_0_{qry}_{pg}_{auth}_{user}")])
    button.append([InlineKeyboardButton(text="Back", callback_data=f"page_CHARACTER_{qry}_{pg}_{auth}_{user}")])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=InlineKeyboardMarkup(button))