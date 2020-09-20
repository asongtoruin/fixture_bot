import asyncio
from datetime import datetime

from discord.ext import commands, tasks

from params import TARGET_CHANNEL_ID, TOKEN
from fixtures import get_active_fixtures, Fixture


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('fixturebot.', ), 
    help_command=None
)


help_text = f'''I post fixtures for predefined teams at 8am each day.

__**Teams**__
Fixtures are shown alphabetically for the teams I'm tracking. Those teams are:
{', '.join(Fixture.BADGE_LOOKUPS.values())}
If you want more teams adding, that's very possible :robot:

__**Form**__
Form is shown by default for the past 5 matches for a team, from most to least 
recent. Form is shown across all competitions, and does not include penalties 
(so, if a match goes to penalties it's recorded as a draw).

The following icons are used:
:blue_circle: - win
:red_circle: - loss
:yellow_circle: - draw
:black_circle: - match postponed / cancelled / other.
'''

POST_TIME = datetime.strptime('08:00', '%H:%M')

@tasks.loop(hours=24)
async def post_fixtures():
    message_channel = bot.get_channel(TARGET_CHANNEL_ID)
    print(f"Got channel {message_channel} @{datetime.now()}")
    current_matches = get_active_fixtures()
    if current_matches:
        print('Got fixtures, posting...')
        text = (
            ':soccer: :soccer: :soccer:'
            + '\n__**Today\'s Fixtures**__\n' 
            + '\n'.join(current_matches)
            + '\n:soccer: :soccer: :soccer:'
        )

        await message_channel.send(text)
    else:
        print('No matches today!')


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
