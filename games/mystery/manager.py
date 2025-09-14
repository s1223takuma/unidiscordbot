import discord
import asyncio

from games.mystery.status import gamestatus
from games.mystery.cleanup import cleanup_channels,cleanup_category

async def start_game(ctx):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"玄関", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"廊下", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"居間", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"寝室", overwrites=overwrites)
    for i,player in enumerate(gamestatus[ctx.guild.id]["players"], start=1):
        if i <= 9:
            await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"客室20{i}号室", overwrites=overwrites)
        else:
            await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"客室2{i}号室", overwrites=overwrites)
    await asyncio.sleep(10)
    await cleanup_category(ctx)
    await cleanup_channels(ctx)