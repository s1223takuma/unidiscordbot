import discord
from discord.ext import commands
import os
import json
import bot_setup as bs

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
invite = None
guild_to_kana = {}
voice_setting = {}

# 起動時に動作する処理
@client.event
async def on_ready():
    print('ログインしました')
    word_path = "data/guild_to_kana.json"
    if os.path.exists(word_path):
        with open(word_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bs.guild_to_kana = {int(gid): word for gid, word in data.items()}
    voice_path = "data/voice_setting.json"
    if os.path.exists(voice_path):
        with open(voice_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bs.voice_setting = {int(gid): word for gid, word in data.items()}
    await client.tree.sync()