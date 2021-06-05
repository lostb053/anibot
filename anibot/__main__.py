import asyncio
from pyrogram import Client, idle
from . import anibot
from .utils.db import _close_db


async def main():
    await asyncio.gather(anibot.start())
    await idle()
    await asyncio.gather(anibot.stop())
    _close_db()

asyncio.get_event_loop().run_until_complete(main())