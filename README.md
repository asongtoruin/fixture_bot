# fixture_bot
A discord bot for posting football fixtures.

This isn't particularly elegant in its setup, but it could fairly easily be 
adapted for use in other servers. At present, I've got it running on a Raspberry
Pi that runs a twitter bot, but this shouldn't be too processor / 
memory-intensive so hopefully the two can coexist.

## Sources
The bot uses data from [API-Football](https://www.api-football.com/) via
[RapidAPI](https://rapidapi.com/api-sports/api/api-football) as the 100 free 
calls per day is enough for my use case.

## Requirements
The bot, unsurprisingly, requires `discord.py`. That should be it in terms of 
third-party Python modules.

## Setting up parameters
### Functional requirements
The bot relies on a `params.py` file within the `code` directory that the `.gitignore` deliberately excludes
as these values should be kept secret. The file should look as follows (this
example here uses dummy values):

```python
# Discord params
TARGET_CHANNEL_ID = 1234567
TOKEN = 'xxx'

# API params
HEADERS = {
    'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
    'x-rapidapi-key': 'xxx'
}
```

The Discord parameters are detailed well in the 
[discord.py docs](https://discordpy.readthedocs.io/en/latest/), whereas the
API parameters should come from setting up an application with RapidAPI.

### Posting time
The default set-up is to post at 8am every day. This is set right at the top
of `bot.py`, so it should be easy to tweak if necessary.

### Teams to track
The tracked teams are defined as a class attribute of the `Fixture` class. 
This... is a bit messy, in all honesty, but I just wanted to get something up 
and running. `Fixture.BADGE_LOOKUPS` provides an equivalence between team IDs 
used by API-Football and the custom emoji shortcodes used in the Discord server
I run this bot in. You could alternatively set this to, say, format the teams 
you're looking up as bold.

The easiest way I found to get the IDs for teams was to export all leagues for 
country from the relevant API endpoint to JSON, then do the same thing for 
relevant leagues.
