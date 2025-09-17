import discord
import asyncio
import json

from games.mystery.status import gamestatus,location_status
from games.mystery.cleanup import cleanup_channels,cleanup_category
from games.mystery.manager import select_event
from games.mystery.views import SelectView

async def start_game(ctx):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    }
    await gamestatus[ctx.guild.id]["world_category"].create_text_channel(f"廊下", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_text_channel(f"温泉", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_text_channel(f"食堂", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"ロビー", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"廊下", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"温泉", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"食堂", overwrites=overwrites)
    await gamestatus[ctx.guild.id]["world_category"].create_text_channel(f"ロビー", overwrites=overwrites)
    for i,player in enumerate(gamestatus[ctx.guild.id]["players"], start=1):
        if i <= 9:
            guest_room = await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"客室20{i}号室", overwrites=overwrites)
            guest_room = await gamestatus[ctx.guild.id]["world_category"].create_text_channel(f"客室20{i}号室", overwrites=overwrites)
        else:
            guest_room = await gamestatus[ctx.guild.id]["world_category"].create_voice_channel(f"客室2{i}号室", overwrites=overwrites)
            guest_room = await gamestatus[ctx.guild.id]["world_category"].create_text_channel(f"客室2{i}号室", overwrites=overwrites)
        gamestatus[ctx.guild.id]["player_guestroom"][player.id] = guest_room.name
    await gamestatus[ctx.guild.id]["admin_channel"].send("ゲームを開始します。")
    gamestatus[ctx.guild.id]["status"] = "事件発生前"
    await asyncio.sleep(5)
    await introduction(ctx)

async def introduction(ctx):
    with open("games/mystery/story/introduction.json", "r", encoding="utf-8") as f:
        story_data = json.load(f)
    await gamestatus[ctx.guild.id]["admin_channel"].send(f"## {story_data['title']}")
    await gamestatus[ctx.guild.id]["admin_channel"].send(f"{story_data['description']}")
    first_event = await select_event(ctx,0)
    for player in gamestatus[ctx.guild.id]["players"]:
        view = SelectView(ctx,first_event,player)
        await gamestatus[ctx.guild.id]["player_channel"][player.id].send(first_event["text"],view=view)
    await asyncio.sleep(5)
    print(location_status)