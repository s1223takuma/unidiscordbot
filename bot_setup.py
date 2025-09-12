import discord
from discord.ext import commands
import os
import json
import bot_setup as bs

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
invite = None
guild_to_kana = {}

# 起動時に動作する処理
@client.event
async def on_ready():
    print('ログインしました')
    path = "data/guild_to_kana.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bs.guild_to_kana = {int(gid): word for gid, word in data.items()}
    print(guild_to_kana)
    await client.tree.sync()