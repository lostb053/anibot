Telegram Bot Repo Capable of fetching the following Info via Anilist API inspired from [AniFluid](https://t.me/anifluidbot) and [Nepgear](https://t.me/nepgearbot)
* Anime
* Airing
* Manga
* Character
* Studio
* Scheduled
* Top animes
* Favourites
* Anilist Activity
* Update Anilist entry using bot
* Popular, trending and upcoming animes for a season
* Random anime quotes
* Anime fillers from [animefillerslist](https://www.animefillerlist.com)
* Anime Airing notifications from [LiveChart](https://livechart.me)
* Anime Headlines from [LiveChart](https://livechart.me)
* Anime Headlines from [MyAnimeList](https://myanimelist.net)
* Anime release notifications for [Crunchyroll](https://crunchyroll.com)
* Anime release notifications for [Subsplease](https://subsplease.org)
* Anime Reverse Search Powered by [tracemoepy](https://github.com/dragsama/tracemoepy)
* Watch Order from [Chiaki](https://chiaki.site/) using [web api](https://chiaki.vercel.app)
* Supports custom UI to be set for all results shown by /anime and /anilist in a group
<h3>Also can add to grps and enable sfw lock to prevent members from looking up hentai and 18+ rated stuff<br>Also includes command disabling<br><b>With new update you can now change UI for anime/anilist/manga results in your group</b></h3>

<img src='https://img.shields.io/github/repo-size/lostb053/anibot?style=flat-square'>  <img src='https://img.shields.io/github/license/lostb053/anibot?style=flat-square'>  <img src='https://img.shields.io/github/languages/top/lostb053/anibot?style=flat-square'>  [![CodeFactor](https://www.codefactor.io/repository/github/lostb053/anibot/badge)](https://www.codefactor.io/repository/github/lostb053/anibot)

## Requirements
* Python 3.10.1
* Telegram [API Keys](https://my.telegram.org/apps)
* Bot Token from [BotFather](https://t.me/botfather)
* MongoDB [Database URL](https://cloud.mongodb.com/)
* Anilist [Client Keys](https://anilist.co/settings/developer)
* For smooth authentication process deploy [this](https://github.com/lostb053/anilist_oauth_webserver) webserver (well a noob code server hope this helps)


## Available Cmds
```
 /help - Get interactive and detailed help on bot cmds
 /ping - Ping the bot to check if it's online
 /start - To start bot in group (will be logged) or pm (user if not OWNER will be logged)
 /anime - Fetches info on single anime (includes buttons to look up for prequels and sequels)
 /anilist - Fetches info on multiple possible animes related to query
 /character - Fetches info on multiple possible characters related to query
 /manga - Fetches info on multiple possible mangas related to query
 /airing - Fetches info on airing data for anime
 /studio - Fetches info on multiple possible studios related to query
 /flex - Fetches anilist info of an authorised user
 /user - Fetches anilist info as per query
 /schedule - Fetches scheduled animes
 /auth - Fetches info on how to authorize anilist account
 /browse - get popular, trending or upcoming animes
 /quote - get random quotes
 /logout - removes authorization
 /settings - To toggle nsfw lock and airing notifications and other settings in groups
 /top - to retrieve top animes for a genre or tag
 /reverse - Reverse search powered by tracemoepy
 /watch - Fetches watch order for anime series
 /feedback - contact bot owner or main support grp at @hanabi_support
 /me or /activity - Get Anilist recent activity
 /fillers - To get list of anime fillers
 /disable - To disable a command in group
 /enable - To enable a command in group
 /disabled - To list disabled commands in a group
 /favourites - Get Anilist favourites
 /gettags - Get list of available Tags
 /getgenres - Get list of available Genres
 /connect - Helps connect Public channel, to use bot as Channel in group
```


## Owner/Sudo Cmds
```
 /eval - Runs python code (code must start right after cmd like "/eval print('UwU')")
 /term - Runs the code in terminal
 /stats - Gibs data on bot such as no. of grps/users and ping
 /dbcleanup - Cleans useless entries in database
```


## How to host
<p align="center"><a href="https://heroku.com/deploy?template=https://github.com/lostb053/anibot"> <img src="https://img.shields.io/badge/Deploy%20To%20Heroku-blue?style=for-the-badge&logo=heroku" width="220" height="38.45"/></a></p>


## Credits
* AniList Api ([GitHub](https://github.com/AniList/ApiV2-GraphQL-Docs))
* jikanpy ([GitHub](https://github.com/abhinavk99/jikanpy))
* [@NotThatMF](https://t.me/notthatmf) for [chiaki fast api](https://chiaki.vercel.app/) and for creating base for this bot to work
* [@DragSama](https://t.me/dragsama) on telegram for [tracemoepy](https://github.com/dragsama/tracemoepy) & [AniFluid-Base](https://github.com/DragSama/AniFluid-Base)
* [@DeletedUser420](https://t.me/deleteduser420) on telegram for [USERGE-X](https://github.com/code-rgb/USERGE-X) & [Userge-Plugins](https://github.com/code-rgb/Userge-Plugins)
* [Phyco-Ninja](https://github.com/Phyco-Ninja) as author of anilist plugin in Userge-Plugins repo
* [@blank_x](https://t.me/blank_x) on tg for [sukuinote](https://gitlab.com/blank-x/sukuinote)


For improvements PR or contact [@LostB053](https://t.me/lostb053) or [@hanabi_support](https://t.me/hanabi_support)<br>
Can ask for support too but don't expect much (since i myself am learning yet)<br>
<br>
<h4>Note: I dropped SauceNAO stuff cuz i couldnt represent it in some good looking manner<br>
I would be grateful if anybody can help me parse results and organize them like <a href='https://t.me/reverseSearchBot'>@reverseSearchBot</a></h4>Something nearby but good looking would suffice too
