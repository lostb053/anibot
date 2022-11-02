import requests
import re
import asyncio
import time
from traceback import format_exc as err
from bs4 import BeautifulSoup as bs
from collections import defaultdict
from datetime import datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import WebpageCurlFailed, WebpageMediaEmpty, ChatAdminRequired
from .. import anibot
from ..utils.db import get_collection
from ..utils.helper import clog

failed_pic = "https://telegra.ph/file/09733b49f3a9d5b147d21.png"

url_a = "https://www.livechart.me/feeds/episodes"
url_b = 'https://feeds.feedburner.com/crunchyroll/rss/anime?format=xml'
url_c = 'https://subsplease.org/rss/?t'
url_d = 'https://www.livechart.me/feeds/headlines'
url_e = 'https://myanimelist.net/rss/news.xml'

A = get_collection('AIRING_TITLE')
B = get_collection('CRUNCHY_TITLE')
C = get_collection('SUBSPLEASE_TITLE')
D = get_collection('HEADLINES_TITLE')
E = get_collection('MAL_HEADLINES_TITLE')
AR_GRPS = get_collection('AIRING_GROUPS')
CR_GRPS = get_collection('CRUNCHY_GROUPS')
SP_GRPS = get_collection('SUBSPLEASE_GROUPS')
HD_GRPS = get_collection('HEADLINES_GROUPS')
MAL_HD_GRPS = get_collection('MAL_HEADLINES_GROUPS')

admin_error_msg = "Please give bot Pin Message and Delete Message permissions to pin new headlines!!!\nOr you can disable Pin and Unpin options in /settings command to stop seeing this message"

async def livechart_parser():
    print('Parsing data from rss')
    da = bs(requests.get(url_a).text, features="xml")
    db = bs(requests.get(url_b).text, features="xml")
    dc = bs(requests.get(url_c).text, features='xml')
    dd = bs(requests.get(url_d).text, features='xml')
    de = bs(requests.get(url_e).text, features='xml')
    if (await A.find_one()) is None:
        await A.insert_one(
            {
                '_id': str(da.find('item').find('title')),
                'guid': str(da.find('item').find('guid'))
            }
        )
        return
    if (await B.find_one()) is None:
        await B.insert_one(
            {
                '_id': str(db.find('item').find('title')),
                'guid': str(db.find('item').find('guid'))
            }
        )
        return
    if (await C.find_one()) is None:
        await C.insert_one({'_id': str(dc.find('item').find('title'))})
        return
    if (await D.find_one()) is None:
        await D.insert_one(
            {
                '_id': str(dd.find('item').find('title')),
                'guid': str(dd.find('item').find('guid'))
            }
        )
        return
    if (await E.find_one()) is None:
        await E.insert_one(
            {
                '_id': str(de.find('item').find('title')),
                'guid': str(de.find('item').find('guid'))
            }
        )
        return
    msgslc = []
    msgscr = []
    msgssp = []
    msgslch = []
    msgsmh = []
    lc = []
    cr = []
    sp = []
    hd = []
    mhd = []
    lc_pin_data = []
    mal_pin_data = []

#### LiveChart.me / airing ####
    try:
        clc = defaultdict(list)
        for i in da.findAll("item"):
            if (await A.find_one())['_id'] == str(i.find('title')):
                break
            lc.append(
                [
                    str(i.find('title')).split(' #'),
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', str(i.find('guid')))
                ]
            )
            if (await A.find_one())['guid'] == str(i.find('guid')):
                break
        for i in lc:
            if len(i[0])==2:
                clc[i[0][0]].append([i[0][1], i[1]])
            else:
                text = f'{i[0][0]} just aired'
                msgslc.append([text, i[1]])
        for i in list(clc.keys()):
            if len(clc[i])>1:
                aep = [clc[i][len(clc[i])-1][0], clc[i][0][0]]
                text = f'\nEpisode {min(aep)} - {max(aep)} of {i} just aired'
            else:
                text = f'\nEpisode {clc[i][0][0]} of {i} just aired'
            msgslc.append([text, clc[i][0][1]])
    except Exception:
        e = err()
        await clog("ANIBOT", "```"+e+"```", "RSS")
###############################


#### CrunchyRoll.com ####
    try:
        clc = defaultdict(list)
        fk = []
        for i in db.findAll('item'):
            if (await B.find_one())['_id'] == str(i.find('title')):
                break
            if not "Dub" in str(i.find('title')):
                cr.append(
                    [
                        str(i.find('title')).split(' - '),
                        re.sub(r'<.*?>(.*)<.*?>', r'\1', str(i.find('guid')))
                    ]
                )
            if (await B.find_one())['guid'] == str(i.find('guid')):
                break
        for i in cr:
            if len(i[0])==3:
                clc[i[0][0]].append([i[0][1], i[0][2], i[1]])
            elif len(i[0])==2:
                if 'Episode' in i[0][1]:
                    clc[i[0][0]].append([i[0][1], i[1]])
                else:
                    msgscr.append([
f"""**New anime released on Crunchyroll**
**Title:** {i[0][0]}""",
                        i[1]
                    ])
            else:
                fk.append(i)
        for i in list(clc.keys()):
            hmm = []
            for ii in clc[i]:
                try:
                    hmm.append(int((ii[0].split())[1]))
                except ValueError:
                    fk.append(clc[i])
            try:
                aep = [min(hmm), max(hmm)]
                epnum = f"{aep[0]} - {aep[1]}" if aep[1]!=aep[0] else aep[0]
                msgscr.append([
f"""**New anime released on Crunchyroll**

**Title:** {i}
**Episode:** {epnum}
{'**EP Title:** '+ii[1] if len(ii)==3 else ''}""",
                ii[1] if len(ii)!=3 else ii[2]
                ])
            except Exception as e:
                fk.append(i)
        if len(fk)==0:
            for i in fk:
                await clog(
                    "ANIBOT",
                    "<b>Missed crunchyroll update\nCheck out code</b>",
                    "MISSED_UPDATE",
                    send_as_file=str(i)
                )
    except Exception:
        e = err()
        await clog("ANIBOT", "```"+e+"```", "RSS")
#########################


##### Subsplease.org #####
    try:
        ls = defaultdict(list)
        for i in dc.findAll('item'):
            if (await C.find_one())['_id'] in str(i.find('title')):
                break
            text = re.sub(
                r'.*\[.+?\] (.+) (\(.+p\)) \[.+?\].*',
                r'\1__________\2',
                str(i.find('title'))
            )
            link = re.sub(
                r'.*<.+?>(.+)<.+?>.*',
                r'\1',
                str(i.find('link'))
            )
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
                msgssp.append(
                    [
                        '**New anime uploaded on Subsplease**\n\n'
                        +i
                        +listlinks,
                        'https://nyaa.si/?q='
                        +re.sub(
                            r' ',
                            '%20',
                            re.sub(r'(\().*?(\))', r'', i).strip()
                        )
                    ]
                )
    except Exception:
        e = err()
        await clog("ANIBOT", "```"+e+"```", "RSS")
##########################


#### LiveChart.me / headlines ####
    try:
        for i in dd.findAll("item"):
            update = ""
            if (await D.find_one())['_id'] == str(i.find('title')):
                break
            elif (await D.find_one())['guid'] == str(i.find('guid')):
                update = "**[UPDATED]** "
            title = str(i.find('title'))
            guid = str(i.find('guid'))
            url = str(i.find('link'))
            enclosure = i.find('enclosure')
            if not None in [title, guid, url, enclosure]:
                hd.append([
                    update+re.sub(r'<.*?>(.*)<.*?>', r'\1', title),
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', guid),
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', url),
                    str(i.find('enclosure').get('url')).split('?')[0]
                ])
            else:
                await clog(
                    "ANIBOT",
                    "<b>Missed headline\nCheck out code</b>",
                    "MISSED_UPDATE",
                    send_as_file=str(i)
                )
            if (await D.find_one())['guid'] == str(i.find('guid')):
                break
        for i in hd:
            msgslch.append([i[3], i[0], i[1], i[2]])
    except Exception:
        e = err()
        await clog("ANIBOT", "```"+e+"```", "RSS")
##################################


#### MyAnimeList / headlines ####
    try:
        for i in de.findAll("item"):
            update = ""
            if (await E.find_one())['_id'] == str(i.find('title')):
                break
            elif (await E.find_one())['guid'] == str(i.find('guid')):
                update = "**[UPDATED]** "
            title = str(i.find('title'))
            guid = str(i.find('guid'))
            description = str(i.find('description'))
            thumbnail = str(i.find('media:thumbnail'))
            if not None in [title, guid, description, thumbnail]:
                mhd.append([
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', title),
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', description),
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', guid),
                    re.sub(r'<.*?>(.*)<.*?>', r'\1', thumbnail)
                ])
            else:
                await clog(
                    "ANIBOT",
                    f"<b>Missed MAL headline\nCheck out code</b>",
                    "MISSED_UPDATE",
                    send_as_file=str(i)
                )
            if (await E.find_one())['guid'] == str(i.find('guid')):
                break
        for i in mhd:
            msgsmh.append([i[3], f"**{i[0]}**\n\n{i[1]}", i[2]])
    except Exception:
        e = err()
        await clog("ANIBOT", "```"+e+"```", "RSS")
#################################


    print('Notifying Livachart.me airings!!!')
    if await AR_GRPS.find_one() is not None:
        for i in msgslc:
            async for id_ in AR_GRPS.find():
                btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("More Info", url=i[1])
                ]])
                try:
                    await anibot.send_message(
                        id_['_id'], i[0], reply_markup=btn
                    )
                    await asyncio.sleep(1.5)
                except Exception:
                    e = err()
                    await clog("ANIBOT", f"Group: {id_['_id']}\n\n```{e}```", "AIRING")
    if len(msgslc)!=0:
        await A.drop()
        await A.insert_one(
            {
                '_id': str(da.find('item').find('title')),
                'guid': str(da.find('item').find('guid'))
            }
        )
    await asyncio.sleep(10)


    print('Notifying Crunchyroll releases!!!')
    if await CR_GRPS.find_one() is not None:
        for i in msgscr:
            async for id_ in CR_GRPS.find():
                btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("More Info", url=i[1])
                ]])
                try:
                    await anibot.send_message(
                        id_['_id'], i[0], reply_markup=btn
                    )
                    await asyncio.sleep(1.5)
                except Exception:
                    e = err()
                    await clog("ANIBOT", f"Group: {id_['_id']}\n\n```{e}```", "CRUNCHYROLL")
    if len(msgscr)!=0:
        await B.drop()
        await B.insert_one(
            {
                '_id': str(db.find('item').find('title')),
                'guid': str(db.find('item').find('guid'))
            }
        )
    await asyncio.sleep(10)


    print('Notifying Subsplease releases!!!')
    if await SP_GRPS.find_one() is not None:
        for i in msgssp:
            async for id_ in SP_GRPS.find():
                btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("Download", url=i[1])
                ]])
                try:
                    await anibot.send_message(
                        id_['_id'], i[0], reply_markup=btn
                    )
                    await asyncio.sleep(1.5)
                except Exception:
                    e = err()
                    await clog("ANIBOT", f"Group: {id_['_id']}\n\n```{e}```", "SUBSPLEASE")
    await asyncio.sleep(10)    

    
    list_keys = ["_id", "pin", "unpin", "next_unpin", "last"]
    print('Notifying LiveChart.me Headlines!!!')
    if await HD_GRPS.find_one() is not None:
        for i in msgslch:
            async for id_ in HD_GRPS.find():
                var_dict = {}
                btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("More Info", url=i[2]),
                    InlineKeyboardButton("Source", url=i[3]),
                ]])
                try:
                    try:
                        x = await anibot.send_photo(
                            id_['_id'],
                            i[0],
                            caption=i[1]+'\n\n#LiveChart',
                            reply_markup=btn
                        )
                    except (WebpageMediaEmpty, WebpageCurlFailed):
                        x = await anibot.send_photo(
                            id_['_id'],
                            failed_pic,
                            caption=i[1]+'\n\n#LiveChart',
                            reply_markup=btn
                        )
                        await clog("ANIBOT", i[0], "HEADLINES LINK")
                    for var in list_keys:
                        try:
                            var_dict[var] = id_[var]
                        except KeyError:
                            var_dict[var] = None
                    var_dict["current"] = x.id
                    lc_pin_data.append(var_dict)
                    await asyncio.sleep(1.5)
                except Exception:
                    e = err()
                    await clog("ANIBOT", f"Group: {id_['_id']}\n\n```{e}```", "HEADLINES")
    if len(msgslch)!=0:
        await D.drop()
        await D.insert_one(
            {
                '_id': str(dd.find('item').find('title')),
                'guid': str(dd.find('item').find('guid'))
            }
        )
    

    print('Notifying MyAnimeList.net Headlines!!!')
    if await MAL_HD_GRPS.find_one() is not None:
        for i in msgsmh:
            async for id_ in MAL_HD_GRPS.find():
                var_dict = {}
                btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("More Info", url=i[2]),
                ]])
                try:
                    try:
                        x = await anibot.send_photo(
                            id_['_id'],
                            i[0],
                            caption=i[1]+'\n\n#MyAnimeList',
                            reply_markup=btn
                        )
                    except (WebpageMediaEmpty, WebpageCurlFailed):
                        x = await anibot.send_photo(
                            id_['_id'],
                            failed_pic,
                            caption=i[1]+'\n\n#MyAnimeList',
                            reply_markup=btn
                        )
                        await clog("ANIBOT", i[0], "HEADLINES LINK")
                    for var in list_keys:
                        try:
                            var_dict[var] = id_[var]
                        except KeyError:
                            var_dict[var] = None
                    var_dict["current"] = x.id
                    mal_pin_data.append(var_dict)
                    await asyncio.sleep(1.5)
                except Exception:
                    e = err()
                    await clog("ANIBOT", f"Group: {id_['_id']}\n\n```{e}```", "HEADLINES")
    if len(msgsmh)!=0:
        await E.drop()
        await E.insert_one(
            {
                '_id': str(de.find('item').find('title')),
                'guid': str(de.find('item').find('guid'))
            }
        )
    

    print("Handling Pins and Unpins!!!")
    lc_final_dict = []
    lc_listed = []
    for i in lc_pin_data:
        if i["_id"] in lc_listed:
            lc_final_dict[lc_listed.index(i["_id"])]["current"].append(i["current"])
        else:
            lc_listed.append(i['_id'])
            lc_final_dict.append({"_id": i["_id"], "pin": i["pin"], "current": [i["current"]]})
    mal_final_dict = []
    mal_listed = []
    for i in mal_pin_data:
        if i["_id"] in mal_listed:
            mal_final_dict[mal_listed.index(i["_id"])]["current"].append(i["current"])
        else:
            mal_listed.append(i['_id'])
            mal_final_dict.append({"_id": i["_id"], "pin": i["pin"], "current": [i["current"]]})
    for i in lc_final_dict:
        if i['pin'] not in ["OFF", None]:
            if i['unpin'] == 0:
                i['current'] = [i['current'].pop()]
            for mid in i['current']:
                try:
                    pin_msg = await anibot.pin_chat_message(i['_id'], mid)
                    await pin_msg.delete()
                except ChatAdminRequired:
                    await anibot.send_message(i['_id'], admin_error_msg)
                except:
                    e = err()
                    await clog("ANIBOT", f"Group: {i['_id']}\n\n```{e}```", "UN_PIN")
                await asyncio.sleep(0.7)
        unpin_now = False
        if i['unpin']:
            if i['next_unpin']:
                if time.time() > i['next_unpin']:
                    unpin_now = True
            else:
                unpin_now = True
        if unpin_now:
            await HD_GRPS.find_one_and_update({"_id": i['_id']}, {"$set": {"last": i['current']}})
            for mid in i['last']:
                try:
                    await anibot.unpin_chat_message(i['_id'], mid)
                except ChatAdminRequired:
                    await anibot.send_message(i['_id'], admin_error_msg)
                except:
                    e = err()
                    await clog("ANIBOT", f"Group: {i['_id']}\n\n```{e}```", "UN_PIN")
        elif (len(lc_final_dict) != 0) and (i['unpin'] not in [None, 0]):
            tbud = await HD_GRPS.find_one({"_id": i['_id']})
            await HD_GRPS.find_one_and_update(tbud, {"$set": {"last": i['current']+tbud['last']}})
    for i in mal_final_dict:
        if i['pin'] not in ["OFF", None]:
            if i['unpin'] == 0:
                i['current'] = [i['current'].pop()]
            for mid in i['current']:
                try:
                    pin_msg = await anibot.pin_chat_message(i['_id'], mid)
                    await pin_msg.delete()
                except ChatAdminRequired:
                    await anibot.send_message(i['_id'], admin_error_msg)
                except:
                    e = err()
                    await clog("ANIBOT", f"Group: {i['_id']}\n\n```{e}```", "UN_PIN")
                await asyncio.sleep(0.7)
        unpin_now = False
        if i['unpin']:
            if i['next_unpin']:
                if time.time() > i['next_unpin']:
                    unpin_now = True
            else:
                unpin_now = True
        if unpin_now:
            await MAL_HD_GRPS.find_one_and_update({"_id": i['_id']}, {"$set": {"last": i['current']}})
            for mid in i['last']:
                try:
                    await anibot.unpin_chat_message(i['_id'], mid)
                except ChatAdminRequired:
                    await anibot.send_message(i['_id'], admin_error_msg)
                except:
                    e = err()
                    await clog("ANIBOT", f"Group: {i['_id']}\n\n```{e}```", "UN_PIN")
        elif (len(lc_final_dict) != 0) and (i['unpin'] not in [None, 0]):
            tbud = await HD_GRPS.find_one({"_id": i['_id']})
            await MAL_HD_GRPS.find_one_and_update(tbud, {"$set": {"last": i['current']+tbud['last']}})


scheduler = AsyncIOScheduler()
scheduler.add_job(livechart_parser, "interval", minutes=5)
scheduler.start()