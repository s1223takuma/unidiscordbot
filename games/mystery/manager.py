import discord
import json

from games.mystery.status import gamestatus



async def select_event(ctx,event_id):
    with open("games/mystery/story/introduction.json", "r", encoding="utf-8") as f:
        story_data = json.load(f)
    event = story_data['events'][event_id]
    return event

async def move_user(ctx, player, channelname):
    category = gamestatus[ctx.guild.id]["world_category"]
    target_channel = None
    for channel in category.channels:
        if channel.name == channelname and isinstance(channel, discord.VoiceChannel):
            target_channel = channel
            break
    if not target_channel:
        await ctx.send(f"{channelname} が見つかりませんでした。")
        return
    if player.voice and player.voice.channel:
        try:
            await player.move_to(target_channel)
        except discord.errors.HTTPException:
            await ctx.send(f"{player.display_name} を {channelname} に移動できませんでした。")
    else:
        await ctx.send(f"{player.display_name} さん、まずボイスチャンネルに入ってください。")
