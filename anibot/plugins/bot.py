import io, sys, traceback, os, re, subprocess, asyncio
from datetime import datetime as dt
from natsort import natsorted
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from .. import BOT_NAME, TRIGGERS as trg, OWNER, HELP_DICT
from ..utils.db import get_collection
from ..utils.helper import AUTH_USERS, clog, check_user

USERS = get_collection("USERS")
GROUPS = get_collection("GROUPS")


@Client.on_message(filters.command(['start', f'start{BOT_NAME}'], prefixes=trg))
async def start_(client: Client, message: Message):
    bot = await client.get_me()
    if message.chat.id==message.from_user.id:
        user = message.from_user
        if not (user.id in OWNER) and not (await USERS.find_one({"id": user.id})):
            await asyncio.gather(USERS.insert_one({"id": user.id, "user": user.first_name}))
            await clog("ANIBOT", f"New User started bot\n\n[{user.first_name}](tg://user?id={user.id})\nID: `{user.id}`", "NEW_USER")
        if len(message.text.split(" "))==2:
            if message.text.split(" ")[1]=="help":
                await help_(client, message)
                return
        await client.send_message(
            message.chat.id,
            text=f"""Kon'nichiwa!!!
I'm {bot.first_name} bot and i can help you get info related to Animes, Mangas, Characters, Airing, Schedule, Watch Order, etc...
For more info send /help cmd in pm
If you wish to use me in a group start bot by /start{BOT_NAME} after adding it

**Note:** If bot doesnt responds properly in grps give it admin privilage"""
        )
    else:
        gid = message.chat
        if not await (GROUPS.find_one({"id": gid.id})):
            await asyncio.gather(GROUPS.insert_one({"id": gid.id, "grp": gid.title}))
            await clog("ANIBOT", f"Bot added to a new group\n\n{gid.username or gid.title}\nID: `{gid.id}`", "NEW_GROUP")
        await client.send_message(message.chat.id, text="Bot seems online!!!")


@Client.on_message(filters.command(['help', f'help{BOT_NAME}'], prefixes=trg))
async def help_(client: Client, message: Message):
    id_ = message.from_user.id
    bot_us = (await client.get_me()).username
    buttons = help_btns(id_)
    if id_ in OWNER:
        await client.send_message(message.chat.id, text="Bot Help\nEach button represents available cmd", reply_markup=buttons)
        await client.send_message(
            message.chat.id,
            text="""Owners / Sudos can also use
- __/term__ `to run a cmd in terminal`
- __/eval__ `to run a python code (code must start right after cmd like `__/eval print('UwU')__`)`
- __/stats__ `to getstats on bot like no. of users, grps and authorised users`
Apart from above shown cmds"""
        )
    else:
        if message.chat.id==message.from_user.id:
            await client.send_message(message.chat.id, text="Bot Help\nEach button represents available cmd", reply_markup=buttons)
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
    await cq.edit_message_text(text="Bot Help\nEach button represents available cmd", reply_markup=buttons)


def help_btns(user):
    but_rc = []
    buttons = []
    hd_ = list(natsorted(HELP_DICT.keys()))
    for i in hd_:
        but_rc.append(InlineKeyboardButton(i, callback_data=f"help_{i}_{user}"))
        if len(but_rc)==3:
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
    await x.edit_text(f"""
Stats:-

**User:** {nosus}
**Authourised Users:** {nosauus}
**Groups:** {nosgrps}
**Ping:** `{pt} ms`
"""
    )


@Client.on_message(filters.command(['ping', f'ping{BOT_NAME}'], prefixes=trg))
async def pong_(client: Client, message: Message):
    st = dt.now()
    x = await message.reply_text("Ping...")
    et = dt.now()
    pt = (et-st).microseconds / 1000
    await x.edit_text(f"__Pong!!!__\n`{pt} ms`")

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
                document=out_file, caption=cmd, disable_notification=True
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
async def terminal(client, message):
    if len(message.text.split()) == 1:
        await message.reply("Usage: `/term echo owo`")
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
                await message.reply(
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
            await message.reply(
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
        await message.reply(f"**Output:**\n```{output}```", parse_mode="markdown")
    else:
        await message.reply("**Output:**\n`No Output`")


##########################################################################

HELP_DICT["ping"] = "Use /ping or !ping cmd to check if bot is online"
HELP_DICT["start"] = "Use /start or !start cmd to start bot in group or pm"
HELP_DICT["help"] = "Use /help or !help cmd to get interactive help on available bot cmds"