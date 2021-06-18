import io
import sys
import traceback
import os
import re
import subprocess
import asyncio
import requests
from datetime import datetime as dt
from natsort import natsorted
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ChannelInvalid as ci, ChannelPrivate as cp, PeerIdInvalid as pi, FloodWait as fw
from .. import BOT_NAME, TRIGGERS as trg, OWNER, HELP_DICT, anibot
from ..utils.db import get_collection
from ..utils.helper import AUTH_USERS, clog, check_user
from ..utils.data_parser import get_additional_info
from .anilist import auth_link_cmd

USERS = get_collection("USERS")
GROUPS = get_collection("GROUPS")
SFW_GROUPS = get_collection("SFW_GROUPS")
DC = get_collection('DISABLED_CMDS')
AG = get_collection('AIRING_GROUPS')
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
    'getgenres'
]


@Client.on_message(~filters.private & filters.command(['disable', f'disable{BOT_NAME}', 'enable', f'enable{BOT_NAME}']))
async def en_dis__able_cmd(client: Client, message: Message):
    cmd = message.text.split(" ", 1)
    if message.from_user.id in OWNER or (await anibot.get_chat_member(message.chat.id, message.from_user.id)).status!='member':
        if len(cmd)==1:
            x = await message.reply_text('No command specified to be disabled!!!')
            await asyncio.sleep(5)
            await x.delete()
            return
        enable = False if not 'enable' in cmd[0] else True
        if set(cmd[1].split()).issubset(CMD):
            find_gc = await DC.find_one({'_id': message.chat.id})
            if find_gc==None:
                if enable:
                    x = await message.reply_text('Command already enabled!!!')
                    await asyncio.sleep(5)
                    await x.delete()
                    return
                await DC.insert_one({'_id': message.chat.id, 'cmd_list': cmd[1]})
                x = await message.reply_text("Command disabled!!!")
                await asyncio.sleep(5)
                await x.delete()
                return
            else:
                ocls: str = find_gc['cmd_list']
                if set(cmd[1].split()).issubset(ocls.split()):
                    if enable:
                        if len(ocls.split())==1:
                            await DC.delete_one({'_id': message.chat.id})
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
                await DC.update_one({'_id': message.chat.id}, {'$set': {'cmd_list': ncls}})
                x = await message.reply_text(f"Command {'dis' if enable==False else 'en'}abled!!!")
                await asyncio.sleep(5)
                await x.delete()
                return
        else:
            await message.reply_text("Hee, is that a command?!")


@Client.on_message(~filters.private & filters.command(['disabled', f'disabled{BOT_NAME}']))
async def list_disabled(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc==None:
        await message.reply_text("No commands disabled in this group!!!")
    else:
        lscmd = find_gc['cmd_list'].replace(" ", "\n")
        await message.reply_text(f"List of commands disabled in **{message.chat.title}**\n\n{lscmd}")


@Client.on_message(filters.user(OWNER) & filters.command(['dbcleanup', f'dbcleanup{BOT_NAME}'], prefixes=trg))
async def db_cleanup(client: Client, message: Message):
    count = 0
    st = dt.now()
    x = await message.reply_text("Starting database cleanup in 5 seconds")
    et = dt.now()
    pt = (et-st).microseconds / 1000
    onosauus = await AUTH_USERS.estimated_document_count()
    onosgrps = await GROUPS.estimated_document_count()
    onossgrps = await SFW_GROUPS.estimated_document_count()
    await asyncio.sleep(5)
    await x.edit_text("Checking 1st collection!!!")
    async for i in GROUPS.find():
        await asyncio.sleep(2)
        try:
            await client.get_chat(i['id'])
        except cp:
            count += 1
            await GROUPS.find_one_and_delete({'id': i['id']})
        except ci:
            count += 1
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
            await SFW_GROUPS.find_one_and_delete({'id': i['id']})
        except ci:
            count += 1
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
            await DC.find_one_and_delete({'id': i['_id']})
        except ci:
            count += 1
            await DC.find_one_and_delete({'id': i['_id']})
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
            await AG.find_one_and_delete({'_id': i['_id']})
        except ci:
            count += 1
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
            await AUTH_USERS.find_one_and_delete({'id': i['id']})
        except fw:
            await asyncio.sleep(fw.x + 5)
    if count == 0:
        msg = f"""Database seems to be accurate, no changes to be made!!!

**Groups:** `{onosgrps}`
**SFW Groups:** `{onossgrps}`
**Authorised Users:** `{onosauus}`
**Ping:** `{pt}`
"""
    else:
        nosgrps = await GROUPS.estimated_document_count()
        nossgrps = await SFW_GROUPS.estimated_document_count()
        nosauus = await AUTH_USERS.estimated_document_count()
        msg = f"""{count} entries removed from database!!!

**Old Data:**
    __Groups:__ `{onosgrps}`
    __SFW Groups:__ `{onossgrps}`
    __Authorised Users:__ `{onosauus}`

**New Data:**
    __Groups:__ `{nosgrps}`
    __SFW Groups:__ `{nossgrps}`
    __Authorised Users:__ `{nosauus}`

**Ping:** `{pt}`
"""
    await x.edit_text(msg)


@Client.on_message(filters.command(['start', f'start{BOT_NAME}'], prefixes=trg))
async def start_(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'start' in find_gc['cmd_list'].split():
        return
    bot = await client.get_me()
    if message.chat.id==message.from_user.id:
        user = message.from_user
        if not (user.id in OWNER) and not (await USERS.find_one({"id": user.id})):
            await USERS.insert_one({"id": user.id, "user": user.first_name})
            await clog("ANIBOT", f"New User started bot\n\n[{user.first_name}](tg://user?id={user.id})\nID: `{user.id}`", "NEW_USER")
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
                await client.send_photo(user.id, pic)
                await client.send_message(user.id, result.replace("~!", "").replace("!~", ""))
                return
        await client.send_message(
            message.chat.id,
            text=f"""Kon'nichiwa!!!
I'm {bot.first_name} bot and I can help you get info on Animes, Mangas, Characters, Airings, Schedules, Watch Orders of Animes, etc
For more info send /help in here.
If you wish to use me in a group start me by /start{BOT_NAME} command after adding me in the group."""
        )
    else:
        gid = message.chat
        if not await (GROUPS.find_one({"id": gid.id})):
            await GROUPS.insert_one({"id": gid.id, "grp": gid.title})
            await clog("ANIBOT", f"Bot added to a new group\n\n{gid.username or gid.title}\nID: `{gid.id}`", "NEW_GROUP")
        await client.send_message(message.chat.id, text="Bot seems online!!!")


@Client.on_message(filters.command(['help', f'help{BOT_NAME}'], prefixes=trg))
async def help_(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'help' in find_gc['cmd_list'].split():
        return
    id_ = message.from_user.id
    bot_us = (await client.get_me()).username
    buttons = help_btns(id_)
    text='''This is a small guide on how to use me\n\n**Basic Commands:**\nUse /ping or !ping cmd to check if bot is online
Use /start or !start cmd to start bot in group or pm
Use /help or !help cmd to get interactive help on available bot cmds
Use /feedback cmd to contact bot owner'''
    if id_ in OWNER:
        await client.send_message(message.chat.id, text=text, reply_markup=buttons)
        await client.send_message(
            message.chat.id,
            text="""Owners / Sudos can also use

- __/term__ `to run a cmd in terminal`
- __/eval__ `to run a python code (code must start right after cmd like `__/eval print('UwU')__`)`
- __/stats__ `to get stats on bot like no. of users, grps and authorised users`
- __/dbcleanup__ `to remove obsolete/useless entries in database`

Apart from above shown cmds"""
        )
    else:
        if message.chat.id==message.from_user.id:
            await client.send_message(message.chat.id, text=text, reply_markup=buttons)
        else:
            await client.send_message(
                message.chat.id,
                text="Click below button for bot help",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help", url=f"https://t.me/{bot_us}/?start=help")]])
            )


@Client.on_callback_query(filters.regex(pattern=r"help_(.*)"))
@check_user
async def help_dicc_parser(clinet, cq: CallbackQuery):
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
async def stats_(client: Client, message: Message):
    st = dt.now()
    x = await message.reply_text("Collecting Stats!!!")
    et = dt.now()
    pt = (et-st).microseconds / 1000
    nosus = await USERS.estimated_document_count()
    nosauus = await AUTH_USERS.estimated_document_count()
    nosgrps = await GROUPS.estimated_document_count()
    nossgrps = await SFW_GROUPS.estimated_document_count()
    kk = requests.get("https://api.github.com/repos/lostb053/anibot").json()
    await x.edit_text(f"""
Stats:-

**Users:** {nosus}
**Authorised Users:** {nosauus}
**Groups:** {nosgrps}
**SFW Groups:** {nossgrps}
**Stargazers:** {kk.get("stargazers_count")}
**Forks:** {kk.get("forks")}
**Ping:** `{pt} ms`
"""
    )


@Client.on_message(filters.command(['ping', f'ping{BOT_NAME}'], prefixes=trg))
async def pong_(client: Client, message: Message):
    find_gc = await DC.find_one({'_id': message.chat.id})
    if find_gc!=None and 'ping' in find_gc['cmd_list'].split():
        return
    st = dt.now()
    x = await message.reply_text("Ping...")
    et = dt.now()
    pt = (et-st).microseconds / 1000
    await x.edit_text(f"__Pong!!!__\n`{pt} ms`")


@Client.on_message(filters.private & filters.command(['feedback', f'feedback{BOT_NAME}'], prefixes=trg))
async def feed_(client: Client, message: Message):
    owner = await client.get_users(OWNER[0])
    await client.send_message(message.chat.id, f"For issues or queries please contact @{owner.username} or join @hanabi_support")

###### credits to @NotThatMF on tg since he gave me the code for it ######


@Client.on_message(filters.command(['eval', f'eval{BOT_NAME}'], prefixes=trg) & filters.user(OWNER))
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