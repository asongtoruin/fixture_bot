import asyncio
import logging
from datetime import datetime
from io import BytesIO
from os import getenv

from discord import File, Intents
from discord.ext import commands, tasks
from dotenv import load_dotenv

from accumulate_daily_fixtures import accumulate_daily_fixtures
from src.drawing_tools.utilities import font_from_url

logger = logging.getLogger("discord")

load_dotenv()

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('fixturebot.', ), 
    intents=intents,
    help_command=None
)


help_text = '''I post fixtures for predefined teams at 8am each day.

__**Teams**__
Fixtures are shown alphabetically for the teams I'm tracking. If you want more 
teams adding, that's very possible :robot:

__**Form**__
Form is shown by default for the past 5 matches for a team, in chronological 
order. Form is shown across all competitions, and does not (might not?) include 
penalties (so, if a match goes to penalties it's recorded as a draw).

The following colours are used:
:blue_circle: - win
:red_circle: - loss
:yellow_circle: - draw
:black_circle: - match postponed / cancelled / other.
'''

POST_TIME = datetime.strptime('08:00', '%H:%M')
TARGET_CHANNEL_ID = int(getenv("TARGET_CHANNEL_ID"))
TOKEN = getenv("TOKEN")
FONT = font_from_url("https://github.com/google/fonts/raw/refs/heads/main/ofl/comfortaa/Comfortaa%5Bwght%5D.ttf")


@tasks.loop(hours=24)
async def post_fixtures():
    message_channel = bot.get_channel(TARGET_CHANNEL_ID)
    logger.info(f"Got channel {message_channel} @{datetime.now()}")
    for card in accumulate_daily_fixtures():
        try:
            img = card.draw(font_path=FONT)

            # Grab the timestamp so we can post relative times with the images (love u Matt)
            timestamp = card.fixture.fixture.localise_date().timestamp()

            text = f"(<t:{timestamp:.0f}:R>)"

            arr = BytesIO()
            img.save(arr, format='PNG')
            arr.seek(0)

            await message_channel.send(text, file=File(arr, filename='card.png'))
        except Exception:
            await message_channel.send("Oops, there was an error here.")


@post_fixtures.before_loop
async def time_wait():
    await bot.wait_until_ready()

    wait_time = (POST_TIME - datetime.now()).total_seconds() % (24*60*60)
    logger.info(f'Waiting {wait_time} seconds for scheduled posts')
    await asyncio.sleep(wait_time)
    logger.info('Ready for scheduled posting!')


@bot.command()
async def help(ctx):
    if ctx.author == bot.user:
        return

    await ctx.send(
        f'Hello {ctx.author.mention}! Here is some info on how I work:\n' + help_text
    )


@bot.command()
async def beep(ctx):
    if ctx.author == bot.user:
        return

    await ctx.send(
        f'{ctx.author.mention} boop :robot:'
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            f'{ctx.author.mention} I don\'t know how to respond to that :robot:'
        )

@bot.event
async def on_ready():
    logger.info(f'We have logged in as {bot.user}')

    post_fixtures.start()

bot.run(TOKEN)
