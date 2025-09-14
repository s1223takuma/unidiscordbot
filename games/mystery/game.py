import discord
import asyncio
import json
import os

from games.mystery.status import gamestatus
from games.mystery.cleanup import cleanup_channels,cleanup_category

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
    await asyncio.sleep(5)
    await cleanup_category(ctx)
    await cleanup_channels(ctx)