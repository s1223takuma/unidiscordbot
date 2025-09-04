import discord
from discord.ext import commands
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
invite = None

# 起動時に動作する処理
@client.event
async def on_ready():
    print('ログインしました')
    await client.tree.sync()