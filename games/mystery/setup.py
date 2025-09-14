import asyncio
import discord
import random

from games.mystery.views import JoinView
from games.mystery.status import gamestatus
from games.mystery.manager import start_game
from games.mystery.cleanup import cleanup_category


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
        "admin_channel":None,
        "player_channel":{},
        "category":None,
        "world_category":None,
        "status": "募集",
    }
    view = JoinView(ctx)
    await ctx.send(
        "ミステリーゲームを開始します！\n30秒間参加者を募集します。\n下のボタンから参加してください。",
        view=view
    )
    await asyncio.sleep(5)
    gamestatus[ctx.guild.id]["status"] = "開始"
    gamestatus[ctx.guild.id] = selectcriminal(gamestatus[ctx.guild.id])
    world_category = await ctx.guild.create_category("フィールドチャンネル")
    await world_category.edit(position=0)
    gamestatus[ctx.guild.id]["world_category"] = world_category
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    for player in gamestatus[ctx.guild.id]["players"]:
        overwrites[player] = discord.PermissionOverwrite(read_messages=True)
    admin = await world_category.create_text_channel("admin_channel",overwrites=overwrites)
    gamestatus[ctx.guild.id]["admin_channel"] = admin
    category = await ctx.guild.create_category("ミステリー(個人用チャンネル)")
    await category.edit(position=1)
    gamestatus[ctx.guild.id]["category"] = category
    for player in gamestatus[ctx.guild.id]["players"]:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            player: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await category.create_text_channel(f"{player.name}-chat", overwrites=overwrites)
        if player == gamestatus[ctx.guild.id]["criminal"]:
            await channel.send(f"{player.mention}あなたのロールは犯人です。\n開始から5ターン以内の任意のタイミングで最初の事件を起こしてください。")
        else:
            await channel.send(f"{player.mention}あなたは旅館に来たお客さんです。ゆっくり羽を伸ばしてください。")
        gamestatus[ctx.guild.id]["player_channel"][player.id] = channel
    await start_game(ctx)