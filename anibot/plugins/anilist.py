# base code was taken from @DeletedUser420's Userge-Plugins repo
# originally authored by Phyco-Ninja (https://github.com/Phyco-Ninja) (@PhycoNinja13b)
# I've just tweaked his file a bit (maybe a lot)
# But i sticked to the format he used which looked cool

""" Search for Anime related Info using Anilist API """


import asyncio, requests, os
from re import A
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message
from .. import ANILIST_CLIENT, ANILIST_REDIRECT_URL, ANILIST_SECRET, HELP_DICT, TRIGGERS as trg, BOT_NAME
from ..utils.data_parser import get_us_act, get_us_fav, tog_fav_, get_ani, get_airing, get_anilist, get_char, get_info, get_manga, get_ls, ls_au_status, get_usr, ANIME_DB, MANGA_DB
from ..utils.helper import check_user, get_btns, AUTH_USERS, rand_key


@Client.on_message(filters.command(["anime", f"anime{BOT_NAME}"], prefixes=trg))
async def anim_arch(client, message: Message):
    """Search Anime Info"""
    text = message.text.split(" ", 1)
    if len(text)==1:
        k = await message.reply_text("NameError: 'query' not defined")
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
    result = await get_ani(vars_, user=user, auth=auth)
    if len(result) != 1:
        title_img, finals_ = result[0], result[1]
    else:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    buttons = get_btns("ANIME", result=result, user=user, auth=auth)
    await message.reply_photo(title_img, caption=finals_, reply_markup=buttons)


@Client.on_message(filters.command(["manga", f"manga{BOT_NAME}"], prefixes=trg))
async def manga_arch(client, message: Message):
    """Search Manga Info"""
    text = message.text.split(" ", 1)
    if len(text)==1:
        k = await message.reply_text("NameError: 'query' not defined")
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
    await message.reply_photo(pic, caption=finals_, reply_markup=buttons)


@Client.on_message(filters.command(["character", f"character{BOT_NAME}"], prefixes=trg))
async def character_search(client, message: Message):
    """Get Info about a Character"""
    text = message.text.split(" ", 1)
    if len(text)==1:
        k = await message.reply_text("NameError: 'query' not defined")
        await asyncio.sleep(5)
        return await k.delete()
    query = text[1]
    var = {"search": query}
    auth = False
    user = message.from_user.id
    if (await AUTH_USERS.find_one({"id": user})):
        auth = True
    result = await get_char(var, auth=auth, user=user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    img = result[0]
    cap_text = result[1][0]
    buttons = get_btns("CHARACTER", user=user, lsqry=query, lspage=1, result=result, auth=auth)
    await message.reply_photo(img, caption=cap_text, reply_markup=buttons)


@Client.on_message(filters.command(["anilist", f"anilist{BOT_NAME}"], prefixes=trg))
async def ianime(client, message: Message):
    text = message.text.split(" ", 1)
    if len(text)==1:
        k = await message.reply_text("NameError: 'query' not defined")
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
    await message.reply_photo(pic, caption=msg, reply_markup=buttons)


@Client.on_message(filters.command(["flex", f"flex{BOT_NAME}", "me", f"me{BOT_NAME}", "user", f"user{BOT_NAME}"], prefixes=trg))
async def flex_(client, message: Message):
    query = message.text.split(" ", 1)
    get_user = None
    if "user" in query[0]:
        if not len(query)==2:
            k = await message.reply_text("NameError: 'query' not defined")
            await asyncio.sleep(5)
            return await k.delete()
        else:
            get_user = {"search": query[1]}
    user = message.from_user.id
    if not "user" in query[0] and not (await AUTH_USERS.find_one({"id": user})):
        return await message.reply_text("Please connect your account first to use this cmd")
    result = await get_usr(get_user, query[0], user)
    if len(result) == 1:
        k = await message.reply_text(result[0])
        await asyncio.sleep(5)
        return await k.delete()
    pic, msg, buttons = result
    await message.reply_photo(pic, caption=msg, reply_markup=buttons)


@Client.on_message(filters.command(["airing", f"airing{BOT_NAME}"], prefixes=trg))
async def airing_anim(client, message: Message):
    """Get Airing Detail of Anime"""
    text = message.text.split(" ", 1)
    if len(text)==1:
        k = await message.reply_text("NameError: 'query' not defined")
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
    await message.reply_photo(coverImg, caption=out, reply_markup=btn)


@Client.on_message(filters.private & filters.command("auth", prefixes=trg))
async def auth_link(client, message: Message):
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


@Client.on_message(filters.private & filters.command("code", prefixes=trg))
async def code_to_accTok(client, message: Message):
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


@Client.on_message(filters.private & filters.command("logout", prefixes=trg))
async def logout_(client, message: Message):
    if (await AUTH_USERS.find_one({"id": message.from_user.id})):
        asyncio.gather(AUTH_USERS.find_one_and_delete({"id": message.from_user.id}))
        await message.reply_text("Logged out!!!")
    else:
        await message.reply_text("You are not authorized to begin with!!!")


@Client.on_callback_query(filters.regex(pattern=r"page_(.*)"))
@check_user
async def present_ls(client, cq: CallbackQuery):
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
        else (await get_char(get_pg, auth=authbool, user=int(user)))
        if media == "CHARACTER"
        else (await get_manga(query, int(page), auth=authbool, user=int(user)))
    )
    pic, msg = result[0], result[1][0]
    button = get_btns(media, lsqry=query, lspage=int(page), result=result, user=user, auth=authbool)
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=button)


@Client.on_callback_query(filters.regex(pattern=r"btn_(.*)"))
@check_user
async def present_res(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")
    idm = query[1]
    user = int(cq.data.split("_").pop())
    authbool = bool(1) if query[2]=="True" else bool(0)
    vars_ = {"id": int(idm)}
    result = await get_ani(vars_, auth=authbool, user=user)
    pic, msg = result[0], result[1]
    btns = get_btns("ANIME", result=result, user=user, auth=authbool)
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"myacc_(.*)"))
@check_user
async def myacc_(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")[1]
    user = cq.data.split("_").pop()
    result = await get_us_act(int(query), user=int(user))
    pic, msg, btns = result
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"myfavs_(.*)"))
@check_user
async def myfavs_(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")[1]
    user = cq.data.split("_").pop()
    result = await get_us_fav(int(query), user=int(user))
    pic, msg, btns = result
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"getusrbc_(.*)"))
@check_user
async def getusrbc(client, cq: CallbackQuery):
    await cq.answer()
    query = cq.data.split("_")[1]
    result = await get_usr(None, "flex", user=query)
    pic, msg, btns = result
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"fav_(.*)"))
@check_user
async def fav_(client, cq: CallbackQuery):
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
    rslt = await tog_fav_(id_=idm, media=query[1], user=user)
    if rslt=="ok":
        await cq.answer("Updated")
    else:
        return
    result = (
        (await get_ani({"id": idm}, auth=True, user=user)) if query[1]=="ANIME" and len(query)==4
        else (await get_anilist(query[3], page = int(query[4]), auth=True, user=user)) if query[1]=="ANIME" and len(query)!=4
        else (await get_manga(query[3], page = int(query[4]), auth=True, user=user)) if query[1]=="MANGA"
        else (await get_airing({"id": idm}, auth=True, user=user)) if query[1]=="AIRING"
        else (await get_char({"search": query[3], "page": int(query[4])}, auth=True, user=user))
    )
    pic, msg = (
        (result[0], result[1]) if query[1]=="ANIME" and len(query)==4
        else (result[0]) if query[1]=="AIRING"
        else (result[0], result[1][0])
    )
    btns = get_btns(query[1], result=result, user=user, auth=True, lsqry=query[3] if len(query)!=4 else None, lspage=int(query[4]) if len(query)!=4 else None)
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=btns)


@Client.on_callback_query(filters.regex(pattern=r"(lsadd|lsupdt)_(.*)"))
@check_user
async def ls_add_(client, cq: CallbackQuery):
    stts_ls = ["COMPLETED", "CURRENT", "PLANNING", "DROPPED", "PAUSED", "REPEATING"]
    query = cq.data.split("_")
    btns = []
    row = []
    for i in stts_ls:
        row.append(InlineKeyboardButton(text=i, callback_data=cq.data.replace("lsadd", f"lsas_{i}") if query[0]=="lsadd" else cq.data.replace("lsupdt", f"lsus_{i}")))
        if len(row)==3:
            btns.append(row)
            row = []
    if query[0]=="lsupdt":
        btns.append([InlineKeyboardButton("Delete", callback_data=cq.data.replace("lsupdt", f"dlt_{i}"))])
    await cq.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btns))


@Client.on_callback_query(filters.regex(pattern=r"(lsas|lsus|dlt)_(.*)"))
@check_user
async def lsas_(client, cq: CallbackQuery):
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
    rslt = await ls_au_status(id=idm, req=query[0], status=query[1], user=user, eid=eid)
    if rslt=="ok":
        await cq.answer("Updated")
    else:
        return
    result = (
        (await get_ani({"id": idm}, auth=True, user=user)) if query[2]=="ANIME" and (len(query)==5 or len(query)==6)
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
async def dcl_(client, cq: CallbackQuery):
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
    pic, result = await get_info(query, kek, ctgry)
    if len(result) > 1000:
        result = result[:940] + "..."
        result += "\n\nFor more info click back button and open synopsis link"
    msg = f"{info}:\n\n{result}"
    user = cq.data.split("_").pop()
    cbd = (
        f"btn_{query}_{q[3]}_{user}" if len(q) == 5
        else f"page_ANIME{lsqry}{lspg}_{q[5]}_{user}" if ctgry=="ANI"
        else f"page_CHARACTER{lsqry}{lspg}_{q[5]}_{user}"
    )
    button = InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data=cbd)]])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=button)


@Client.on_callback_query(filters.regex(pattern=r"lsc_(.*)"))
@check_user
async def lsc_(client, cq: CallbackQuery):
    kek, idm, qry, pg, auth, user = cq.data.split("_")
    result = await get_ls(int(idm), "ANI")
    req = "lscm"
    if result[0]==False:
        result = await get_ls(int(idm), "MAN")
        req = None
        if result[0]==False:
            await cq.answer("No Data Available!!!")
            return
    msg, pic = result
    button = []
    if req!=None:
        button.append([InlineKeyboardButton(text="Manga", callback_data=f"lscm_{idm}_{qry}_{pg}_{auth}_{user}")])
    button.append([InlineKeyboardButton(text="Back", callback_data=f"page_CHARACTER_{qry}_{pg}_{auth}_{user}")])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=InlineKeyboardMarkup(button))


@Client.on_callback_query(filters.regex(pattern=r"lsc(a|m)_(.*)"))
@check_user
async def lscam_(client, cq: CallbackQuery):
    req, idm, qry, pg, auth, user = cq.data.split("_")
    result = await get_ls(int(idm), "MAN" if req=="lscm" else "ANI")
    reqb = "lsca" if req=="lscm" else "lscm"
    bt = "Anime"  if req=="lscm" else "Manga"
    if result[0]==False:
        await cq.answer("No Data Available!!!")
        return
    msg, pic = result
    button = []
    button.append([InlineKeyboardButton(text=f"{bt}", callback_data=f"{reqb}_{idm}_{qry}_{pg}_{auth}_{user}")])
    button.append([InlineKeyboardButton(text="Back", callback_data=f"page_CHARACTER_{qry}_{pg}_{auth}_{user}")])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=InlineKeyboardMarkup(button))


HELP_DICT["anime"] = """Use /anime cmd to get info on specific anime using
keywords (anime name) or Anilist ID
(Don't confuse with anilist)

This cmd includes buttons for prequel and sequel related to anime searched (if any),
while anilist can scroll between animes with similar names

**Usage:**
        `/anime Fumetsu No Anata E`
        `!anime Higehiro`
        `/anime 98385`"""

HELP_DICT["anilist"] = """Use /anilist cmd to get info on all animes related to search query
(Don't confuse with anime)

This cmd helps you choose between animes with similar names,
while anime gives info on single anime

**Usage:**
        `/anilist rezero`
        `!anilist hello world`"""

HELP_DICT["character"] = """Use /character cmd to get info on characters

**Usage:**
        `/character Hanabi`
        `!character tachibana`"""

HELP_DICT["manga"] = """Use /manga cmd to get info on mangas

**Usage:**
        `/manga Karakai Jouzu no Takagi San`
        `!manga Ao Haru Ride`"""

HELP_DICT["airing"] = """Use /airing cmd to get info on airing status of anime

**Usage:**
        `/airing Nagatoro`
        `!airing Seijo no Maryoku wa Bannou desu`"""

HELP_DICT["auth"] = "Use /auth or !auth cmd to authorize your Anilist account with bot"

HELP_DICT["flex"] = "Use /flex or !flex cmd to get your anilist stats\nCan also use /me or !me"

HELP_DICT["logout"] = "Use /logout or !logout cmd to revoke authorization"

HELP_DICT["user"] = """Use /user cmd to get info on a user

**Usage:**
        `/user lostb053`
        `!user lostb053`"""