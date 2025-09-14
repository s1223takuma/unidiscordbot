from games.mystery.status import gamestatus

async def cleanup_category(ctx):
    guild_id = ctx.guild.id
    category = gamestatus[guild_id].get("category")
    if category:
        for channel in category.channels:
            await channel.delete()
        await category.delete()

# async def cleanup_channels(ctx):
#     guild_id = ctx.guild.id
#     category = gamestatus[guild_id].get("world_category")
#     if category:
#         for channel in category.channels:
#             if channel.name != "admin_channel":
#                 await channel.delete()

async def cleanup_channels(ctx):
    guild_id = ctx.guild.id
    category = gamestatus[guild_id].get("world_category")
    if category:
        for channel in category.channels:
            await channel.delete()
        await category.delete()