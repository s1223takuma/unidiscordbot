from games.jinro.status import gamestatus
from games.jinro.views import JoinView
import discord
import asyncio
from games.jinro.manager import start_game

async def setup(ctx):
    if ctx.guild.id in gamestatus:
        await ctx.send("すでにゲームが進行中です。")
        return
    gamestatus[ctx.guild.id] = {
        "players": [],
        "roles": {},
        "status": "募集",
        "襲撃_target": [],
        "守護_target": [],
        "vote": {},
        "player_channel": {},
        "dead_players": [],
        "category": None,
        "heven_channel": None,
        "heaven_voice_channel": None,
        "turn": 1,
        "wolf_list": []
    }
    view = JoinView(ctx)
    await ctx.send(
        "人狼ゲームを開始します！\n30秒間参加者を募集します。\n下のボタンから参加してください。",
        view=view
    )
    await asyncio.sleep(30)
    if len(gamestatus[ctx.guild.id]["players"]) < 3:
        await ctx.send("参加者が3人未満のため、ゲームを中止します。")
        del gamestatus[ctx.guild.id]
        return
    await ctx.send(f"ゲームを開始します！役職を配布します。")
    category = await ctx.guild.create_category("人狼")
    gamestatus[ctx.guild.id]["category"] = category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
    heaven = await category.create_text_channel("天界", overwrites=overwrites)
    heaven_voice = await category.create_voice_channel("天界", user_limit=99, overwrites=overwrites)
    gamestatus[ctx.guild.id]["heven_channel"] = heaven
    gamestatus[ctx.guild.id]["heaven_voice_channel"] = heaven_voice
    for player in gamestatus[ctx.guild.id]["players"]:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            player: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await category.create_text_channel(f"{player.name}-chat", overwrites=overwrites)
        gamestatus[ctx.guild.id]["player_channel"][player] = channel
    await start_game(ctx)

async def cleanup_channels(ctx):
    guild_id = ctx.guild.id
    category = gamestatus[guild_id].get("category")
    if category:
        for channel in category.channels:
            await channel.delete()
        await category.delete()