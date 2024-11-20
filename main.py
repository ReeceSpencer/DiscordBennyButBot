import discord
import random
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.hybrid_command(name='ping')
async def ping(context):
    await context.send('pong')

@bot.hybrid_command(name='dice')
async def dice(context, arg=6):
    await context.send(random.randint(1, arg))

#bot.run(DISCORD_API_TOKEN)