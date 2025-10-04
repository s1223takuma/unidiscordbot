import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import bot_setup as bs

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
tree = client.tree
invite = None
guild_to_kana = {}
voice_setting = {}
GUILD_ID = 1190628761033515038  # テストしたいサーバーID
guild = discord.Object(id=GUILD_ID)

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
    try:

        synced = await client.tree.sync(guild=guild)
        print(f"✅ スラッシュコマンド同期成功: {len(synced)} 件")
        print(synced)
    except Exception as e:
        print(f"❌ スラッシュコマンド同期エラー: {e}")