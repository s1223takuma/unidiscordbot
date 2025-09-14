import discord
import asyncio
import json
import os

from games.mystery.status import gamestatus
from games.mystery.cleanup import cleanup_channels,cleanup_category
from games.mystery.manager import select_event

async def start_game(ctx):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"ロビー", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"廊下", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"温泉", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"食堂", overwrites=overwrites)
    for i,player in enumerate(gamestatus[ctx.guild.id]["players"], start=1):
        if i <= 9:
            await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"客室20{i}号室", overwrites=overwrites)
        else:
            await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"客室2{i}号室", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["admin_channel"].send("ゲームを開始します。")
    gamestatus[ctx.guild.id]["status"] = "事件発生前"
    await introduction(ctx)

async def introduction(ctx):
    with open("games/mystery/story/introduction.json", "r", encoding="utf-8") as f:
        story_data = json.load(f)
    await gamestatus[ctx.guild.id]["admin_channel"].send(f"## {story_data['title']}")
    await gamestatus[ctx.guild.id]["admin_channel"].send(f"{story_data['description']}")
    first_message = await select_event(ctx,0)
    for player in gamestatus[ctx.guild.id]["players"]:
        await gamestatus[ctx.guild.id]["player_channel"][player.id].send(first_message["text"])
    await asyncio.sleep(5)
    await cleanup_category(ctx)
    await cleanup_channels(ctx)
    del gamestatus[ctx.guild.id]