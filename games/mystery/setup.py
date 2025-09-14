from games.mystery.views import JoinView
from games.mystery.status import gamestatus
import asyncio
import discord
import random

def selectcriminal(status):
    if len(status["criminals"]) == 1:
        status["criminal"] = status["criminals"][0]
        del status["criminals"]
        print(status)
        return status
    elif len(status["criminals"]) == 0:
        criminal = random.choice(status["players"])
        del status["criminals"]
        status["criminal"] = criminal
        print(status)
        return status
    else:
        criminal = random.choice(status["criminals"])
        del status["criminals"]
        status["criminal"] = criminal
        print(status)
        return status

async def setup(ctx):
    if ctx.guild.id in gamestatus:
        await ctx.send("すでにゲームが進行中です。")
        return
    gamestatus[ctx.guild.id] = {
        "players": [],
        "criminals":[],
        "criminal":None,
        "status": "募集",
        "player_channel":{},
        "category":None
    }
    view = JoinView(ctx)
    await ctx.send(
        "ミステリーゲームを開始します！\n30秒間参加者を募集します。\n下のボタンから参加してください。",
        view=view
    )
    await asyncio.sleep(10)
    gamestatus[ctx.guild.id]["status"] = "開始"
    gamestatus[ctx.guild.id] = selectcriminal(gamestatus[ctx.guild.id])
    category = await ctx.guild.create_category("ミステリー")
    gamestatus[ctx.guild.id]["category"] = category
    for player in gamestatus[ctx.guild.id]["players"]:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            player: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await category.create_text_channel(f"{player.name}-chat", overwrites=overwrites)
        if player == gamestatus[ctx.guild.id]["criminal"]:
            await channel.send(f"{player.mention}あなたは犯人です。事件を起こしてください")
        else:
            await channel.send(f"{player.mention}あなたは事件に巻き込まれました。事件を解決に導いてください。")
        gamestatus[ctx.guild.id]["player_channel"][player] = channel
    print(gamestatus[ctx.guild.id]["criminal"])
    await asyncio.sleep(10)
    await cleanup_channels(ctx)


async def cleanup_channels(ctx):
    guild_id = ctx.guild.id
    category = gamestatus[guild_id].get("category")
    if category:
        for channel in category.channels:
            await channel.delete()
        await category.delete()