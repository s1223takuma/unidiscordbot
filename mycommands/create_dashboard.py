import discord
from discord.ext import commands
import datetime
import json
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

    await ctx.send(embed=embed)
