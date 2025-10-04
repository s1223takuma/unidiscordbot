import discord

async def delete_category(ctx, name):
    category = discord.utils.get(ctx.guild.categories, name=name) if name else None
    if not category:
        await ctx.send(f"カテゴリー「{name}」が見つかりません。" if name else "カテゴリー名を指定してください。")
        return
    for channel in category.channels:
        await channel.delete()
    await category.delete()
    await ctx.send(f"カテゴリー「{category.name}」とそのチャンネルを削除しました。")