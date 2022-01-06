import os
from pyrogram import Client
from aiohttp import ClientSession

TRIGGERS = os.environ.get("TRIGGERS", "/ !").split()
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_NAME = os.environ.get("BOT_NAME")
DB_URL = os.environ.get("DATABASE_URL")
ANILIST_CLIENT = os.environ.get("ANILIST_CLIENT")
ANILIST_SECRET = os.environ.get("ANILIST_SECRET")
ANILIST_REDIRECT_URL = os.environ.get("ANILIST_REDIRECT_URL", "https://anilist.co/api/v2/oauth/pin")
API_ID = int(os.environ.get("API_ID"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
OWNER = list(filter(lambda x: x, map(int, os.environ.get("OWNER_ID", "1005170481 804248372 1993696756").split())))  ## sudos can be included

DOWN_PATH = "anibot/downloads/"
HELP_DICT = dict()

session = ClientSession()
plugins = dict(root="anibot/plugins")
anibot = Client("anibot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, plugins=plugins)

has_user: bool = False
if os.environ.get('USER_SESSION'):
    has_user: bool = True
    user = Client(os.environ.get('USER_SESSION'), api_id=API_ID, api_hash=API_HASH)

HELP_DICT['Group'] = '''
Group based commands:

/settings - Toggle stuff like whether to allow 18+ stuff in group or whether to notify about aired animes, etc and change UI

/disable - Disable use of a cmd in the group (Disable multiple cmds by adding space between them)
`/disable anime anilist me user`

/enable - Enable use of a cmd in the group (Enable multiple cmds by adding space between them)
`/enable anime anilist me user`

/disabled - List out disabled cmds
'''

HELP_DICT["Additional"] = """Use /reverse cmd to get reverse search via tracemoepy API
__Note: This works best on uncropped anime pic,
when used on cropped media, you may get result but it might not be too reliable__

Use /schedule cmd to get scheduled animes based on weekdays

Use /watch cmd to get watch order of searched anime

Use /fillers cmd to get a list of fillers for an anime

Use /quote cmd to get a random quote
"""

HELP_DICT["Anilist"] = """
Below is the list of basic anilist cmds for info on anime, character, manga, etc.

/anime - Use this cmd to get info on specific anime using keywords (anime name) or Anilist ID
(Can lookup info on sequels and prequels)

/anilist - Use this cmd to choose between multiple animes with similar names related to searched query
(Doesn't includes buttons for prequel and sequel)

/character - Use this cmd to get info on character

/manga - Use this cmd to get info on manga

/airing - Use this cmd to get info on airing status of anime

/top - Use this cmd to lookup top animes of a genre/tag or from all animes
(To get a list of available tags or genres send /gettags or /getgenres
'/gettags nsfw' for nsfw tags)

/user - Use this cmd to get info on an anilist user

/browse - Use this cmd to get updates about latest animes
"""

HELP_DICT["Oauth"] = """
This includes advanced anilist features

Use /auth or !auth cmd to get details on how to authorize your Anilist account with bot
Authorising yourself unlocks advanced features of bot like:
- adding anime/character/manga to favourites
- viewing your anilist data related to anime/manga in your searches which includes score, status, and favourites
- unlock /flex, /me, /activity and /favourites commands
- adding/updating anilist entry like completed or plan to watch/read
- deleting anilist entry

Use /flex or !flex cmd to get your anilist stats

Use /logout or !logout cmd to disconnect your Anilist account

Use /me or !me cmd to get your anilist recent activity
Can also use /activity or !activity

Use /favourites or !favourites cmd to get your anilist favourites
"""
