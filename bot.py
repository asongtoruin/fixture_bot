import asyncio
from datetime import datetime
from io import BytesIO

from discord import File
from discord.ext import commands, tasks

from params import TARGET_CHANNEL_ID, TOKEN, FONT_PATH
from fixtures import draw_competition_fixtures, Fixture


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('fixturebot.', ), 
    help_command=None
)


help_text = f'''IT'S THE EUROPEAN CHAMPIONSHIPS. GET EXCITED.
'''

POST_TIME = datetime.strptime('08:00', '%H:%M')

@tasks.loop(hours=24)
async def post_fixtures():
    message_channel = bot.get_channel(TARGET_CHANNEL_ID)
    print(f"Got channel {message_channel} @{datetime.now()}")
    for img in draw_competition_fixtures(font_path=FONT_PATH, league_id=403):
        arr = BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)

        await message_channel.send(file=File(arr, filename='card.png'))


@post_fixtures.before_loop
async def time_wait():
    await bot.wait_until_ready()

    wait_time = (POST_TIME - datetime.now()).total_seconds() % (24*60*60)
    print(f'Waiting {wait_time} seconds for scheduled posts')
    await asyncio.sleep(wait_time)
    print('Ready for scheduled posting!')


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

post_fixtures.start()
bot.run(TOKEN)
