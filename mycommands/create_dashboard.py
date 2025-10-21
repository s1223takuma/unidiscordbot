import discord
from discord.ext import commands
import datetime
import json
import os

async def dashboard(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title="PDFリンクまとめダッシュボード",
        description=f"{guild.name} に送信されたPDF一覧です",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    data_path = "data/dashboard.json"
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}
    if str(guild.id) in data:
        await ctx.send("このサーバーにはすでにダッシュボードが登録されています。")
        return
    category = await ctx.guild.create_category("PDF一覧")
    message = await ctx.send(embed=embed)
    data[str(guild.id)] = {"dashboard_ID":message.id,"category_ID":category.id}
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
