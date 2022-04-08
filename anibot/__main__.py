import asyncio
from pyrogram import idle
from . import anibot, has_user, session
from .utils.db import _close_db

user = None
if has_user:
    from . import user

async def main():
    await anibot.start()
    if user is not None:
        await user.start()
    await idle()
    await anibot.stop()
    if user is not None:
        await user.stop()
    _close_db()
    await session.close()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
