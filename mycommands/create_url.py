async def geturl(ctx,day=1):
    if day >= 30:
        await ctx.send('30日を超える招待URLは発行できません')
        return
    invite = await ctx.channel.create_invite(max_age = int(day) * 24 * 3600)
    await ctx.reply(f'招待URLを発行しました。\n{invite.url}\n有効期限は{day}日です。')