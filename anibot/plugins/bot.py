import io
import sys
import traceback
import os
import re
import subprocess
import asyncio
import requests
import tracemoepy
from bson.objectid import ObjectId
from bs4 import BeautifulSoup as bs
from datetime import datetime
from natsort import natsorted
from pyrogram import filters, enums, Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from pyrogram.errors import (
    ChannelInvalid as ci,
    ChannelPrivate as cp,
    PeerIdInvalid as pi,
    FloodWait as fw
)
from .. import (
    BOT_NAME,
    TRIGGERS as trg,
    OWNER,
    HELP_DICT,
    anibot,
    DOWN_PATH,
    LOG_CHANNEL_ID
)
from ..utils.db import get_collection
from ..utils.helper import (
    AUTH_USERS,
    clog,
    check_user,
    control_user,
    get_btns,
    rand_key,
    return_json_senpai,
    runcmd,
    take_screen_shot,
    media_to_image,
    make_it_rw,
    IGNORE,
    USER_JSON,
    USER_WC
)
from ..utils.data_parser import (
    get_all_genres,
    get_all_tags,
    get_top_animes,
    get_user_activity,
    get_user_favourites,
    toggle_favourites,
    parse_filler,
    get_anime,
    get_airing,
    get_anilist,
    get_character,
    get_additional_info,
    get_manga,
    browse_,
    get_wo,
    get_wols,
    get_featured_in_lists,
    update_anilist,
    get_user,
    get_recommendations,
    get_scheduled,
    search_filler,
    ANIME_DB,
    AIR_QUERY,
    MANGA_DB,
    CHAR_DB,
    ANIME_QUERY,
    ACTIVITY_QUERY,
    ALLTOP_QUERY,
    ANILIST_MUTATION,
    ANILIST_MUTATION_DEL,
    ANILIST_MUTATION_UP,
    ANIME_MUTATION,
    BROWSE_QUERY,
    ANIME_TEMPLATE,
    CHA_INFO_QUERY,
    CHAR_MUTATION,
    CHARACTER_QUERY,
    DES_INFO_QUERY,
    DESC_INFO_QUERY,
    FAV_ANI_QUERY,
    GET_TAGS,
    FAV_CHAR_QUERY,
    FAV_MANGA_QUERY,
    GET_GENRES,
    ISADULT,
    LS_INFO_QUERY,
    MANGA_MUTATION,
    MANGA_QUERY,
    PAGE_QUERY,
    TOP_QUERY,
    REL_INFO_QUERY,
    TOPT_QUERY,
    USER_QRY,
    VIEWER_QRY,
    RECOMMENDTIONS_QUERY,
)
from .anilist import auth_link_cmd, code_cmd, logout_cmd

USERS = get_collection("USERS")
GROUPS = get_collection("GROUPS")
SFW_GROUPS = get_collection("SFW_GROUPS")
DC = get_collection('DISABLED_CMDS')
AG = get_collection('AIRING_GROUPS')
CR_GRPS = get_collection('CRUNCHY_GROUPS')
HD_GRPS = get_collection('HEADLINES_GROUPS')
MAL_HD_GRPS = get_collection('MAL_HEADLINES_GROUPS')
SP_GRPS = get_collection('SUBSPLEASE_GROUPS')
CC = get_collection('CONNECTED_CHANNELS')
CHAT_OWNER = ChatMemberStatus.OWNER
MEMBER = ChatMemberStatus.MEMBER
ADMINISTRATOR = ChatMemberStatus.ADMINISTRATOR

CMD = [
    'anime',
    'anilist',
    'character',
    'manga',
    'airing',
    'help',
    'schedule',
    'fillers',
    'top',
    'reverse',
    'watch',
    'start',
    'ping',
    'flex',
    'me',
    'activity',
    'user',
    'favourites',
    'gettags',
    'quote',
    'getgenres',
    'connect',
    'browse',
    'studio'
]


@anibot.on_message(
    ~filters.private & filters.command(
        ['disable', f'disable{BOT_NAME}', 'enable', f'enable{BOT_NAME}'],
        prefixes=trg
    )
)
@control_user
async def en_dis__able_cmd(client: Client, message: Message, mdata: dict):
    cmd = mdata['text'].split(" ", 1)
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = mdata['sender_chat']['id']
    if user in OWNER or (
        await anibot.get_chat_member(gid, user)
    ).status in [ADMINISTRATOR, CHAT_OWNER] or user==gid:
        if len(cmd)==1:
            x = await message.reply_text(
                'No command specified to be disabled!!!'
            )
            await asyncio.sleep(5)
            await x.delete()
            return
        enable = 'enable' in cmd[0]
        if set(cmd[1].split()).issubset(CMD):
            find_gc = await DC.find_one({'_id': gid})
            if find_gc is None:
                if enable:
                    x = await message.reply_text('Command already enabled!!!')
                    await asyncio.sleep(5)
                    await x.delete()
                    return
                await DC.insert_one({'_id': gid, 'cmd_list': cmd[1]})
                x = await message.reply_text("Command disabled!!!")
            else:
                ocls: str = find_gc['cmd_list']
                if set(cmd[1].split()).issubset(ocls.split()):
                    if enable:
                        if len(ocls.split())==1:
                            await DC.delete_one({'_id': gid})
                            x = await message.reply_text("Command enabled!!!")
                            await asyncio.sleep(5)
                            await x.delete()
                            return
                        ncls = ocls.split()
                        for i in cmd[1].split():
                            ncls.remove(i)
                        ncls = " ".join(ncls)
                    else:
                        x = await message.reply_text(
                            'Command already disabled!!!'
                        )
                        await asyncio.sleep(5)
                        await x.delete()
                        return
                elif enable:
                    x = await message.reply_text(
                        'Command already enabled!!!'
                    )
                    await asyncio.sleep(5)
                    await x.delete()
                    return
                else:
                    prencls = f'{ocls} {cmd[1]}'.replace('  ', ' ')
                    lsncls = []
                    for i in prencls.split():
                        if i not in lsncls:
                            lsncls.append(i)
                    ncls = " ".join(lsncls)
                await DC.update_one({'_id': gid}, {'$set': {'cmd_list': ncls}})
                x = await message.reply_text(f"Command {'en' if enable else 'dis'}abled!!!")
            await asyncio.sleep(5)
            await x.delete()
            return
        else:
            await message.reply_text("Hee, is that a command?!")


@anibot.on_message(
    ~filters.private & filters.command(
        ['disabled', f'disabled{BOT_NAME}'],
        prefixes=trg
    )
)
@control_user
async def list_disabled(client: Client, message: Message, mdata: dict):
    find_gc = await DC.find_one({'_id': mdata['chat']['id']})
    if find_gc is None:
        await message.reply_text("No commands disabled in this group!!!")
    else:
        lscmd = find_gc['cmd_list'].replace(" ", "\n")
        await message.reply_text(
f"""List of commands disabled in **{mdata['chat']['title']}**

{lscmd}"""
        )


@anibot.on_message(
    filters.user(OWNER) & filters.command(
        ['dbcleanup', f'dbcleanup{BOT_NAME}'], prefixes=trg
    )
)
@control_user
async def db_cleanup(client: Client, message: Message, mdata: dict):
    count = 0
    entries = ""
    st = datetime.now()
    x = await message.reply_text("Starting database cleanup in 5 seconds")
    et = datetime.now()
    pt = (et-st).microseconds / 1000
    await asyncio.sleep(5)
    await x.edit_text("Checking 1st collection!!!")
    async for i in GROUPS.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['_id'])
        except (cp, ci, pi):
            count += 1
            entries += str(await GROUPS.find_one(i))+'\n\n'
            await GROUPS.find_one_and_delete(i)
            await SFW_GROUPS.find_one_and_delete({'id': i['_id']})
            await DC.find_one_and_delete({'_id': i['_id']})
            await AG.find_one_and_delete({'_id': i['_id']})
            await HD_GRPS.find_one_and_delete({'_id': i['_id']})
            await SP_GRPS.find_one_and_delete({'_id': i['_id']})
            await CR_GRPS.find_one_and_delete({'_id': i['_id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)
    await x.edit_text("Checking 2nd collection!!!")
    async for i in AUTH_USERS.find():
        if i['id']=='pending':
            count += 1
            entries += str(await AUTH_USERS.find_one({'_id': i['_id']}))+'\n\n'
            await AUTH_USERS.find_one_and_delete({'_id': i['_id']})
    async for i in AUTH_USERS.find():
        await asyncio.sleep(2)
        try:
            await client.get_users(i['id'])
        except pi:
            count += 1
            entries += str(await AUTH_USERS.find_one({'id': i['id']}))+'\n\n'
            await AUTH_USERS.find_one_and_delete({'id': i['id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)

    nosgrps = await GROUPS.estimated_document_count()
    nossgrps = await SFW_GROUPS.estimated_document_count()
    nosauus = await AUTH_USERS.estimated_document_count()
    if count == 0:
        msg = f"""Database seems to be accurate, no changes to be made!!!

**Groups:** `{nosgrps}`
**SFW Groups:** `{nossgrps}`
**Authorised Users:** `{nosauus}`
**Ping:** `{pt}`
"""
    else:
        msg = f"""{count} entries removed from database!!!

**New Data:**
    __Groups:__ `{nosgrps}`
    __SFW Groups:__ `{nossgrps}`
    __Authorised Users:__ `{nosauus}`

**Ping:** `{pt}`
"""
        if len(entries)>4095:
            with open('entries.txt', "w+") as file:
                file.write(entries)
            return await x.reply_document('entries.txt')
        await x.reply_text(entries)
    await x.edit_text(msg)


@anibot.on_message(
    filters.command(['start', f'start{BOT_NAME}'], prefixes=trg)
)
@control_user
async def start_(client: Client, message: Message, mdata: dict):
    gid = mdata['chat']['id']
    try:
        user = mdata['from_user']['id']
    except KeyError:
        user = 00000000
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'start' in find_gc['cmd_list'].split():
        return
    bot = await client.get_me()
    if gid==user:
        if user not in OWNER and not (await USERS.find_one({"id": user})):
                        try:
                            usertitle = mdata['from_user']['username']
                        except KeyError:
                            usertitle = mdata['from_user']['first_name']
                        await USERS.insert_one({"id": user, "user": usertitle})
                        await clog(
                            "ANIBOT",
            f"""New User started bot

<a url="tg://user?id={user}">{usertitle}</a>
ID: `{user}`""",
                            "NEW_USER"
                        )
        if len(mdata['text'].split())!=1:
            deep_cmd = mdata['text'].split()[1]
            if deep_cmd=="help":
                await help_(client, message)
                return
            if deep_cmd=="auth":
                await auth_link_cmd(client, message)
                return
            if deep_cmd=="logout":
                await logout_cmd(client, message)
                return
            deep_cmd_list = deep_cmd.split("_")
            if deep_cmd_list[0]=="des":
                try:
                    req = deep_cmd_list[3]
                except IndexError:
                    req = "desc"
                pic, result = await get_additional_info(
                    deep_cmd_list[2],
                    deep_cmd_list[1],
                    req
                )
                await client.send_photo(user, pic)
                try:
                    await client.send_message(
                        user,
                        result.replace("~!", "").replace("!~", "")
                    )
                except (TypeError, AttributeError):
                    await client.send_message(
                        user,
                        "No description available!!!"
                    )
                return
            if deep_cmd_list[0]=="anime":
                auth = bool((await AUTH_USERS.find_one({"id": user})))
                result = await get_anime(
                    {"id": int(deep_cmd_list[1])},
                    user=user,
                    auth=auth
                )
                pic, msg = result[0], result[1]
                buttons = get_btns(
                    "ANIME",
                    result=result,
                    user=user,
                    auth=auth
                )
                await client.send_photo(
                    user,
                    pic,
                    caption=msg,
                    reply_markup=buttons
                )
                return
            if deep_cmd_list[0]=="anirec":
                result = await get_recommendations(deep_cmd_list[1])
                await client.send_message(
                    user, result, disable_web_page_preview=True
                )
                return
            if deep_cmd.split("_", 1)[0]=="code":
                if not os.environ.get('ANILIST_REDIRECT_URL'):
                    return
                qry = deep_cmd.split("_", 1)[1]
                k = await AUTH_USERS.find_one({'_id': ObjectId(qry)})
                await code_cmd(k['code'], message)
                return
        await client.send_message(
            gid,
            text=(
                (
                    (
                        (
                            (
                                f"Kon'nichiwa!!!\n"
                                + f"I'm {bot.first_name} bot and I can help you get info on "
                                + "Animes, Mangas, Characters, Airings, Schedules, Watch "
                            )
                            + "Orders of Animes, etc."
                        )
                        + f"\n\nFor more info send /help in here."
                    )
                    + "If you wish to use me in a group start me by "
                )
                + f"/start{BOT_NAME} command after adding me in the group."
            ),
        )

    else:
        if not await (GROUPS.find_one({"_id": gid})):
            try:
                gidtitle = mdata['chat']['username']
            except KeyError:
                gidtitle = mdata['chat']['title']
            await GROUPS.insert_one({"_id": gid, "grp": gidtitle})
            await clog(
                "ANIBOT",
                f"Bot added to a new group\n\n{gidtitle}\nID: `{gid}`",
                "NEW_GROUP"
            )
        await client.send_message(gid, text="Bot seems online!!!")


@anibot.on_message(
    filters.command(['help', f'help{BOT_NAME}'], prefixes=trg)
)
@control_user
async def help_(client: Client, message: Message, mdata: dict):
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'help' in find_gc['cmd_list'].split():
        return
    bot_us = (await client.get_me()).username
    try:
        id_ = mdata['from_user']['id']
    except KeyError:
        await client.send_message(
            gid,
            text="Click below button for bot help",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help", url=f"https://t.me/{bot_us}/?start=help")]])
        )
        return
    buttons = help_btns(id_)
    text='''This is a small guide on how to use me
    
**Basic Commands:**
Use /ping or !ping cmd to check if bot is online
Use /start or !start cmd to start bot in group or pm
Use /help or !help cmd to get interactive help on available bot cmds
Use /feedback cmd to contact bot owner'''
    if id_ in OWNER:
        await client.send_message(gid, text=text, reply_markup=buttons)
        await client.send_message(
            gid,
            text="""Owners / Sudos can also use

- __/term__ `to run a cmd in terminal`
- __/eval__ `to run a python code like `__/eval print('UwU')__` `
- __/stats__ `to get stats on bot like no. of users, grps and authorised users`
- __/dbcleanup__ `to remove obsolete/useless entries in database`

Apart from above shown cmds"""
        )
    elif gid==id_:
        await client.send_message(gid, text=text, reply_markup=buttons)
    else:
        await client.send_message(
            gid,
            text="Click below button for bot help",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "Help",
                        url=f"https://t.me/{bot_us}/?start=help"
                    )
                ]]
            )
        )


@anibot.on_message(
    filters.command(
        [
            'connect',
            f'connect{BOT_NAME}',
            'disconnect',
            f'disconnect{BOT_NAME}'
        ],
        prefixes=trg
    )
)
@control_user
async def connect_(client: Client, message: Message, mdata: dict):
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'connect' in find_gc['cmd_list'].split():
        return
    bot_us = (await client.get_me()).username
    try:
        id_ = mdata['from_user']['id']
    except KeyError:
        await client.send_message(
            gid,
            text="Go to bot pm to connect channel",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "Bot PM", url=f"https://t.me/{bot_us}"
                    )
                ]]
            )
        )
        return
    if gid==id_:
        data = (mdata['text'].split())
        try:
            channel = data[1]
        except:
            return await client.send_message(
                gid,
                text=(
                    "Please provide the channel id you wish to connect!!!"
                    +"\nExample: /connect -100xxxxxxxxx"
                )
            )
        if "-100" not in channel:
            return await client.send_message(
                gid, text="Please enter the full channel ID!!!"
            )
        if  data[0]=='connect':
            if (await CC.find_one({"_id": str(channel)})):
                await client.send_message(
                    gid,
                    text=(
                        "Channel already connected"
                        +"\nIf someone else has access to it who doesn't own "
                        +"the channel, contact @hanabi_support"
                    )
                )
                return
            await CC.insert_one({"_id": str(channel), "usr": id_})
            await client.send_message(
                gid, text="Successfully connected the channel"
            )
        else:
            k = await CC.find_one({"_id": str(channel)})
            if k and k['usr']==id_:
                await CC.find_one_and_delete({"_id": str(channel)})
                await client.send_message(
                    gid, text="Successfully disconnected the channel"
                )
            else:
                await client.send_message(gid, text="Channel not connected")
    else:
        k = (await client.get_chat_member(gid, id_)).status
        if k == CHAT_OWNER:
            if 'connect' in mdata['text']:
                await CC.insert_one({"_id": str(message.chat.id), "usr": id_})
                await client.send_message(
                    gid, text="Successfully connected the channel"
                )
            else:
                await CC.find_one_and_delete({"_id": str(message.chat.id)})
                await client.send_message(
                    gid, text="Successfully disconnected the channel"
                )
            return
        await client.send_message(
            gid,
            text="Click below button for bot help",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "Bot PM", url=f"https://t.me/{bot_us}"
                    )
                ]]
            )
        )


@anibot.on_callback_query(filters.regex(pattern=r"help_(.*)"))
@check_user
async def help_dicc_parser(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    kek, qry, user = cdata['data'].split("_")
    text = HELP_DICT[qry]
    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back", callback_data=f"hlplist_{user}")]]
    )
    await cq.edit_message_text(text=text, reply_markup=btn)


@anibot.on_callback_query(filters.regex(pattern=r"hlplist_(.*)"))
@check_user
async def help_list_parser(client: Client, cq: CallbackQuery, cdata: dict):
    await cq.answer()
    user = cdata['data'].split("_")[1]
    buttons = help_btns(user)
    text='''This is a small guide on how to use me
    
**Basic Commands:**
Use /ping or !ping cmd to check if bot is online
Use /start or !start cmd to start bot in group or pm
Use /help or !help cmd to get interactive help on available bot cmds
Use /feedback cmd to contact bot owner'''
    await cq.edit_message_text(text=text, reply_markup=buttons)


def help_btns(user):
    but_rc = []
    buttons = []
    hd_ = list(natsorted(HELP_DICT.keys()))
    for i in hd_:
        but_rc.append(
            InlineKeyboardButton(i, callback_data=f"help_{i}_{user}")
        )
        if len(but_rc)==2:
            buttons.append(but_rc)
            but_rc = []
    if len(but_rc)!=0:
        buttons.append(but_rc)
    return InlineKeyboardMarkup(buttons)


@anibot.on_message(
    filters.user(OWNER) & filters.command(
        ['stats', f'stats{BOT_NAME}'],
        prefixes=trg
    )
)
@control_user
async def stats_(client: Client, message: Message, mdata: dict):
    st = datetime.now()
    x = await message.reply_text("Collecting Stats!!!")
    et = datetime.now()
    pt = (et-st).microseconds / 1000
    nosus = await USERS.estimated_document_count()
    nosauus = await AUTH_USERS.estimated_document_count()
    nosgrps = await GROUPS.estimated_document_count()
    nossgrps = await SFW_GROUPS.estimated_document_count()
    noshdgrps = await HD_GRPS.estimated_document_count()
    nosmhdgrps = await MAL_HD_GRPS.estimated_document_count()
    s = await SP_GRPS.estimated_document_count()
    a = await AG.estimated_document_count()
    c = await CR_GRPS.estimated_document_count()
    kk = requests.get("https://api.github.com/repos/lostb053/anibot").json()
    await x.edit_text(f"""
Stats:-

**Users:** {nosus}
**Authorised Users:** {nosauus}
**Groups:** {nosgrps}
**Airing Groups:** {a}
**Crunchyroll Groups:** {c}
**Subsplease Groups:** {s}
**LC Headline Groups:** {noshdgrps}
**MAL Headline Groups:** {nosmhdgrps}
**SFW Groups:** {nossgrps}
**Stargazers:** {kk.get("stargazers_count")}
**Forks:** {kk.get("forks")}
**Ping:** `{pt} ms`
"""
    )


@anibot.on_message(filters.command(['ping', f'ping{BOT_NAME}'], prefixes=trg))
@control_user
async def pong_(client: Client, message: Message, mdata: dict):
    find_gc = await DC.find_one({'_id': mdata['chat']['id']})
    if find_gc is not None and 'ping' in find_gc['cmd_list'].split():
        return
    st = datetime.now()
    x = await message.reply_text("Ping...")
    et = datetime.now()
    pt = (et-st).microseconds / 1000
    await x.edit_text(f"__Pong!!!__\n`{pt} ms`")


@anibot.on_message(
    filters.private & filters.command(
        ['feedback', f'feedback{BOT_NAME}'], prefixes=trg
    )
)
@control_user
async def feed_(client: Client, message: Message, mdata: dict):
    owner = (await client.get_users(OWNER[0])).username
    await client.send_message(
        mdata['chat']['id'],
        f"For issues or queries please contact @{owner} or join @hanabi_support",
    )

###### credits to @NotThatMF on tg since he gave me the code for it ######


@anibot.on_message(
    filters.command(
        ['eval', f'eval{BOT_NAME}'], prefixes=trg
    ) & filters.user(OWNER)
)
@control_user
async def eval_(client: Client, message: Message, mdata: dict):
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(" ", maxsplit=1)[1]
    reply_to_ = message.reply_to_message or message
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = "<b>EVAL</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>OUTPUT</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[:1000],
                disable_notification=True
            )
    else:
        await reply_to_.reply_text(final_output)
    await status_message.delete()


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@anibot.on_message(
    filters.user(OWNER) & filters.command(
        ["term", f"term{BOT_NAME}"], prefixes=trg
    )
)
@control_user
async def terminal(client: Client, message: Message, mdata: dict):
    if len(message.text.split()) == 1:
        await message.reply_text("Usage: `/term echo owo`")
        return
    args = message.text.split(None, 1)
    teks = args[1]
    if "\n" in teks:
        code = teks.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            except Exception as err:
                print(err)
                await message.reply_text(
                    """
**Error:**
```{}```
""".format(
                        err
                    ),
                    parse_mode=enums.ParseMode.MARKDOWN,
                )
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", teks)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type, value=exc_obj, tb=exc_tb
            )
            await message.reply_text(
                f"""**Error:**\n```{"".join(errors)}```""",
                parse_mode=enums.ParseMode.MARKDOWN,
            )

            return
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            filename = "output.txt"
            with open(filename, "w+") as file:
                file.write(output)
            await client.send_document(
                message.chat.id,
                filename,
                reply_to_message_id=message.id,
                caption="`Output file`",
            )
            os.remove(filename)
            return
        await message.reply_text(
            f"**Output:**\n```{output}```",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("**Output:**\n`No Output`")


##########################################################################

@anibot.on_edited_message(
    ~filters.private & filters.command(
        ['disable', f'disable{BOT_NAME}', 'enable', f'enable{BOT_NAME}'],
        prefixes=trg
    )
)
@control_user
async def en_dis__able_cmd_edit(client: Client, message: Message, mdata: dict):
    await en_dis__able_cmd(client, message)


@anibot.on_edited_message(
    ~filters.private & filters.command(
        ['disabled', f'disabled{BOT_NAME}'],
        prefixes=trg
    )
)
@control_user
async def list_disabled_edit(client: Client, message: Message, mdata: dict):
    await list_disabled(client, message)

@anibot.on_edited_message(
    filters.user(OWNER) & filters.command(
        ['dbcleanup', f'dbcleanup{BOT_NAME}'], prefixes=trg
    )
)
@control_user
async def db_cleanup_edit(client: Client, message: Message, mdata: dict):
    await db_cleanup(client, message)

@anibot.on_edited_message(
    filters.command(['start', f'start{BOT_NAME}'], prefixes=trg)
)
@control_user
async def start_edit(client: Client, message: Message, mdata: dict):
    await start_(client, message)

@anibot.on_edited_message(
    filters.command(['help', f'help{BOT_NAME}'], prefixes=trg)
)
@control_user
async def help_edit(client: Client, message: Message, mdata: dict):
    await help_(client, message)

@anibot.on_edited_message(
    filters.command(
        [
            'connect',
            f'connect{BOT_NAME}',
            'disconnect',
            f'disconnect{BOT_NAME}'
        ],
        prefixes=trg
    )
)
@control_user
async def connect_edit(client: Client, message: Message, mdata: dict):
    await connect_(client, message)

@anibot.on_edited_message(
    filters.user(OWNER) & filters.command(
        ['stats', f'stats{BOT_NAME}'], prefixes=trg
    )
)
@control_user
async def stats_edit(client: Client, message: Message, mdata: dict):
    await stats_(client, message)

@anibot.on_edited_message(
    filters.command(['ping', f'ping{BOT_NAME}'], prefixes=trg)
)
@control_user
async def pong_edit(client: Client, message: Message, mdata: dict):
    await pong_(client, message)

@anibot.on_edited_message(
    filters.private & filters.command(
        ['feedback', f'feedback{BOT_NAME}'], prefixes=trg
    )
)
@control_user
async def feed_edit(client: Client, message: Message, mdata: dict):
    await feed_(client, message)

@anibot.on_edited_message(
    filters.command(
        ['eval', f'eval{BOT_NAME}'], prefixes=trg
    ) & filters.user(OWNER)
)
@control_user
async def eval_edit(client: Client, message: Message, mdata: dict):
    await eval_(client, message)

@anibot.on_edited_message(
    filters.user(OWNER) & filters.command(
        ["term", f"term{BOT_NAME}"], prefixes=trg
    )
)
@control_user
async def terminal_edit(client: Client, message: Message, mdata: dict):
    await terminal(client, message)