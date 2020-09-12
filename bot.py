import asyncio
from datetime import datetime

from discord.ext import commands, tasks

from params import TARGET_CHANNEL_ID, TOKEN
from fixtures import get_active_fixtures


bot = commands.Bot('!')

POST_TIME = datetime.strptime('10:00', '%H:%M')

@tasks.loop(hours=24)
async def post_fixtures():
    message_channel = bot.get_channel(TARGET_CHANNEL_ID)
    print(f"Got channel {message_channel}")
    current_matches = get_active_fixtures()
    if current_matches:
        text = (
            ':soccer: :soccer: :soccer:'
            + '\n__**Today\'s Fixtures**__\n' 
            + '\n'.join(current_matches)
            + '\n:soccer: :soccer: :soccer:'
        )

        await message_channel.send(text)

@post_fixtures.before_loop
async def time_wait():
    await bot.wait_until_ready()

    wait_time = (POST_TIME - datetime.now()).total_seconds() % (24*60*60)
    print(f'Waiting {wait_time} seconds for scheduled posts')
    await asyncio.sleep(wait_time)
    print('Ready for scheduled posting!')


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if message.content.startswith('$hello'):
#         await message.channel.send(f'Hello {message.author.mention}')
    
#     if message.content.startswith('$teams'):
#         await message.channel.send(
#             f'{message.author.mention} - available teams are'
#         )

post_fixtures.start()
bot.run(TOKEN)
