import requests, time
from .helper import cflag, make_it_rw, pos_no, return_json_senpai, day_
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from jikanpy import AioJikan
from datetime import datetime

ANIME_DB, MANGA_DB = {}, {}

#### Anilist part ####

ANIME_TEMPLATE = """{name}

**ID | MAL ID:** `{idm}` | `{idmal}`
➤ **SOURCE:** `{source}`
➤ **TYPE:** `{formats}`{dura}
{status_air}{user_data}
➤ **ADULT RATED:** `{adult}`
🎬 {trailer_link}
📖 <a href="{url}">Synopsis & More</a>

{additional}"""

# GraphQL Queries.
ANIME_QUERY = """
query ($id: Int, $idMal:Int, $search: String) {
  Media (id: $id, idMal: $idMal, search: $search, type: ANIME) {
    id
    idMal
    title {
      romaji
      english
      native
    }
    format
    status
    episodes
    duration
    countryOfOrigin
    source (version: 2)
    trailer {
      id
      site
    }
    relations {
      edges {
        node {
          title {
            romaji
            english
          }
          id
        }
        relationType
      }
    }
    nextAiringEpisode {
      timeUntilAiring
      episode
    }
    isAdult
    isFavourite
    mediaListEntry {
      status
      score
      id
    }
    siteUrl
  }
}
"""

ACTIVITY_QUERY = """
query ($id: Int) {
  Page (perPage: 10) {
    mediaList (userId: $id, sort: UPDATED_TIME_DESC) {
      progress 
      status
      media {
        title {
          romaji
        }
        type
        siteUrl
      }
    }
  }
}"""

FAV_QUERY = """
query ($id: Int) {
  User (id: $id) {
    favourites {
      anime (perPage: 10) {
        edges {
          node {
            title {
              romaji
            }
          }
        }
      }
    }
  }
}
"""

VIEWER_QRY = """
query {
  Viewer{
    id
    name
    siteUrl
    statistics {
      anime {
        count
        minutesWatched
        episodesWatched
        meanScore
      }
      manga {
        count
        chaptersRead
        volumesRead
        meanScore
      }
    }
  }
}
"""

USER_QRY = """
query ($search: String) {
  User (name: $search) {
    id
    name
    siteUrl
    statistics {
      anime {
        count
        minutesWatched
        episodesWatched
        meanScore
      }
      manga {
        count
        chaptersRead
        volumesRead
        meanScore
      }
    }
  }
}
"""

ANIME_MUTATION = """
mutation ($id: Int) {
  ToggleFavourite (animeId: $id) {
    anime {
      pageInfo {
        total
      }
    }
  }
}"""

MANGA_MUTATION = """
mutation ($id: Int) {
  ToggleFavourite (mangaId: $id) {
    manga {
      pageInfo {
        total
      }
    }
  }
}"""

CHAR_MUTATION = """
mutation ($id: Int) {
  ToggleFavourite (characterId: $id) {
    characters {
      pageInfo {
        total
      }
    }
  }
}"""

ANILIST_MUTATION = """
mutation ($id: Int, $status: MediaListStatus) {
  SaveMediaListEntry (mediaId: $id, status: $status) {
    media {
      title {
        romaji
      }
    }
  }
}"""

ANILIST_MUTATION_UP = """
mutation ($id: [Int], $status: MediaListStatus) {
  UpdateMediaListEntries (ids: $id, status: $status) {
    media {
      title {
        romaji
      }
    }
  }
}"""

ANILIST_MUTATION_DEL = """
mutation ($id: Int) {
  DeleteMediaListEntry (id: $id) {
    deleted
  }
}"""

AIR_QUERY = """
query ($id: Int, $idMal:Int, $search: String) {
  Media (id: $id, idMal: $idMal, search: $search, type: ANIME) {
    id
    title {
      romaji
      english
    }
    status
    countryOfOrigin
    nextAiringEpisode {
      timeUntilAiring
      episode
    }
    siteUrl
    isFavourite
    mediaListEntry {
      status
      id
    }
  }
}
"""

DES_INFO_QUERY = """
query ($id: Int) {
  Media (id: $id, type: ANIME) {
    id
    description (asHtml: false)
  }
}
"""

CHA_INFO_QUERY = """
query ($id: Int) {
  Media (id: $id, type: ANIME) {
    id
    characters (role: MAIN, page: 1, perPage: 20) {
      nodes {
        name {
          full
        }
      }
    }
  }
}
"""

REL_INFO_QUERY = """
query ($id: Int) {
  Media (id: $id, type: ANIME) {
    id
    relations {
      edges {
        node {
          title {
            romaji
          }
        }
        relationType
      }
    }
  }
}
"""

PAGE_QUERY = """
query ($search: String, $page: Int) {
  Page (perPage: 1, page: $page) {
    pageInfo {
      total
    }
    media (search: $search, type: ANIME) {
      id
      idMal
      title {
        romaji
        english
        native
      }
      format
      status
      episodes
      duration
      countryOfOrigin
      source (version: 2)
      trailer {
        id
        site
      }
      relations {
        edges {
          node {
            title {
              romaji
              english
            }
          }
          relationType
          }
        }
      nextAiringEpisode {
        timeUntilAiring
        episode
      }
      isAdult
      isFavourite
      mediaListEntry {
        status
        score
        id
      }
      siteUrl
    }
  }
}
"""

CHARACTER_QUERY = """
query ($id: Int, $search: String, $page: Int) {
  Page (perPage: 1, page: $page) {
    pageInfo{
      total
    }
    characters (id: $id, search: $search) {
      id
      name {
        full
        native
      }
      image {
        large
      }
      isFavourite
      siteUrl
    }
  }
}
"""

MANGA_QUERY = """
query ($search: String, $page: Int) {
  Page (perPage: 1, page: $page) {
    pageInfo {
      total
    }
    media (search: $search, type: MANGA) {
      id
      title {
        romaji
        english
        native
      }
      format
      countryOfOrigin
      source (version: 2)
      status
      description(asHtml: true)
      chapters
      isFavourite
      mediaListEntry {
        status
        score
        id
      }
      volumes
      averageScore
      siteUrl
    }
  }
}
"""


DESC_INFO_QUERY = """
query ($id: Int) {
	Character (id: $id) {
    image {
      large
    }
    description(asHtml: false)
  }
}
"""

LS_INFO_QUERY = """
query ($id: Int) {
	Character (id: $id) {
    image {
      large
    }
    media (page: 1, perPage: 25) {
      nodes {
        title {
          romaji
          english
        }
        type
      }
    }
  }
}
"""


async def get_us_act(id_, user):
    vars_ = {"id": id_}
    result = await return_json_senpai(ACTIVITY_QUERY, vars_, auth=True, user=user)
    data = result["data"]["Page"]["mediaList"]
    msg = ""
    for i in data:
        name = f"[{i['media']['title']['romaji']}]({i['media']['siteUrl']})"
        if i['media']['type']=="MANGA":
            if i['status'] in ["COMPLETED", "DROPPED", "PAUSED", "REPEATING"]:
                msg += f"⚬ {i['status'].capitalize()} reading \n"
            if i['status']=="CURRENT":
                msg += f"⚬ Read chapter {i['progress']} of {name}\n"
            if i['status']=="PLANNING":
                msg += f"⚬ Planning to read {name}\n"
        if i['media']['type']=="ANIME":
            if i['status'] in ["COMPLETED", "DROPPED", "PAUSED", "REPEATING"]:
                msg += f"⚬ {i['status'].capitalize()} watching {name}\n"
            if i['status']=="CURRENT":
                msg += f"⚬ Watch episode {i['progress']} of {name}\n"
            if i['status']=="PLANNING":
                msg += f"⚬ Planning to watch {name}\n"
    btn = [[InlineKeyboardButton("Back", callback_data=f"getusrbc_{user}")]]
    return f"https://img.anili.st/user/{id_}", msg, InlineKeyboardMarkup(btn)


async def get_us_fav(id_, user):
    vars_ = {"id": id_}
    result = await return_json_senpai(FAV_QUERY, vars_, auth=True, user=user)
    data = result["data"]["User"]["favourites"]["anime"]["edges"]
    msg = "Favourite animes:\n\n"
    for i in data:
        msg += f"⚬ {i['node']['title']['romaji']}\n"
    btn = [[InlineKeyboardButton("Back", callback_data=f"getusrbc_{user}")]]
    return f"https://img.anili.st/user/{id_}", msg, InlineKeyboardMarkup(btn)


async def get_ls(idm, req, auth: bool = False, user: int = None):
    vars_ = {"id": int(idm)}
    result = await return_json_senpai(LS_INFO_QUERY, vars_, auth=auth, user=user)
    data = result["data"]["Character"]["media"]["nodes"]
    if req == "ANI":
        out = "ANIMES:\n\n"
        out_ = ""
        for ani in data:
            k = ani["title"]["english"] or ani["title"]["romaji"]
            kk = ani["type"]
            if kk == "ANIME":
                out_ += f"• __{k}__\n"
        return (out+out_ if len(out_) != 0 else False), result["data"]["Character"]["image"]["large"]
    else:
        out = "MANGAS:\n\n"
        out_ = ""
        for ani in data:
            k = ani["title"]["english"] or ani["title"]["romaji"]
            kk = ani["type"]
            if kk == "MANGA":
                out_ += f"• __{k}__\n"
        return (out+out_ if len(out_) != 0 else False), result["data"]["Character"]["image"]["large"]


async def get_info(idm, req, ctgry, auth: bool = False, user: int = None):
    vars_ = {"id": int(idm)}
    result = await return_json_senpai(
        (
            (
                DES_INFO_QUERY
                if req == "desc"
                else CHA_INFO_QUERY
                if req == "char"
                else REL_INFO_QUERY
            )
            if ctgry == "ANI"
            else DESC_INFO_QUERY
        ),
        vars_,
        auth=auth,
        user=user
    )
    data = result["data"]["Media"] if ctgry == "ANI" else result["data"]["Character"]
    pic = f"https://img.anili.st/media/{idm}"
    if req == "desc":
        synopsis = data.get("description")
        return (pic if ctgry == "ANI" else data["image"]["large"]), synopsis
    elif req == "char":
        charlist = []
        for char in data["characters"]["nodes"]:
            charlist.append(f"• {char['name']['full']}")
        chrctrs = ("\n").join(charlist)
        charls = f"`{chrctrs}`" if len(charlist) != 0 else ""
        return pic, charls
    else:
        prqlsql = data.get("relations").get("edges")
        ps = ""
        for i in prqlsql:
            ps += f'• {i["node"]["title"]["romaji"]} `{i["relationType"]}`\n'
        return pic, ps


async def get_ani(vars_, auth: bool = False, user: int = None):
    result = await return_json_senpai(ANIME_QUERY, vars_, auth=auth, user=user)

    error = result.get("errors")
    if error:
        error_sts = error[0].get("message")
        return [f"[{error_sts}]"]

    data = result["data"]["Media"]

    # Data of all fields in returned json
    # pylint: disable=possibly-unused-variable
    idm = data.get("id")
    idmal = data.get("idMal")
    romaji = data["title"]["romaji"]
    english = data["title"]["english"]
    native = data["title"]["native"]
    formats = data.get("format")
    status = data.get("status")
    episodes = data.get("episodes")
    duration = data.get("duration")
    country = data.get("countryOfOrigin")
    c_flag = cflag(country)
    source = data.get("source")
    prqlsql = data.get("relations").get("edges")
    adult = data.get("isAdult")
    url = data.get("siteUrl")
    trailer_link = "N/A"
    isfav = data.get("isFavourite")
    fav = ", in Favourites" if isfav==True else ""
    user_data = ""
    in_ls = False
    in_ls_id = ""
    if auth==True:
        in_list = data.get("mediaListEntry")
        if in_list!=None:
            in_ls = True
            in_ls_id = in_list['id']
            in_ls_stts = in_list['status']
            in_ls_score = f" and scored {in_list['score']}" if in_list['score']!=0 else ""
            user_data = f"\n➤ **USER DATA:** `{in_ls_stts}{fav}{in_ls_score}`"
    if data["title"]["english"] is not None:
        name = f"""[{c_flag}]**{romaji}**
        __{english}__
        {native}"""
    else:
        name = f"""[{c_flag}]**{romaji}**
        {native}"""
    prql, prql_id, sql, sql_id = "", "None", "", "None"
    for i in prqlsql:
        if i["relationType"] == "PREQUEL":
            pname = (
                i["node"]["title"]["english"]
                if i["node"]["title"]["english"] is not None
                else i["node"]["title"]["romaji"]
            )
            prql += f"**PREQUEL:** `{pname}`\n"
            prql_id = i["node"]["id"]
            break
    for i in prqlsql:
        if i["relationType"] == "SEQUEL":
            sname = (
                i["node"]["title"]["english"]
                if i["node"]["title"]["english"] is not None
                else i["node"]["title"]["romaji"]
            )
            sql += f"**SEQUEL:** `{sname}`\n"
            sql_id = i["node"]["id"]
            break
    additional = f"{prql}{sql}"
    dura = (
        f"\n➤ **DURATION:** `{duration} min/ep`"
        if duration != None
        else ""
    )
    air_on = None
    if data["nextAiringEpisode"]:
        nextAir = data["nextAiringEpisode"]["timeUntilAiring"]
        air_on = make_it_rw(nextAir*1000)
        eps = data["nextAiringEpisode"]["episode"]
        ep_ = list(str(eps))
        x = ep_.pop()
        th = "th"
        if len(ep_) >= 1:
            if ep_.pop() != "1":
                th = pos_no(x)
        else:
            th = pos_no(x)
        air_on += f" | {eps}{th} eps"
    if air_on == None:
        eps_ = f"` | `{episodes} eps" if episodes != None else ""
        status_air = f"➤ **STATUS:** `{status}{eps_}`"
    else:
        status_air = f"➤ **STATUS:** `{status}`\n➤ **NEXT AIRING:** `{air_on}`"
    if data["trailer"] and data["trailer"]["site"] == "youtube":
        trailer_link = f"<a href='https://youtu.be/{data['trailer']['id']}'>Trailer</a>"
    title_img = f"https://img.anili.st/media/{idm}"
    try:
        finals_ = ANIME_TEMPLATE.format(**locals())
    except KeyError as kys:
        return [f"{kys}"]
    return title_img, finals_, [idm, in_ls, in_ls_id, isfav], prql_id, sql_id


async def get_anilist(qdb, page,auth: bool = False, user: int = None):
    vars_ = {"search": ANIME_DB[qdb], "page": page}
    result = await return_json_senpai(PAGE_QUERY, vars_, auth=auth, user=user)

    error = result.get("errors")
    if error:
        error_sts = error[0].get("message")
        return [f"{error_sts}"]

    data = result["data"]["Page"]["media"][0]
    # Data of all fields in returned json
    # pylint: disable=possibly-unused-variable
    idm = data.get("id")
    idmal = data.get("idMal")
    romaji = data["title"]["romaji"]
    english = data["title"]["english"]
    native = data["title"]["native"]
    formats = data.get("format")
    status = data.get("status")
    episodes = data.get("episodes")
    duration = data.get("duration")
    country = data.get("countryOfOrigin")
    c_flag = cflag(country)
    source = data.get("source")
    prqlsql = data.get("relations").get("edges")
    adult = data.get("isAdult")
    trailer_link = "N/A"
    isfav = data.get("isFavourite")
    fav = ", in Favourites" if isfav==True else ""
    in_ls = False
    in_ls_id = ""
    user_data = ""
    if auth==True:
        in_list = data.get("mediaListEntry")
        if in_list!=None:
            in_ls = True
            in_ls_id = in_list['id']
            in_ls_stts = in_list['status']
            in_ls_score = f" and scored {in_list['score']}" if in_list['score']!=0 else ""
            user_data = f"\n➤ **USER DATA:** `{in_ls_stts}{fav}{in_ls_score}`"
    if data["title"]["english"] is not None:
        name = f"[{c_flag}]**{english}** (`{native}`)"
    else:
        name = f"[{c_flag}]**{romaji}** (`{native}`)"
    prql, sql = "", ""
    for i in prqlsql:
        if i["relationType"] == "PREQUEL":
            pname = (
                i["node"]["title"]["english"]
                if i["node"]["title"]["english"] is not None
                else i["node"]["title"]["romaji"]
            )
            prql += f"**PREQUEL:** `{pname}`\n"
            break
    for i in prqlsql:
        if i["relationType"] == "SEQUEL":
            sname = (
                i["node"]["title"]["english"]
                if i["node"]["title"]["english"] is not None
                else i["node"]["title"]["romaji"]
            )
            sql += f"**SEQUEL:** `{sname}`\n"
            break
    additional = f"{prql}{sql}"
    additional.replace("-", "")
    dura = (
        f"\n➤ **DURATION:** `{duration} min/ep`"
        if duration != None
        else ""
    )
    air_on = None
    if data["nextAiringEpisode"]:
        nextAir = data["nextAiringEpisode"]["timeUntilAiring"]
        air_on = make_it_rw(nextAir*1000)
        eps = data["nextAiringEpisode"]["episode"]
        ep_ = list(str(eps))
        x = ep_.pop()
        th = "th"
        if len(ep_) >= 1:
            if ep_.pop() != "1":
                th = pos_no(x)
        else:
            th = pos_no(x)
        air_on += f" | {eps}{th} eps"
    if air_on == None:
        eps_ = f"` | `{episodes} eps" if episodes != None else ""
        status_air = f"➤ **STATUS:** `{status}{eps_}`"
    else:
        status_air = f"➤ **STATUS:** `{status}`\n➤ **NEXT AIRING:** `{air_on}`"
    if data["trailer"] and data["trailer"]["site"] == "youtube":
        trailer_link = f"<a href='https://youtu.be/{data['trailer']['id']}'>Trailer</a>"
    url = data.get("siteUrl")
    title_img = f"https://img.anili.st/media/{idm}"
    total = result["data"]["Page"]["pageInfo"]["total"]
    try:
        finals_ = ANIME_TEMPLATE.format(**locals())
    except KeyError as kys:
        return [f"{kys}"]
    return title_img, [finals_, total], [idm, in_ls, in_ls_id, isfav]


async def get_char(var, auth: bool = False, user: int = None):
    result = await return_json_senpai(CHARACTER_QUERY, var, auth=auth, user=user)

    error = result.get("errors")
    if error:
        error_sts = error[0].get("message")
        return [f"[{error_sts}]"]
    data = result["data"]["Page"]["characters"][0]
    # Character Data
    id_ = data["id"]
    name = data["name"]["full"]
    native = data["name"]["native"]
    img = data["image"]["large"]
    site_url = data["siteUrl"]
    isfav = data.get("isFavourite")
    cap_text = f"""
__{native}__
(`{name}`)
**ID:** {id_}

<a href='{site_url}'>Visit Website</a>"""
    total = result["data"]["Page"]["pageInfo"]["total"]
    return img, [cap_text, total], [id_, isfav]


async def get_manga(qdb, page, auth: bool = False, user: int = None):
    vars_ = {"search": MANGA_DB[qdb], "asHtml": True, "page": page}
    result = await return_json_senpai(MANGA_QUERY, vars_, auth=auth, user=user)

    error = result.get("errors")
    if error:
        error_sts = error[0].get("message")
        return [error_sts]

    data = result["data"]["Page"]["media"][0]

    # Data of all fields in returned json
    # pylint: disable=possibly-unused-variable
    idm = data.get("id")
    romaji = data["title"]["romaji"]
    english = data["title"]["english"]
    native = data["title"]["native"]
    status = data.get("status")
    synopsis = data.get("description")
    description = synopsis[:500]
    if len(synopsis) > 500:
        description += "..."
    volumes = data.get("volumes")
    chapters = data.get("chapters")
    score = data.get("averageScore")
    url = data.get("siteUrl")
    format_ = data.get("format")
    country = data.get("countryOfOrigin")
    source = data.get("source")
    c_flag = cflag(country)
    isfav = data.get("isFavourite")
    fav = ", in Favourites" if isfav==True else ""
    in_ls = False
    in_ls_id = ""
    user_data = ""
    if auth==True:
        in_list = data.get("mediaListEntry")
        if in_list!=None:
            in_ls = True
            in_ls_id = in_list['id']
            in_ls_stts = in_list['status']
            in_ls_score = f" and scored {in_list['score']}" if in_list['score']!=0 else ""
            user_data = f"➤ **USER DATA:** `{in_ls_stts}{fav}{in_ls_score}`\n\n"
    name = f"""[{c_flag}]**{romaji}**
        __{english}__
        {native}"""
    if english == None:
        name = f"""[{c_flag}]**{romaji}**
        {native}"""
    finals_ = f"{name}\n\n"
    finals_ += f"➤ **ID:** `{idm}`\n"
    finals_ += f"➤ **STATUS:** `{status}`\n"
    finals_ += f"➤ **VOLUMES:** `{volumes}`\n"
    finals_ += f"➤ **CHAPTERS:** `{chapters}`\n"
    finals_ += f"➤ **SCORE:** `{score}`\n"
    finals_ += f"➤ **FORMAT:** `{format_}`\n"
    finals_ += f"➤ **SOURCE:** `{source}`\n"
    finals_ += user_data
    finals_ += f"Description: `{description}`\n\n"
    pic = f"https://img.anili.st/media/{idm}"
    return pic, [finals_, result["data"]["Page"]["pageInfo"]["total"], url], [idm, in_ls, in_ls_id, isfav]


async def get_airing(vars_, auth: bool = False, user: int = None):
    result = await return_json_senpai(AIR_QUERY, vars_, auth=auth, user=user)
    error = result.get("errors")
    if error:
        error_sts = error[0].get("message")
        return f"[{error_sts}]"
    data = result["data"]["Media"]
    # Airing Details
    mid = data.get("id")
    romaji = data["title"]["romaji"]
    english = data["title"]["english"]
    status = data.get("status")
    country = data.get("countryOfOrigin")
    c_flag = cflag(country)
    coverImg = f"https://img.anili.st/media/{mid}"
    isfav = data.get("isFavourite")
    in_ls = False
    in_ls_id = ""
    user_data = ""
    if auth==True:
        in_list = data.get("mediaListEntry")
        if in_list!=None:
            in_ls = True
            in_ls_id = in_list['id']
            in_ls_stts = in_list['status']
            user_data = f"**USER DATA:** `{in_ls_stts}`\n"
    air_on = None
    if data["nextAiringEpisode"]:
        nextAir = data["nextAiringEpisode"]["timeUntilAiring"]
        episode = data["nextAiringEpisode"]["episode"]
        air_on = make_it_rw(nextAir*1000)
    title_ = english or romaji
    out = f"[{c_flag}] **{title_}**"
    out += f"\n\n**ID:** `{mid}`"
    out += f"\n**Status:** `{status}`\n"
    out += user_data
    if air_on:
        out += f"Airing Episode `{episode}th` in `{air_on}`"
    site = data["siteUrl"]
    return [coverImg, out], site, [mid, in_ls, in_ls_id, isfav]


async def tog_fav_(id_: int, media: str, user: int):
    vars_ = {"id": int(id_)}
    query = (
      ANIME_MUTATION if media=="ANIME" or media=="AIRING"
      else CHAR_MUTATION if media=="CHARACTER"
      else MANGA_MUTATION
    )
    k = await return_json_senpai(query=query, vars=vars_, auth=True, user=int(user))
    try:
        kek = k['data']['ToggleFavourite']
        return "ok"
    except KeyError:
        return "failed"


async def get_usr(vars_, req, user):
    query = USER_QRY if "user" in req else VIEWER_QRY
    k = await return_json_senpai(query=query, vars=vars_, auth=True if "flex" in req else False, user=int(user))
    data = k['data']['User' if "user" in req else 'Viewer']
    anime = data['statistics']['anime']
    manga = data['statistics']['manga']
    stats = f"""
**Anime Stats**:

Total Anime Watched: `{anime['count']}`
Total Episode Watched: `{anime['episodesWatched']}`
Total Time Spent: `{anime['minutesWatched']}`
Average Score: `{anime['meanScore']}`

**Manga Stats**:

Total Manga Read: `{manga['count']}`
Total Chapters Read: `{manga['chaptersRead']}`
Total Volumes Read: `{manga['volumesRead']}`
Average Score: `{manga['meanScore']}`
""" 
    btn = []
    if "flex" in req:
        btn.append([
            InlineKeyboardButton("Favourites", callback_data=f"myfavs_{data['id']}_{user}"),
            InlineKeyboardButton("Activity", callback_data=f"myacc_{data['id']}_{user}")
        ])
    btn.append([InlineKeyboardButton("Profile", url=str(data['siteUrl']))])
    return f'https://img.anili.st/user/{data["id"]}?a={time.time()}', stats, InlineKeyboardMarkup(btn)


async def ls_au_status(id, req, user, eid: int = None, status: str = None):
    vars_ = {"id": int(id), "status": status}
    if req=="lsus":
        vars_ = {"id": int(eid), "status": status}
    if req=="dlt":
        vars_ = {"id": int(eid)}
    k = await return_json_senpai(query=(
        ANILIST_MUTATION if req=="lsas"
        else ANILIST_MUTATION_UP if req=="lsus"
        else ANILIST_MUTATION_DEL), vars=vars_, auth=True, user=user)
    try:
        k['data']['SaveMediaListEntry'] if req=="lsas" else k['data']['UpdateMediaListEntries'] if req=="lsus" else k["data"]['DeleteMediaListEntry']
        return "ok"
    except KeyError:
        return "failed"


####       END        ####

#### Jikanpy part ####

async def get_scheduled(x: int = 9):
    day = day_(x if x!=9 else datetime.now().weekday())
    out = f"Scheduled animes for {day}\n\n"
    async with AioJikan() as session:
        sched_ls = (await session.schedule(day=str(day.lower()))).get(str(day.lower()))
        for i in sched_ls:
            out += f"• {i['title']}\n"
    return out, x if x!=9 else datetime.now().weekday()

####     END      ####

#### chiaki part ####

def get_wols(x: str):
    data = requests.get(f"https://chiaki.vercel.app/search?query={x}").json()
    ls = []
    for i in data:
        sls = [i['id'], i['value']]
        ls.append(sls)
    return ls


def get_wo(x: int):
    data = requests.get(f"https://chiaki.vercel.app/get?group_id={x}").json()
    msg = "Watch order for the given query is:\n\n"
    for i in data:
        msg += f"{i['index']}. `{i['name']}`\n"
    return msg

####     END     ####