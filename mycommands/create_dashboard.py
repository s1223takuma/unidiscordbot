import discord
from discord.ext import commands
import datetime
import json
import os

async def dashboard(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title="サーバーダッシュボード",
        description=f"{guild.name} の概要です",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="👥 メンバー数", value=f"{guild.member_count}人", inline=True)
    embed.add_field(name="💬 テキストチャンネル数", value=str(len(guild.text_channels)), inline=True)
    embed.add_field(name="🔊 ボイスチャンネル数", value=str(len(guild.voice_channels)), inline=True)
    embed.set_footer(text=f"最終更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # JSONファイルの読み込み
    data_path = "data/dashboard.json"
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    # すでにギルドIDが登録されていたら何もしない
    if str(guild.id) in data:
        await ctx.send("このサーバーにはすでにダッシュボードが登録されています。")
        return

    # 登録されていない場合のみ新しく作成
    message = await ctx.send(embed=embed)
    data[str(guild.id)] = message.id

    # JSONファイルに保存
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    await ctx.send("✅ ダッシュボードを作成しました。")
