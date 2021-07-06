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
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ChannelInvalid as ci, ChannelPrivate as cp, PeerIdInvalid as pi, FloodWait as fw
from .. import BOT_NAME, TRIGGERS as trg, OWNER, HELP_DICT, anibot, DOWN_PATH, LOG_CHANNEL_ID
from ..utils.db import get_collection
from ..utils.helper import (
    AUTH_USERS, clog, check_user, control_user, rand_key, return_json_senpai,
    runcmd, take_screen_shot, IGNORE, media_to_image, make_it_rw,
    USER_JSON, USER_WC
)
from ..utils.data_parser import (
    get_all_genres, get_all_tags, get_top_animes, get_user_activity, get_user_favourites, toggle_favourites, parse_filler,
    get_anime, get_airing, get_anilist, get_character, get_additional_info, get_manga, browse_, get_wo, get_wols, AIR_QUERY,
    get_featured_in_lists, update_anilist, get_user, ANIME_DB, MANGA_DB, CHAR_DB, get_scheduled, search_filler, ANIME_QUERY,
    ACTIVITY_QUERY, ALLTOP_QUERY, ANILIST_MUTATION, ANILIST_MUTATION_DEL, ANILIST_MUTATION_UP, ANIME_MUTATION, BROWSE_QUERY,
    ANIME_TEMPLATE, CHA_INFO_QUERY, CHAR_MUTATION, CHARACTER_QUERY, DES_INFO_QUERY, DESC_INFO_QUERY, FAV_ANI_QUERY, GET_TAGS,
    FAV_CHAR_QUERY, FAV_MANGA_QUERY, GET_GENRES, ISADULT, LS_INFO_QUERY, MANGA_MUTATION, MANGA_QUERY, PAGE_QUERY, TOP_QUERY,
    REL_INFO_QUERY, TOPT_QUERY, USER_QRY, VIEWER_QRY
)
from .anilist import auth_link_cmd, code_cmd

USERS = get_collection("USERS")
GROUPS = get_collection("GROUPS")
SFW_GROUPS = get_collection("SFW_GROUPS")
DC = get_collection('DISABLED_CMDS')
AG = get_collection('AIRING_GROUPS')
CR_GRPS = get_collection('CRUNCHY_GROUPS')
SP_GRPS = get_collection('SUBSPLEASE_GROUPS')
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
    'getgenres'
]


@Client.on_message(~filters.private & filters.command(['disable', f'disable{BOT_NAME}', 'enable', f'enable{BOT_NAME}']))
@control_user
async def en_dis__able_cmd(client: Client, message: Message):
    cmd = message.text.split(" ", 1)
    gid = message.chat.id
    user = message.from_user.id
    if user in OWNER or (await anibot.get_chat_member(gid, user)).status!='member':
        if len(cmd)==1:
            x = await message.reply_text('No command specified to be disabled!!!')
            await asyncio.sleep(5)
            await x.delete()
            return
        enable = False if not 'enable' in cmd[0] else True
        if set(cmd[1].split()).issubset(CMD):
            find_gc = await DC.find_one({'_id': gid})
            if find_gc==None:
                if enable:
                    x = await message.reply_text('Command already enabled!!!')
                    await asyncio.sleep(5)
                    await x.delete()
                    return
                await DC.insert_one({'_id': gid, 'cmd_list': cmd[1]})
                x = await message.reply_text("Command disabled!!!")
                await asyncio.sleep(5)
                await x.delete()
                return
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
                        x = await message.reply_text('Command already disabled!!!')
                        await asyncio.sleep(5)
                        await x.delete()
                        return
                else:
                    if enable:
                        x = await message.reply_text('Command already enabled!!!')
                        await asyncio.sleep(5)
                        await x.delete()
                        return
                    else:
                        lsncls = []
                        prencls = (ocls+' '+cmd[1]).replace('  ', ' ')
                        for i in prencls.split():
                            if i not in lsncls:
                                lsncls.append(i)
                        ncls = " ".join(lsncls)
                await DC.update_one({'_id': gid}, {'$set': {'cmd_list': ncls}})
                x = await message.reply_text(f"Command {'dis' if enable==False else 'en'}abled!!!")
                await asyncio.sleep(5)
                await x.delete()
                return
        else:
            await message.reply_text("Hee, is that a command?!")


@Client.on_message(~filters.private & filters.command(['disabled', f'disabled{BOT_NAME}']))
@control_user
async def list_disabled(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc==None:
        await message.reply_text("No commands disabled in this group!!!")
    else:
        lscmd = find_gc['cmd_list'].replace(" ", "\n")
        await message.reply_text(f"List of commands disabled in **{message.chat.title}**\n\n{lscmd}")


@Client.on_message(filters.user(OWNER) & filters.command(['dbcleanup', f'dbcleanup{BOT_NAME}'], prefixes=trg))
@control_user
async def db_cleanup(client: Client, message: Message):
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
            await client.get_chat(i['id'])
        except cp:
            count += 1
            entries += str(await GROUPS.find_one({'id': i['id']}))+'\n\n'
            await GROUPS.find_one_and_delete({'id': i['id']})
        except ci:
            count += 1
            entries += str(await GROUPS.find_one({'id': i['id']}))+'\n\n'
            await GROUPS.find_one_and_delete({'id': i['id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)
    await x.edit_text("Checking 2nd collection!!!")
    async for i in SFW_GROUPS.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['id'])
        except cp:
            count += 1
            entries += str(await SFW_GROUPS.find_one({'id': i['id']}))+'\n\n'
            await SFW_GROUPS.find_one_and_delete({'id': i['id']})
        except ci:
            count += 1
            entries += str(await SFW_GROUPS.find_one({'id': i['id']}))+'\n\n'
            await SFW_GROUPS.find_one_and_delete({'id': i['id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)
    await x.edit_text("Checking 3rd collection!!!")
    async for i in DC.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['_id'])
        except cp:
            count += 1
            entries += str(await DC.find_one({'_id': i['_id']}))+'\n\n'
            await DC.find_one_and_delete({'_id': i['_id']})
        except ci:
            count += 1
            entries += str(await DC.find_one({'_id': i['_id']}))+'\n\n'
            await DC.find_one_and_delete({'_id': i['_id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)
    await x.edit_text("Checking 4th collection!!!")
    async for i in AG.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['_id'])
        except cp:
            count += 1
            entries += str(await AG.find_one({'id': i['_id']}))+'\n\n'
            await AG.find_one_and_delete({'_id': i['_id']})
        except ci:
            count += 1
            entries += str(await AG.find_one({'id': i['_id']}))+'\n\n'
            await AG.find_one_and_delete({'_id': i['_id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)
    await x.edit_text("Checking 5th collection!!!")
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
    await x.edit_text("Checking 6th collection!!!")
    async for i in CR_GRPS.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['_id'])
        except cp:
            count += 1
            entries += str(await CR_GRPS.find_one({'_id': i['_id']}))+'\n\n'
            await CR_GRPS.find_one_and_delete({'_id': i['_id']})
        except ci:
            count += 1
            entries += str(await CR_GRPS.find_one({'_id': i['_id']}))+'\n\n'
            await CR_GRPS.find_one_and_delete({'_id': i['_id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    await asyncio.sleep(5)
    await x.edit_text("Checking 7th collection!!!")
    async for i in SP_GRPS.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['_id'])
        except cp:
            count += 1
            entries += str(await SP_GRPS.find_one({'_id': i['_id']}))+'\n\n'
            await SP_GRPS.find_one_and_delete({'_id': i['_id']})
        except ci:
            count += 1
            entries += str(await SP_GRPS.find_one({'_id': i['_id']}))+'\n\n'
            await SP_GRPS.find_one_and_delete({'_id': i['_id']})
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


@Client.on_message(filters.command(['start', f'start{BOT_NAME}'], prefixes=trg))
@control_user
async def start_(client: Client, message: Message):
    gid = message.chat.id
    user = message.from_user.id
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'start' in find_gc['cmd_list'].split():
        return
    bot = await client.get_me()
    if gid==user:
        usertitle = message.from_user.username or message.from_user.first_name
        if not (user in OWNER) and not (await USERS.find_one({"id": user})):
            await USERS.insert_one({"id": user, "user": usertitle})
            await clog("ANIBOT", f"New User started bot\n\n[{usertitle}](tg://user?id={user})\nID: `{user}`", "NEW_USER")
        if len(message.text.split())!=1:
            deep_cmd = message.text.split()[1]
            if deep_cmd=="help":
                await help_(client, message)
                return
            if deep_cmd=="auth":
                await auth_link_cmd(client, message)
                return
            if deep_cmd.split("_")[0]=="des":
                pic, result = await get_additional_info(deep_cmd.split("_")[2], "desc", deep_cmd.split("_")[1])
                await client.send_photo(user, pic)
                await client.send_message(user, result.replace("~!", "").replace("!~", ""))
                return
            if deep_cmd.split("_", 1)[0]=="code":
                qry = deep_cmd.split("_", 1)[1]
                k = await AUTH_USERS.find_one({'_id': ObjectId(qry)})
                await code_cmd(k['code'], message)
                return
        await client.send_message(
            gid,
            text=f"""Kon'nichiwa!!!
I'm {bot.first_name} bot and I can help you get info on Animes, Mangas, Characters, Airings, Schedules, Watch Orders of Animes, etc
For more info send /help in here.
If you wish to use me in a group start me by /start{BOT_NAME} command after adding me in the group."""
        )
    else:
        gidtitle = message.chat.username or message.chat.title
        if not await (GROUPS.find_one({"id": gid})):
            await GROUPS.insert_one({"id": gid, "grp": gidtitle})
            await clog("ANIBOT", f"Bot added to a new group\n\n{gidtitle}\nID: `{gid}`", "NEW_GROUP")
        await client.send_message(gid, text="Bot seems online!!!")


@Client.on_message(filters.command(['help', f'help{BOT_NAME}'], prefixes=trg))
@control_user
async def help_(client: Client, message: Message):
    gid = message.chat.id
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'help' in find_gc['cmd_list'].split():
        return
    id_ = message.from_user.id
    bot_us = (await client.get_me()).username
    buttons = help_btns(id_)
    text='''This is a small guide on how to use me\n\n**Basic Commands:**\nUse /ping or !ping cmd to check if bot is online
Use /start or !start cmd to start bot in group or pm
Use /help or !help cmd to get interactive help on available bot cmds
Use /feedback cmd to contact bot owner'''
    if id_ in OWNER:
        await client.send_message(gid, text=text, reply_markup=buttons)
        await client.send_message(
            gid,
            text="""Owners / Sudos can also use

- __/term__ `to run a cmd in terminal`
- __/eval__ `to run a python code (code must start right after cmd like `__/eval print('UwU')__`)`
- __/stats__ `to get stats on bot like no. of users, grps and authorised users`
- __/dbcleanup__ `to remove obsolete/useless entries in database`

Apart from above shown cmds"""
        )
    else:
        if gid==id_:
            await client.send_message(gid, text=text, reply_markup=buttons)
        else:
            await client.send_message(
                gid,
                text="Click below button for bot help",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help", url=f"https://t.me/{bot_us}/?start=help")]])
            )


@Client.on_callback_query(filters.regex(pattern=r"help_(.*)"))
@check_user
async def help_dicc_parser(client, cq: CallbackQuery):
    await cq.answer()
    kek, qry, user = cq.data.split("_")
    text = HELP_DICT[qry]
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"hlplist_{user}")]])
    await cq.edit_message_text(text=text, reply_markup=btn)


@Client.on_callback_query(filters.regex(pattern=r"hlplist_(.*)"))
@check_user
async def help_list_parser(client, cq: CallbackQuery):
    await cq.answer()
    user = cq.data.split("_")[1]
    buttons = help_btns(user)
    text='''This is a small guide on how to use me\n\n**Basic Commands:**\nUse /ping or !ping cmd to check if bot is online
Use /start or !start cmd to start bot in group or pm
Use /help or !help cmd to get interactive help on available bot cmds
Use /feedback cmd to contact bot owner'''
    await cq.edit_message_text(text=text, reply_markup=buttons)


def help_btns(user):
    but_rc = []
    buttons = []
    hd_ = list(natsorted(HELP_DICT.keys()))
    for i in hd_:
        but_rc.append(InlineKeyboardButton(i, callback_data=f"help_{i}_{user}"))
        if len(but_rc)==2:
            buttons.append(but_rc)
            but_rc = []
    if len(but_rc)!=0:
        buttons.append(but_rc)
    return InlineKeyboardMarkup(buttons)


@Client.on_message(filters.user(OWNER) & filters.command(['stats', f'stats{BOT_NAME}'], prefixes=trg))
@control_user
async def stats_(client: Client, message: Message):
    st = datetime.now()
    x = await message.reply_text("Collecting Stats!!!")
    et = datetime.now()
    pt = (et-st).microseconds / 1000
    nosus = await USERS.estimated_document_count()
    nosauus = await AUTH_USERS.estimated_document_count()
    nosgrps = await GROUPS.estimated_document_count()
    nossgrps = await SFW_GROUPS.estimated_document_count()
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
**SFW Groups:** {nossgrps}
**Stargazers:** {kk.get("stargazers_count")}
**Forks:** {kk.get("forks")}
**Ping:** `{pt} ms`
"""
    )


@Client.on_message(filters.command(['ping', f'ping{BOT_NAME}'], prefixes=trg))
@control_user
async def pong_(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc is not None and 'ping' in find_gc['cmd_list'].split():
        return
    st = datetime.now()
    x = await message.reply_text("Ping...")
    et = datetime.now()
    pt = (et-st).microseconds / 1000
    await x.edit_text(f"__Pong!!!__\n`{pt} ms`")


@Client.on_message(filters.private & filters.command(['feedback', f'feedback{BOT_NAME}'], prefixes=trg))
@control_user
async def feed_(client: Client, message: Message):
    owner = await client.get_users(OWNER[0])
    await client.send_message(message.chat.id, f"For issues or queries please contact @{owner.username} or join @hanabi_support")

###### credits to @NotThatMF on tg since he gave me the code for it ######


@Client.on_message(filters.command(['eval', f'eval{BOT_NAME}'], prefixes=trg) & filters.user(OWNER))
@control_user
async def eval(client: Client, message: Message):
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(" ", maxsplit=1)[1]
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message
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
                document=out_file, caption=cmd[:1000], disable_notification=True
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


@Client.on_message(filters.user(OWNER) & filters.command(["term", f"term{BOT_NAME}"], prefixes=trg))
@control_user
async def terminal(client: Client, message: Message):
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
                    parse_mode="markdown",
                )
            output += "**{}**\n".format(code)
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
                """**Error:**\n```{}```""".format("".join(errors)),
                parse_mode="markdown",
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
                reply_to_message_id=message.message_id,
                caption="`Output file`",
            )
            os.remove(filename)
            return
        await message.reply_text(f"**Output:**\n```{output}```", parse_mode="markdown")
    else:
        await message.reply_text("**Output:**\n`No Output`")


##########################################################################