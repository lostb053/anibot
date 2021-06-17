import requests, re, asyncio
from bs4 import BeautifulSoup as bs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .. import anibot
from ..utils.db import get_collection

url = "https://www.livechart.me/feeds/episodes"
A = get_collection('AIRING_TITLE')
AIRING_GRPS = get_collection('AIRING_GROUPS')

async def livechart_parser():
    print('Parsing data from Livechart.me')
    k = bs(requests.get(url).text, features="html.parser")
    if (await A.find_one())==None:
        await asyncio.gather(A.insert_one({'_id': str(k.find('item').find('title'))}))
        return
    count = 0
    for i in k.findAll("item"):
        if (await A.find_one())['_id'] == str(i.find('title')):
            break
        await asyncio.sleep(2)
        async for id_ in AIRING_GRPS.find():
            if '#' in str(i.find('title')):
                await Client.send_message(anibot, id_['_id'], re.sub(r"(.*)#([0-9]+)", r"Episode \2 of \1just aired", str(i.find('title'))), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("More Info", url=re.sub(r'<.*?>(.*)<.*?>', r'\1', str(i.find('guid'))))]]))
            else:
                await Client.send_message(anibot, id_['_id'], str(i.find('title'))+' just aired', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("More Info", url=re.sub(r'<.*?>(.*)<.*?>', r'\1', str(i.find('guid'))))]]))
        count += 1
    if count!=0:
        await asyncio.gather(A.drop())
        await asyncio.gather(A.insert_one({'_id': str(k.find('item').find('title'))}))


scheduler = AsyncIOScheduler()
scheduler.add_job(livechart_parser, "interval", minutes=20)
scheduler.start()