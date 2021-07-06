import requests
import re
import asyncio
from bs4 import BeautifulSoup as bs
from collections import defaultdict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .. import anibot
from ..utils.db import get_collection

url_a = "https://www.livechart.me/feeds/episodes"
url_b = 'https://feeds.feedburner.com/crunchyroll/rss/anime?format=xml'
url_c = 'https://subsplease.org/rss/?t'
A = get_collection('AIRING_TITLE')
B = get_collection('CRUNCHY_TITLE')
C = get_collection('SUBSPLEASE_TITLE')
AR_GRPS = get_collection('AIRING_GROUPS')
CR_GRPS = get_collection('CRUNCHY_GROUPS')
SP_GRPS = get_collection('SUBSPLEASE_GROUPS')

async def livechart_parser():
    print('Parsing data from rss')
    da = bs(requests.get(url_a).text, features="xml")
    db = bs(requests.get(url_b).text, features="xml")
    dc = bs(requests.get(url_c).text, features='xml')
    if (await A.find_one()) is None:
        await A.insert_one({'_id': str(da.find('item').find('title'))})
        return
    if (await B.find_one()) is None:
        await B.insert_one({'_id': str(db.find('item').find('title'))})
        return
    if (await C.find_one()) is None:
        await C.insert_one({'_id': str(dc.find('item').find('title'))})
        return
    count_a = 0
    count_b = 0
    msgslc = []
    msgscr = []
    msgssp = []
    lc = []
    cr = []
    sp = []


#### LiveChart.me ####
    clc = defaultdict(list)
    for i in da.findAll("item"):
        if (await A.find_one())['_id'] == str(i.find('title')):
            break
        lc.append([str(i.find('title')).split(' #'), re.sub(r'<.*?>(.*)<.*?>', r'\1', str(i.find('guid')))])
        count_a += 1
    if count_a!=0:
        await A.drop()
        await A.insert_one({'_id': str(da.find('item').find('title'))})
    for i in lc:
        if len(i[0])==2:
            clc[i[0][0]].append([i[0][1], i[1]])
        else:
            text = f'{i[0][0]} just aired'
            msgslc.append([text, i[1]])
    for i in list(clc.keys()):
        if len(clc[i])>1:
            text = f'\nEpisode {clc[i][len(clc[i])-1][0]} - {clc[i][0][0]} of {i} just aired'
        else:
            text = f'\nEpisode {clc[i][0][0]} of {i} just aired'
        msgslc.append([text, clc[i][0][1]])
######################


#### CrunchyRoll.com ####
    clc = defaultdict(list)
    fk = []
    for i in db.findAll('item'):
        if (await B.find_one())['_id'] == str(i.find('title')):
            break
        cr.append([str(i.find('title')).split(' - '), re.sub(r'<.*?>(.*)<.*?>', r'\1', str(i.find('guid')))])
        count_b+=1
    if count_b!=0:
        await B.drop()
        await B.insert_one({'_id': str(db.find('item').find('title'))})
    for i in cr:
        if len(i[0])==3:
            clc[i[0][0].split('(')[0]].append([i[0][1], i[0][2], i[1]])
        elif len(i[0])==2:
            if 'Episode' in i[0][1]:
                clc[i[0][0]].append([i[0][1], i[1]])
            else:
                msgscr.append([f"**New anime released on Crunchyroll**\n\n**Title:** {i[0][0]}", i[1]])
        else:
            fk.append(i)
    for i in list(clc.keys()):
        hmm = []
        for ii in clc[i]:
            hmm.append(ii[0].split()[1])
        msgscr.append([f"**New anime released on Crunchyroll**\n\n**Title:** {i}\n**Episode:** {hmm[len(hmm)-1]+' - '+hmm[0] if len(hmm)!=1 and hmm[len(hmm)-1]!=hmm[0] else hmm[0]}\n{'**EP Title:** '+ii[1] if len(ii)==3 else ''}", ii[1] if len(ii)!=3 else ii[2]])
#########################


##### Subsplease.org #####
    ls = defaultdict(list)
    for i in dc.findAll('item'):
        if (await C.find_one())['_id'] in str(i.find('title')):
            break
        text = re.sub(r'.*\[.+?\] (.+) (\(.+p\)) \[.+?\].*', r'\1__________\2', str(i.find('title')))
        link = re.sub(r'.*<.+?>(.+)<.+?>.*', r'\1', str(i.find('link')))
        sp.append([text, link])
    for i in sp:
        hmm = i[0].split('__________')
        ls[hmm[0]].append([hmm[1].replace(')', '').replace('(', ''), i[1]])
    updated = False
    for i in ls.keys():
        if len(ls[i])==3:
            if not updated:
                await C.drop()
                await C.insert_one({'_id': i})
                updated = True
            listlinks = ""
            for ii in ls[i]:
                listlinks += '\n__'+ii[0]+'__: [Link]('+ii[1]+')'
            msgssp.append(['**New anime uploaded on Subsplease**\n\n' + i + listlinks, 'https://nyaa.si/?q='+re.sub(r' ', '%20', re.sub(r'(\().*?(\))', r'', i).strip())])
##########################


    print('Notifying Livachart.me airings!!!')
    for i in msgslc:
        if await AR_GRPS.find_one()  is not None:
            async for id_ in AR_GRPS.find():
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("More Info", url=i[1])]])
                await anibot.send_message(id_['_id'], i[0], reply_markup=btn)
                await asyncio.sleep(1.5)
    await asyncio.sleep(10)
    print('Notifying Crunchyroll releases!!!')
    for i in msgscr:
        if await CR_GRPS.find_one()  is not None:
            async for id_ in CR_GRPS.find():
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("More Info", url=i[1])]])
                await anibot.send_message(id_['_id'], i[0], reply_markup=btn)
                await asyncio.sleep(1.5)
    await asyncio.sleep(10)
    print('Notifying Subsplease releases!!!')
    for i in msgssp:
        if await SP_GRPS.find_one()  is not None:
            async for id_ in SP_GRPS.find():
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("Download", url=i[1])]])
                await anibot.send_message(id_['_id'], i[0], reply_markup=btn)
                await asyncio.sleep(1.5)


scheduler = AsyncIOScheduler()
scheduler.add_job(livechart_parser, "interval", minutes=4)
scheduler.start()