async def join(ctx):
    if ctx.author.voice is None:
        await ctx.reply("ボイスチャンネルに参加してからコマンドを実行してください。")
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
        await ctx.reply(f"{voice_channel.name}に参加しました。")
    else:
        await ctx.voice_client.move_to(voice_channel)
        await ctx.reply(f"{voice_channel.name}に移動しました。")

async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.reply("ボイスチャンネルに参加していません。")
    else:
        await ctx.voice_client.disconnect()
        await ctx.reply("ボイスチャンネルから退出しました。")