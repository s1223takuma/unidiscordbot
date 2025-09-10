import discord

async def contact(ctx,*,inquiry):
    print(inquiry)
    managementrole = discord.utils.get(ctx.guild.roles, name='bots')
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        managementrole: discord.PermissionOverwrite(read_messages=True),
    }
    channel = await ctx.guild.create_text_channel(f'お問い合わせ- {ctx.author.name}', overwrites=overwrites)

    embed = discord.Embed(title="新規お問い合わせ", description=inquiry)
    await channel.send(embed=embed)
    await channel.send(f"こんにちは！\n{ctx.author.mention}さんのお問い合わせを受け付けました。{managementrole.mention}よりご連絡いたします。")