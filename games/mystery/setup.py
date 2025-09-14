from games.mystery.views import JoinView
from games.mystery.status import gamestatus
import asyncio
import discord


async def setup(ctx):
    if ctx.guild.id in gamestatus:
        await ctx.send("すでにゲームが進行中です。")
        return
    gamestatus[ctx.guild.id] = {
        "players": [],
        "criminal":[],
        "status": "募集"
    }
    view = JoinView(ctx)
    await ctx.send(
        "ミステリーゲームを開始します！\n30秒間参加者を募集します。\n下のボタンから参加してください。",
        view=view
    )
    await asyncio.sleep(30)
    if len(gamestatus[ctx.guild.id]["players"]) < 3:
        await ctx.send("参加者が3人未満のため、ゲームを中止します。")
        del gamestatus[ctx.guild.id]
        return